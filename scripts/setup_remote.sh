#!/usr/bin/env bash
set -euo pipefail
# Run this locally; it will execute commands on the Mac via SSH and
# create a bare repo and the post-receive hook that checks out the working
# tree into ~/Desktop/inference and runs the restart script.

REMOTE_USER_HOST="macuser@192.168.1.151"
BARE_REPO_DIR="~/git/inference.git"
WORK_TREE_DIR="~/Desktop/inference"

echo "Creating bare repo on remote: $REMOTE_USER_HOST:$BARE_REPO_DIR"
ssh "$REMOTE_USER_HOST" "mkdir -p $BARE_REPO_DIR && cd $BARE_REPO_DIR && git init --bare"

echo "Creating working tree and cloning if needed"
ssh "$REMOTE_USER_HOST" "mkdir -p $WORK_TREE_DIR && if [ ! -d \"$WORK_TREE_DIR/.git\" ]; then git clone $BARE_REPO_DIR $WORK_TREE_DIR; fi"

echo "Installing post-receive hook"
ssh "$REMOTE_USER_HOST" 'cat > ~/git/inference.git/hooks/post-receive <<'"'"'HOOK'"'"'
#!/bin/sh
# Post-receive hook: checkout into the working dir and restart the app
GIT_WORK_TREE="$HOME/Desktop/inference" git checkout -f
cd "$HOME/Desktop/inference" || exit 0
chmod +x ./scripts/restart.sh || true
./scripts/restart.sh >> ./deploy_hook.log 2>&1 || true
HOOK

ssh "$REMOTE_USER_HOST" "chmod +x ~/git/inference.git/hooks/post-receive"

echo "Remote setup complete. Push to the remote bare repo to deploy."
echo "Example: git remote add mac ${REMOTE_USER_HOST}:~/git/inference.git && git push mac main"
