#!/usr/bin/env python3
import json, os, sqlite3, csv, sys

DB = "taj_menu.db"
PLAN_FILE = "image_update_plan.json"

def main(apply=False):
    with open(PLAN_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    plan = data.get("plan", [])
    # plan entries are [item_id, "/static/images/..", "static/images/.."]
    to_apply = []
    missing = []

    for item_id, db_path, rel in plan:
        # prefer the filesystem relative path (third element)
        filesystem_path = rel
        if not os.path.isabs(filesystem_path):
            filesystem_path = os.path.normpath(filesystem_path)
        if os.path.exists(filesystem_path):
            to_apply.append((item_id, db_path, filesystem_path))
        else:
            # try alternative: change ext to .webp if the plan points to avif/png/jpg
            base, ext = os.path.splitext(filesystem_path)
            alt = base + ".webp"
            if os.path.exists(alt):
                print(f"will use alt: {alt} for id {item_id}")
                to_apply.append((item_id, "/"+alt.replace("\\","/"), alt))
            else:
                missing.append((item_id, db_path, filesystem_path, alt if os.path.exists(alt) else None))

    print(f"Found {len(to_apply)} files present, {len(missing)} missing")

    # write missing to CSV for manual review
    with open("skipped_missing_files.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["item_id","db_path","requested_fs_path","alt_webp_exists"])
        for r in missing:
            w.writerow(r)

    if not apply:
        print("Dry run. To apply run: APPLY=1 python3 apply_plan_safe.py")
        for item_id, db_path, fs in to_apply[:20]:
            print(f"Would update id {item_id} -> {db_path}")
        return

    # Apply updates
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    for item_id, db_path, fs in to_apply:
        cur.execute("UPDATE menu_items SET image_url=?, updated_at = CURRENT_TIMESTAMP WHERE id=?", (db_path, item_id))
    conn.commit()
    conn.close()
    print("Applied", len(to_apply), "updates. See skipped_missing_files.csv for missing ones.")

if __name__ == "__main__":
    apply_flag = os.environ.get("APPLY","0") in ("1","true","True")
    main(apply=apply_flag)
