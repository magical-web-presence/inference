#!/usr/bin/env bash
# Restart helper for the inference app. Intended to be run on the remote mac
# from a git post-receive hook or manual invocation.

# Path assumptions: run from the working tree root (e.g. ~/Desktop/inference)
PIDFILE=/tmp/inference.pid
VENV_DIR=.venv
LOGFILE=app.log

echo "[restart] $(date)" >> "$LOGFILE"

# try to stop existing process if running
if [ -f "$PIDFILE" ]; then
  OLDPID=$(cat "$PIDFILE" 2>/dev/null || true)
  if [ -n "$OLDPID" ]; then
    if kill -0 "$OLDPID" 2>/dev/null; then
      echo "[restart] stopping pid $OLDPID" >> "$LOGFILE"
      kill "$OLDPID" || true
      sleep 1
    fi
  fi
fi

# Activate venv if present
if [ -x "$VENV_DIR/bin/python" ]; then
  PY="$VENV_DIR/bin/python"
else
  PY=python3
fi

# run in background with nohup, detach and write pidfile
nohup "$PY" src/main.py >> "$LOGFILE" 2>&1 &
NEWPID=$!
echo $NEWPID > "$PIDFILE"
echo "[restart] started pid $NEWPID" >> "$LOGFILE"

echo "[restart] done"
