#!/usr/bin/env bash
set -euo pipefail

# Demo script for courtlistener-cli
export TERM=xterm-256color
export NO_COLOR=1
export PAGER=cat
export GIT_PAGER=cat
export COLUMNS=96
export LINES=28

# Suppress uv virtual environment warnings
export UV_PROJECT_ENVIRONMENT=.venv

run() {
  local cmd="$1"
  printf '\n\033[1;36m$ %s\033[0m\n' "$cmd"
  sleep 0.8
  # Execute in a subshell with a clean environment
  bash -lc "export COURTLISTENER_API_TOKEN=$(grep COURTLISTENER_API_TOKEN .env | cut -d '=' -f2) && $cmd"
  sleep 1.2
}

# 1. Installation
clear
printf '\033[1;32mSlide: Installing CourtListener CLI\033[0m\n'
sleep 2.0
run "git clone https://github.com/miguelfg/courtlistener-cli"
cd courtlistener-cli
# Use --active to use the project's own venv without conflicting with Hermes' venv
run "uv sync --active"
run "uv pip install -e . --active"
source .venv/bin/activate

# 2. CLI Surface & Data Retrieval
clear
printf '\033[1;32mSlide: Version Check\033[0m\n'
run "courtlistener-cli --version"

clear
printf '\033[1;32mSlide: Querying Courts Data\033[0m\n'
run "courtlistener-cli courts list --limit 3"

clear
printf '\033[1;32mSlide: Retrieving Attorney Records\033[0m\n'
run "courtlistener-cli attorneys list --limit 3"

clear
printf '\033[1;32mSlide: Accessing Financial Disclosures\033[0m\n'
run "courtlistener-cli financial list --limit 3"

clear
printf '\033[1;32mSlide: Browsing Data Tags\033[0m\n'
run "courtlistener-cli tags list --limit 5"

# 3. Documentation & Modules
clear
printf '\033[1;32mSlide: Documentation & Modules\033[0m\n'
run "ls -F src/commands/"
run "cat README.md | head -n 15"

printf '\n\033[1;32mDemo complete.\033[0m\n'
