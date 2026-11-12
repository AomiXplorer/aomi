#!/usr/bin/env python3
"""Install Aomi from this checkout: python3 install.py

No pip, no virtualenv, no root. It sets up the `aomi` command and can copy the
skill into an agent's folder. See docs/installation.md for the long version.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from aomi.bootstrap import main  # noqa: E402  (after the path is set)

if __name__ == "__main__":
    sys.exit(main())
