#!/bin/bash
# Sync the Obsidian vault → Quartz site → GitHub.
# Run this whenever you've added new info in Obsidian and want it live.
#
# Usage:  ./sync.sh "optional commit message"
# If no message is given, defaults to "Sync from vault".

set -e

VAULT="/Users/fnunitishmichael/Library/Mobile Documents/iCloud~md~obsidian/Documents/aarits vault/world history"
SITE_DIR="$(cd "$(dirname "$0")" && pwd)"
MSG="${1:-Sync from vault}"

cd "$SITE_DIR"

echo "▸ Syncing vault → content/"
# rsync mirrors the vault into content/, deleting files removed from the vault.
# --exclude protects the index page that lives only in the site, not the vault.
rsync -a --delete \
  --exclude '.obsidian' \
  --exclude '.trash' \
  --exclude '.DS_Store' \
  --exclude 'index.md' \
  "$VAULT/" content/

if git diff --quiet content/ && git diff --cached --quiet content/; then
  echo "▸ No changes to push. You're already in sync."
  exit 0
fi

echo "▸ Committing"
git add content/
git commit -m "$MSG"

echo "▸ Pushing to GitHub"
git push

echo ""
echo "✓ Done. Live site will rebuild in ~1 minute."
echo "  https://aarit-s.github.io/ap-world-history-vault/"
