"""Terminal output that stays readable in Termux, in a plain pipe and in CI.

Colour is opt in through a real terminal and never required to read a message.
No emoji, no spinner, no cursor movement: a line is printed once and stays.
"""
from __future__ import annotations

import os
import sys

_CODES = {"bold": "1", "dim": "2", "red": "31", "green": "32", "yellow": "33",
          "blue": "34", "magenta": "35", "cyan": "36"}


def _isatty(stream) -> bool:
    try:
        return bool(stream.isatty())
    except Exception:
        return False


def supports_color(stream=None) -> bool:
    stream = stream if stream is not None else sys.stdout
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    if os.environ.get("CLICOLOR") == "0":
        return False
    if os.environ.get("TERM") in {"dumb", ""}:
        return False
    return _isatty(stream)


def paint(text: str, colour: str, stream=None) -> str:
    if not text or not supports_color(stream):
        return text
    code = _CODES.get(colour)
    return f"\033[{code}m{text}\033[0m" if code else text


def bold(text: str, stream=None) -> str:
    return paint(text, "bold", stream)


def dim(text: str, stream=None) -> str:
    return paint(text, "dim", stream)


def ok(text: str) -> str:
    return paint(text, "green")


def warn(text: str) -> str:
    return paint(text, "yellow")


def bad(text: str) -> str:
    return paint(text, "red")


def title(text: str) -> str:
    return bold(text)


def field(label: str, value: str, width: int = 16) -> str:
    """One aligned key/value line. Width is small enough for an 80 column term."""
    return f"  {label.ljust(width)}{value}"


def bullet(text: str, indent: int = 2) -> str:
    return f"{' ' * indent}- {text}"


def ask(prompt: str, default: str = "") -> str:
    """Read a line, survive a closed stdin, and never echo an empty answer."""
    suffix = f" [{default}]" if default else ""
    try:
        answer = input(f"{prompt}{suffix}: ").strip()
    except EOFError:
        return default
    return answer or default


def confirm(prompt: str, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    answer = ask(f"{prompt} ({hint})", "").lower()
    if not answer:
        return default
    return answer in {"y", "yes", "ya", "true", "1"}


def is_interactive() -> bool:
    """True only when a person is there to answer."""
    if os.environ.get("AOMI_NONINTERACTIVE"):
        return False
    return _isatty(sys.stdin) and _isatty(sys.stdout)
