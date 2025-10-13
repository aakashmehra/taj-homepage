#!/usr/bin/env python3
"""
update_image_urls.py
- Scans static/images for .webp files
- Attempts to match file -> menu_items by normalized basename 
- Prints SQL update plan and writes CSVs for ambiguous / no match
- To actually apply updates set environment APPLY=True
"""

import os
import sqlite3
import re
import json
from pathlib import Path
from collections import defaultdict
import sys
import csv
import hashlib
import os

DB_PATH = "taj_menu.db"         # set to your DB path if different
IMAGES_ROOT = "static/images"   # root where images live
ALLOWED_EXTS = {".webp", ".png", ".jpg", ".jpeg", ".avif"}  # we only care about converted webp but include others

def norm(s: str) -> str:
    # Normalize string for filename matching
    if not s:
        return ""
    s = s.lower()
    s = s.replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", " ", s)   # replace non-alnum with space
    s = re.sub(r"\s+", " ", s).strip()
    return s

def file_candidates(root):
    files = []
    for p in Path(root).rglob("*"):
        if p.is_file() and p.suffix.lower() in ALLOWED_EXTS:
            files.append(p)
    return files

def build_db_index(conn):
    # create a simple mapping from normalized name -> list of rows (id, name_en)
    cur = conn.cursor()
    cur.execute("SELECT id, name_en, image_url FROM menu_items")
    by_name = defaultdict(list)
    rows = cur.fetchall()
    for r in rows:
        _id, name_en, image_url = r
        key = norm(name_en)
        by_name[key].append({"id": _id, "name_en": name_en, "image_url": image_url})
    return by_name, rows

def guess_matches(fname_norm, by_name):
    # exact match
    if fname_norm in by_name:
        return by_name[fname_norm]
    # try contained matches
    candidates = []
    for n, rows in by_name.items():
        if fname_norm in n or n in fname_norm:
            candidates.extend(rows)
    # dedupe by id
    ids = {}
    for c in candidates:
        ids[c["id"]] = c
    return list(ids.values())

def main(apply=False):
    conn = sqlite3.connect(DB_PATH)
    by_name, all_rows = build_db_index(conn)

    files = file_candidates(IMAGES_ROOT)
    plan = []
    ambiguous = []
    no_match = []
    mapped = {}

    for p in files:
        # prefer webp files if both jpg and webp exist
        if p.suffix.lower() != ".webp":
            # skip non-webp unless there's no webp sibling
            webp = p.with_suffix(".webp")
            if webp.exists():
                continue

        rel = os.path.relpath(p, ".")  # e.g. static/images/...
        basename = p.stem   # filename without extension
        fname_norm = norm(basename)

        matches = guess_matches(fname_norm, by_name)

        if len(matches) == 1:
            row = matches[0]
            # prefer starting slash in DB
            db_path = "/" + rel.replace("\\", "/")
            plan.append((row['id'], db_path, rel))
            mapped[rel] = row['id']
        elif len(matches) > 1:
            ambiguous.append({"file": rel, "candidates": matches})
        else:
            # fallback: try matching by exact filename contained in existing image_url
            found = False
            for r in all_rows:
                rid, name_en, imgurl = r
                if imgurl:
                    if basename in imgurl:
                        db_path = "/" + rel.replace("\\", "/")
                        plan.append((rid, db_path, rel))
                        mapped[rel] = rid
                        found = True
                        break
            if not found:
                no_match.append(rel)

    # present plan summary
    print("=== PLAN SUMMARY ===")
    print(f"Files scanned: {len(files)}")
    print(f"To update: {len(plan)}")
    print(f"Ambiguous: {len(ambiguous)}")
    print(f"No match: {len(no_match)}")
    print()

    if plan:
        print("Sample SQL updates (first 20):")
        for item_id, db_path, rel in plan[:20]:
            print(f"UPDATE menu_items SET image_url = '{db_path}', updated_at = CURRENT_TIMESTAMP WHERE id = {item_id};  -- {rel}")

    # write csvs for manual review
    with open("image_update_plan.json", "w") as fh:
        json.dump({"plan": plan, "ambiguous": ambiguous, "no_match": no_match}, fh, indent=2)

    with open("ambiguous.csv", "w", newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(["file", "candidate_ids", "candidate_names"])
        for a in ambiguous:
            w.writerow([a["file"], ";".join(str(c["id"]) for c in a["candidates"]), ";".join(c["name_en"] for c in a["candidates"])])

    with open("no_match.csv", "w", newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(["file"])
        for nm in no_match:
            w.writerow([nm])

    if apply:
        print("\nApplying updates to DB...")
        cur = conn.cursor()
        for item_id, db_path, rel in plan:
            cur.execute("UPDATE menu_items SET image_url = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (db_path, item_id))
        conn.commit()
        print("Applied", len(plan), "updates.")
    else:
        print("\nDry-run only. No DB changes applied.")
        print("To apply, run: APPLY=True python3 update_image_urls.py")

    conn.close()

if __name__ == "__main__":
    apply_flag = os.environ.get("APPLY", "False").lower() in ("1","true","yes")
    main(apply=apply_flag)
