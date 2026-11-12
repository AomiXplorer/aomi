"""`python3 -m aomi ...` works from a checkout with no install step."""
import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
