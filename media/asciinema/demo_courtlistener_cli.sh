#!/usr/bin/env bash
set -euo pipefail

# Demo script for courtlistener-cli
export TERM=xterm-256color
export NO_COLOR=1
export PAGER=cat
export GIT_PAGER=cat
export COLUMNS=96
export LINES=28

run() {
  local cmd="$1"
  printf '\n\033[1;36m$ %s\033[0m\n' "$cmd"
  sleep 0.8
  bash -lc "$cmd"
  sleep 1.2
}

slide() {
  clear
  printf '\033[1;32mSlide: %s\033[0m\n' "$1"
  printf '%s\n' "$2"
  sleep 2.0
}

# Load local API credentials without printing secrets.
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

# Avoid inheriting the Hermes runtime venv. Use this project's .venv only.
deactivate 2>/dev/null || true
unset VIRTUAL_ENV

# 1. Installation
slide "Installing CourtListener CLI" "Sync dependencies, install the editable CLI package, then activate the project virtualenv."
run "git pull --ff-only origin main"
run "uv sync"
run "uv pip install -e ."
source .venv/bin/activate

# 2. CLI Surface & Data Retrieval
slide "Version Check" "Verify the direct command is available after activation."
run "courtlistener-cli --version"

slide "Querying Courts Data" "Default flow: fetch a small courts sample using the standard cache/output behavior."
run "courtlistener-cli courts list --limit 3"

slide "Printing Results to Screen" "Use --screen to print JSON results directly in the terminal, useful for inspection and demos."
run "courtlistener-cli --screen courts list --limit 3"

slide "Bypassing Cache for Fresh API Data" "Use --no-cache together with --screen to force a fresh API request and display the returned data."
run "courtlistener-cli --no-cache --screen courts list --limit 3"

slide "Retrieving Attorney Records" "Compare the regular output flow with direct screen output for PACER attorney records."
run "courtlistener-cli attorneys list --limit 3"
run "courtlistener-cli --screen attorneys list --limit 3"

slide "Accessing Financial Disclosures" "Retrieve a small sample of federal judicial financial disclosure records."
run "courtlistener-cli financial list --limit 3"

slide "Browsing Data Tags" "List user-created tags linked to dockets."
run "courtlistener-cli tags list --limit 5"

# 3. Documentation & Modules
slide "Documentation & Modules" "Show the command modules and the project documentation entry point."
run "ls -F src/commands/"
run "cat README.md | head -n 15"

printf '\n\033[1;32mDemo complete.\033[0m\n'
