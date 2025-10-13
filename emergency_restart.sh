# /usr/local/bin/emergency_restart.sh
#!/usr/bin/env bash
set -euo pipefail

LOG="/var/log/emergency_restart.log"
REPO_DIR="/root/taj-homepage"
SERVICE_NAME="taj"
VENV_DIR="${REPO_DIR}/venv"
GIT_REMOTE="origin"
GIT_BRANCH="main"
TIMESTAMP() { date "+%Y-%m-%d %H:%M:%S"; }

echo
echo "=== emergency_restart started at $(TIMESTAMP) ===" | tee -a "$LOG"
echo "Working dir: $REPO_DIR" | tee -a "$LOG"

# must run as root or with sudo
if [ "$EUID" -ne 0 ]; then
  echo "$(TIMESTAMP) ERROR: This script should be run as root (or via sudo)." | tee -a "$LOG"
  exit 1
fi

# safe checks
if [ ! -d "$REPO_DIR" ]; then
  echo "$(TIMESTAMP) ERROR: repo dir $REPO_DIR does not exist." | tee -a "$LOG"
  exit 1
fi

cd "$REPO_DIR"

# create a small lock so the script can't run concurrently
LOCK="/tmp/emergency_restart.lock"
if [ -e "$LOCK" ]; then
  echo "$(TIMESTAMP) ERROR: lock $LOCK exists. Another run may be in progress." | tee -a "$LOG"
  exit 1
fi
trap 'rm -f "$LOCK"; echo "$(TIMESTAMP) emergency_restart aborted" | tee -a "$LOG"' EXIT
touch "$LOCK"

# Record current HEAD
OLD_HEAD=$(git rev-parse --verify HEAD)
echo "$(TIMESTAMP) Current HEAD: $OLD_HEAD" | tee -a "$LOG"

# 1) Stop the service cleanly
echo "$(TIMESTAMP) Stopping service: $SERVICE_NAME" | tee -a "$LOG"
systemctl stop "$SERVICE_NAME" || true
sleep 1

# 2) Stash local changes (if any) and remember stash id
STASHED=0
if ! git diff --quiet || ! git ls-files --others --exclude-standard --quiet; then
  echo "$(TIMESTAMP) Local changes detected. Stashing..." | tee -a "$LOG"
  git stash push -u -m "emergency_restart_stash_$(date +%s)" >/dev/null 2>&1 || true
  STASHED=1
  echo "$(TIMESTAMP) Stashed local changes." | tee -a "$LOG"
else
  echo "$(TIMESTAMP) No local changes to stash." | tee -a "$LOG"
fi

# 3) Pull latest code from remote (the requested 'git pull origin main' is here)
echo "$(TIMESTAMP) Pulling latest from ${GIT_REMOTE}/${GIT_BRANCH}" | tee -a "$LOG"
set +e
GIT_PULL_OUTPUT=$(git pull "${GIT_REMOTE}" "${GIT_BRANCH}" 2>&1)
GIT_PULL_EXIT=$?
set -e
echo "$GIT_PULL_OUTPUT" | tee -a "$LOG"

if [ $GIT_PULL_EXIT -ne 0 ]; then
  echo "$(TIMESTAMP) ERROR: git pull failed (exit ${GIT_PULL_EXIT}). Trying to abort and restore." | tee -a "$LOG"
  # try to reapply the original HEAD (safe fallback)
  git reset --hard "$OLD_HEAD" || true
  if [ "$STASHED" -eq 1 ]; then
    echo "$(TIMESTAMP) Restoring stash (pop)..." | tee -a "$LOG"
    git stash pop || echo "$(TIMESTAMP) stash pop had conflicts; please resolve manually" | tee -a "$LOG"
  fi
  echo "$(TIMESTAMP) emergency_restart failed during git pull." | tee -a "$LOG"
  exit 2
fi

# 4) (optional) install new/updated requirements
if [ -f "requirements.txt" ]; then
  echo "$(TIMESTAMP) Installing requirements (if any) into venv: $VENV_DIR" | tee -a "$LOG"
  if [ -x "${VENV_DIR}/bin/pip" ]; then
    "${VENV_DIR}/bin/pip" install -r requirements.txt 2>&1 | tee -a "$LOG" || {
      echo "$(TIMESTAMP) WARNING: pip install failed, continuing to restart service." | tee -a "$LOG"
    }
  else
    echo "$(TIMESTAMP) WARNING: venv pip not found at ${VENV_DIR}/bin/pip — skipping pip install" | tee -a "$LOG"
  fi
else
  echo "$(TIMESTAMP) No requirements.txt found; skipping pip install." | tee -a "$LOG"
fi

# 5) Reload systemd (in case service file changed), restart taj
echo "$(TIMESTAMP) Reloading systemd & restarting service: $SERVICE_NAME" | tee -a "$LOG"
systemctl daemon-reload
systemctl restart "$SERVICE_NAME"
sleep 1
systemctl status "$SERVICE_NAME" --no-pager -l | tee -a "$LOG"

# 6) Reload nginx to pick up config changes (if any)
echo "$(TIMESTAMP) Testing nginx config and reloading" | tee -a "$LOG"
if nginx -t 2>&1 | tee -a "$LOG"; then
  systemctl reload nginx
else
  echo "$(TIMESTAMP) nginx config test failed; not reloading. Check /var/log/nginx/error.log" | tee -a "$LOG"
fi

# 7) Try to reapply stash (if we stashed earlier)
if [ "$STASHED" -eq 1 ]; then
  echo "$(TIMESTAMP) Attempting to pop previously stashed changes" | tee -a "$LOG"
  set +e
  git stash pop 2>&1 | tee -a "$LOG"
  PST=$?
  set -e
  if [ $PST -ne 0 ]; then
    echo "$(TIMESTAMP) Warning: stash pop returned ${PST}. Manual resolution may be required." | tee -a "$LOG"
  else
    echo "$(TIMESTAMP) Stash reapplied." | tee -a "$LOG"
  fi
fi

echo "$(TIMESTAMP) emergency_restart finished" | tee -a "$LOG"
rm -f "$LOCK"
trap - EXIT
