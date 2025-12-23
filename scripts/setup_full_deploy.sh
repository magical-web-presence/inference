#!/usr/bin/env bash
set -euo pipefail
# Full local helper to create GitHub repo, commit, push, and set up remote autodeploy.
# Requires:
# - gh authenticated locally (for GitHub creation)
# - ssh key setup to macuser@192.168.1.151
# - git installed

REMOTE_USER_HOST="macuser@192.168.1.151"
BARE_REPO_PATH="~/git/inference.git"
WORK_TREE_PATH="~/Desktop/inference"
REPO_NAME="inference"

echo "1) Ensure .gitignore contains excludes for models and virtualenv"
cat .gitignore || true

if [ ! -d .git ]; then
  echo "2) Initializing git"
  git init
else
  echo "2) Git already initialized"
fi

# Ensure there is at least one commit (gh requires an existing commit to push)
if git rev-parse --verify HEAD >/dev/null 2>&1; then
  echo "Repository has commits."
else
  echo "No commits found; creating initial commit."
  # ensure git identity is set for this repo (set locally if not present)
  if ! git config user.name >/dev/null || [ -z "$(git config user.name || true)" ]; then
    GIT_NAME=${GIT_USER_NAME:-"Auto Deploy"}
    git config user.name "$GIT_NAME"
    echo "Set local git user.name=$GIT_NAME"
  fi
  if ! git config user.email >/dev/null || [ -z "$(git config user.email || true)" ]; then
    GIT_EMAIL=${GIT_USER_EMAIL:-"deploy@local"}
    git config user.email "$GIT_EMAIL"
    echo "Set local git user.email=$GIT_EMAIL"
  fi

  git add .
  git commit -m "Initial import"
fi

echo "3) Create GitHub repo and push using gh"
./scripts/create_github_repo.sh

echo "4) Create bare repo and post-receive hook on remote"
./scripts/setup_remote.sh

echo "5) Add mac remote locally and push to it"
if git remote | grep -q '^mac$'; then
  echo "Remote 'mac' already present"
else
  git remote add mac ${REMOTE_USER_HOST}:~/git/inference.git
fi

echo "Pushing to mac (this will trigger the post-receive hook and auto-deploy)"
git push mac main

echo "Deploy complete. Check remote logs at ~/Desktop/inference/deploy_hook.log or ~/Desktop/inference/app.log"
