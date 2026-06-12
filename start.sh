#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate

if [ ! -f .venv/.requirements-installed ] || ! cmp -s requirements.txt .venv/.requirements-installed; then
  python -m pip install -r requirements.txt
  cp requirements.txt .venv/.requirements-installed
fi

exec python bot.py
