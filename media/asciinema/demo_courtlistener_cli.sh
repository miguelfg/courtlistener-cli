#!/usr/bin/env bash
set -euo pipefail

# Demo script for courtlistener-cli.
# It clones into a disposable temp workspace so the source repo stays clean.
export TERM=xterm-256color
export NO_COLOR=1
export PAGER=cat
export GIT_PAGER=cat
export COLUMNS=96
export LINES=28

SOURCE_REPO="${SOURCE_REPO:-https://github.com/miguelfg/courtlistener-cli}"
DEMO_WORKDIR="${DEMO_WORKDIR:-$(mktemp -d /tmp/courtlistener-cli-demo.XXXXXX)}"
PROJECT_DIR="$DEMO_WORKDIR/courtlistener-cli"
ORIGINAL_DIR="$(pwd)"

cleanup() {
  # Keep temp workspace for debugging only when explicitly requested.
  if [ "${KEEP_DEMO_WORKDIR:-0}" != "1" ]; then
    rm -rf "$DEMO_WORKDIR"
  fi
}
trap cleanup EXIT

run() {
  local cmd="$1"
  printf '\n\033[1;36m$ %s\033[0m\n' "$cmd"
  sleep 1.0
  bash -lc "$cmd"
  sleep 2.5
}

page_run() {
  local cmd="$1"
  printf '\n\033[1;36m$ %s | less\033[0m\n' "$cmd"
  sleep 1.0
  python3 - "$cmd" <<'PY'
import os
import pty
import select
import sys
import time

cmd = sys.argv[1] + " | less -R -S -X"
pid, fd = pty.fork()
if pid == 0:
    os.execlp("bash", "bash", "-lc", cmd)

def drain(timeout=0.2):
    end = time.time() + timeout
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.05)
        if not r:
            continue
        try:
            data = os.read(fd, 4096)
        except OSError:
            return False
        if not data:
            return False
        os.write(1, data)
    return True

try:
    for _ in range(8):
        if not drain(0.25):
            break
    for _ in range(14):
        os.write(fd, b"j")
        time.sleep(0.55)
        if not drain(0.2):
            break
    time.sleep(0.8)
    drain(0.5)
    os.write(fd, b"q")
    for _ in range(10):
        if not drain(0.15):
            break
except OSError:
    pass
try:
    os.waitpid(pid, 0)
except ChildProcessError:
    pass
PY
  sleep 2.5
}

slide() {
  clear
  printf '\033[1;32m# %s\033[0m\n' "$1"
  printf '%s\n' "$2"
  sleep 3.0
}

# Load local API credentials from the source checkout without printing secrets.
if [ -f "$ORIGINAL_DIR/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$ORIGINAL_DIR/.env"
  set +a
fi

# Avoid inheriting the Hermes runtime venv. Use this project's .venv only.
deactivate 2>/dev/null || true
unset VIRTUAL_ENV

# 1. Installation
slide "Installing CourtListener CLI" "Clone into a temporary workspace, copy local credentials, sync dependencies, install editable CLI, and activate the project virtualenv."
run "mkdir -p '$DEMO_WORKDIR'"
run "git clone '$SOURCE_REPO' '$PROJECT_DIR'"
if [ -f "$ORIGINAL_DIR/.env" ]; then
  cp "$ORIGINAL_DIR/.env" "$PROJECT_DIR/.env"
fi
cd "$PROJECT_DIR"
run "uv sync"
run "uv pip install -e ."
source .venv/bin/activate

# 2. CLI Surface & Data Retrieval
slide "Version Check" "Verify the direct command is available after activation."
run "courtlistener-cli --version"

slide "CSV Export With Cached Output" "Run a larger query that saves results to a CSV file using the default cache/output flow."
run "courtlistener-cli courts list --limit 100 --format csv"

slide "Print JSON Results to Screen" "Use --screen for a compact three-record preview, pipe it to less, and scroll slowly."
page_run "courtlistener-cli --screen courts list --limit 3"

slide "Fresh API Request Without Cache" "Use --no-cache with --screen to bypass local caching and inspect fresh API data."
page_run "courtlistener-cli --no-cache --screen courts list --limit 3"

slide "Attorney Records: Export vs Screen" "Save a larger attorneys result set as CSV, then preview three records directly in the terminal."
run "courtlistener-cli attorneys list --limit 100 --format csv"
page_run "courtlistener-cli --screen attorneys list --limit 3"

slide "Financial Disclosures CSV Export" "Save a larger financial disclosures sample to CSV for downstream analysis."
run "courtlistener-cli financial list --limit 100 --format csv"

slide "Tags CSV Export" "Save tags linked to dockets using the same CSV export flow."
run "courtlistener-cli tags list --limit 100 --format csv"

# 3. Command Overview
slide "Command Overview" "Finish with the CLI's own help output to show the available command groups."
run "courtlistener-cli --help | head -n 35"

printf '\n\033[1;32mDemo complete.\033[0m\n'
