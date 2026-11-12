#!/usr/bin/env bash
# Wrapper so a skill runner can call Aomi's CLI with one string of arguments.
# Usage: run_skill("aomi", "audit ./src")  /  run_skill("aomi", "init .")
set -euo pipefail
mapfile -t ARGS < <(python3 -c 'import shlex,sys
for a in shlex.split(sys.argv[1]): print(a)' "${*:-}")

if command -v aomi >/dev/null 2>&1; then
  exec aomi "${ARGS[@]}"
fi
# No installed command: use the checkout this wrapper sits in, if there is one.
here="$(cd "$(dirname "$0")/.." && pwd)"
if [ -f "$here/aomi/cli.py" ]; then
  exec python3 -m aomi "${ARGS[@]}"
fi
echo "aomi: no aomi command on PATH and no package beside this wrapper." >&2
echo "  install it with: pipx install git+https://github.com/AomiXplorer/aomi.git" >&2
exit 2
