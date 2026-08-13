#!/usr/bin/env bash
# Deploys config/ into $HOME, mirroring its directory structure.
# Existing files that differ from the repo's copy are backed up first.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_DIR="$REPO_ROOT/config"
BACKUP_DIR="$HOME/.config-backup/$(date +%Y%m%d-%H%M%S)"

if [ ! -d "$CONFIG_DIR" ]; then
  echo "No config/ directory found at $CONFIG_DIR" >&2
  exit 1
fi

dry_run=false
if [ "${1:-}" = "--dry-run" ]; then
  dry_run=true
fi

backed_up=false
while IFS= read -r -d '' src; do
  rel="${src#"$CONFIG_DIR"/}"
  dest="$HOME/$rel"

  if $dry_run; then
    echo "would install: config/$rel -> $dest"
    continue
  fi

  mkdir -p "$(dirname "$dest")"

  if [ -e "$dest" ] && ! cmp -s "$src" "$dest"; then
    mkdir -p "$(dirname "$BACKUP_DIR/$rel")"
    cp -p "$dest" "$BACKUP_DIR/$rel"
    backed_up=true
    echo "backed up: $dest -> $BACKUP_DIR/$rel"
  fi

  cp -p "$src" "$dest"
  echo "installed: config/$rel -> $dest"
done < <(find "$CONFIG_DIR" -type f -print0)

if $backed_up; then
  echo
  echo "Existing files that differed were backed up to: $BACKUP_DIR"
fi
