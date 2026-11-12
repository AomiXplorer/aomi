#!/usr/bin/env python3
"""Kept for anyone who has `python3 scripts/aomi.py ...` in a script.

The command line moved into the `aomi` package in 1.1. Both of these work:

    aomi <command>              after `pipx install`
    python3 -m aomi <command>   from a checkout, no install
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

try:
    from aomi.cli import main
except ModuleNotFoundError:  # an installed skill folder has no package beside it
    sys.exit(
        "aomi: this copy of scripts/aomi.py has no Python package beside it.\n"
        "  install the command line with:\n"
        "    pipx install git+https://github.com/AomiXplorer/aomi.git"
    )

if __name__ == "__main__":
    sys.exit(main())
