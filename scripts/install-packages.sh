#!/usr/bin/env bash
# Installs the packages/tools documented in docs/ENVIRONMENT.org.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# --- 1. System-Level Packages (Pacman) ---
PACMAN_PACKAGES=(
  base
  base-devel
  curl
  emacs
  git
  less
  nano
  openssh
  sudo
  tree
  vim
  wget
)

echo "==> Installing pacman packages: ${PACMAN_PACKAGES[*]}"
# -Syu (not just -Sy) to avoid partial upgrades, which Arch does not support.
# --needed skips packages that are already up to date. Left interactive
# (no --noconfirm) since this can perform a full system upgrade.
sudo pacman -Syu --needed "${PACMAN_PACKAGES[@]}"

# --- 2 & 3. Development Tools / Node.js via NVM ---
NVM_VERSION="v0.40.5"
NODE_VERSION="24.16.0"

export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"

if [ -s "$NVM_DIR/nvm.sh" ]; then
  echo "==> nvm already installed at $NVM_DIR, skipping install"
else
  echo "==> Installing nvm $NVM_VERSION"
  curl -o- "https://raw.githubusercontent.com/nvm-sh/nvm/${NVM_VERSION}/install.sh" | bash
fi

# shellcheck disable=SC1091
\. "$NVM_DIR/nvm.sh"

echo "==> Installing Node.js v${NODE_VERSION} via nvm and setting it as default"
nvm install "$NODE_VERSION"
nvm alias default "$NODE_VERSION"
nvm use default

# --- 4. Global NPM Packages ---
NPM_GLOBAL_PACKAGES=(
  @anthropic-ai/claude-code
  corepack
)

echo "==> Installing global npm packages: ${NPM_GLOBAL_PACKAGES[*]}"
npm install -g "${NPM_GLOBAL_PACKAGES[@]}"

echo
echo "==> Manual step required"
echo "'antigravity' (agy) must be installed manually — it's a manual binary"
echo "install with no package manager or curl script. See docs/ENVIRONMENT.org"
echo "section 2 for details."

echo
echo "Done. See ${REPO_ROOT}/docs/ENVIRONMENT.org for the full reference report."
