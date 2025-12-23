#!/usr/bin/env bash
set -euo pipefail
# Create GitHub repository using `gh` and push the current repo.
# Requires: logged into `gh` (run `gh auth login` locally first).

REPO_NAME="inference"
VISIBILITY="public" # or private

if ! command -v gh >/dev/null 2>&1; then
  echo "Error: gh CLI not found. Install from https://cli.github.com/ and run 'gh auth login'"
  exit 2
fi

CURRENT_DIR=$(pwd)

echo "Creating GitHub repo: $REPO_NAME"
gh repo create "$REPO_NAME" --$VISIBILITY --source="$CURRENT_DIR" --remote=origin --push --confirm

echo "GitHub repo created and pushed to origin."
