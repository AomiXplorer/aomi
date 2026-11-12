"""`aomi init`: create only the artifacts this depth actually uses."""
from __future__ import annotations

import pathlib
import re

from . import paths, ui

# The full set. `product` needs all of it; `build` needs the four that get read;
# `sketch` needs none, because a one-component fix does not earn a paper trail.
ALL = ("brief.md", "map.md", "decisions.md", "proof.md", "handoff.md", "features.csv")
BY_DEPTH = {
    "sketch": (),
    "build": ("brief.md", "decisions.md", "proof.md", "features.csv"),
    "product": ALL,
}
# What `aomi init --yes` writes when no depth is given, matching 1.0 behaviour.
DEFAULT_SET = ("brief.md", "decisions.md", "proof.md", "handoff.md", "features.csv")

DEPTH_BLURB = {
    "sketch": "one question, one component, one fix. No artifacts.",
    "build": "one feature, one page, one flow.",
    "product": "several surfaces, real users, someone else maintaining it.",
}


def personalise(text: str, name: str, depth: str) -> str:
    """Put the project name and the chosen depth into the brief, nothing else."""
    text = re.sub(r"^# Brief\b.*$", f"# Brief: {name}", text, count=1, flags=re.M)
    text = re.sub(r"<!--\s*sketch \| build \| product.*?-->",
                  f"Depth: **{depth}** ({DEPTH_BLURB[depth]}) See `core/depth.md`.",
                  text, count=1, flags=re.S)
    return text


def write_artifacts(top: pathlib.Path, names, name: str, depth: str) -> tuple[list[str], list[str]]:
    created, kept = [], []
    if not names:
        return created, kept
    target = top / "aomi"
    target.mkdir(parents=True, exist_ok=True)
    for filename in names:
        dest = target / filename
        if dest.exists():
            kept.append(filename)
            continue
        template = paths.templates_dir() / filename
        body = template.read_text() if template.is_file() else ""
        if filename == "brief.md":
            body = personalise(body, name, depth)
        dest.write_text(body)
        created.append(filename)
    return created, kept


def parse_depth(value: str | None, default: str = "build") -> str:
    if not value:
        return default
    value = value.strip().lower()
    if value in BY_DEPTH:
        return value
    if value in {"1", "s", "small"}:
        return "sketch"
    if value in {"2", "b"}:
        return "build"
    if value in {"3", "p", "full"}:
        return "product"
    raise ValueError(f"unknown depth {value!r}; use sketch, build or product")


def choose_interactively(top: pathlib.Path) -> tuple[str, str, bool]:
    """Ask three questions. Returns (name, depth, write_now)."""
    print(ui.title("Aomi project setup"))
    print()
    print(ui.field("directory", str(top)))
    default_name = top.name if top.name not in {"", ".", ".."} else "my-project"
    name = ui.ask("Project name", default_name)

    print()
    print("  depth:")
    for index, (key, blurb) in enumerate(DEPTH_BLURB.items(), start=1):
        print(f"    [{index}] {key.ljust(8)} {blurb}")
    answer = ui.ask("Select depth", "2")
    depth = parse_depth({"1": "sketch", "2": "build", "3": "product"}.get(answer, answer))

    count = len(BY_DEPTH[depth])
    if count == 0:
        print()
        print("  sketch writes no artifacts. Start with core/depth.md and go.")
        return name, depth, False
    print()
    return name, depth, ui.confirm(f"Write {count} artifact files into aomi/", True)


def command(args) -> int:
    top = pathlib.Path(getattr(args, "dir", ".") or ".").resolve()
    if not top.exists():
        print(f"init: {top} does not exist", file=__import__("sys").stderr)
        return 2
    if not top.is_dir():
        print(f"init: {top} is a file, not a directory", file=__import__("sys").stderr)
        return 2

    yes = bool(getattr(args, "yes", False))
    depth_arg = getattr(args, "depth", None)
    name_arg = getattr(args, "name", None)

    try:
        depth = parse_depth(depth_arg, default="build" if depth_arg else "")
    except ValueError as exc:
        print(f"init: {exc}", file=__import__("sys").stderr)
        return 2

    interactive = not yes and ui.is_interactive() and not name_arg
    if interactive:
        name, depth, write_now = choose_interactively(top)
        names = BY_DEPTH[depth] if write_now else ()
    else:
        name = name_arg or (top.name if top.name not in {"", ".", ".."} else "my-project")
        names = BY_DEPTH[depth] if depth else DEFAULT_SET
        if getattr(args, "no_artifacts", False):
            names = ()

    created, kept = write_artifacts(top, names, name, depth or "build")

    print()
    if not names:
        print(f"  {ui.ok('nothing to write')} for depth {depth or 'build'}")
    elif created:
        print(f"  {ui.ok('created')} aomi/{', aomi/'.join(created)}")
    if kept:
        print(f"  kept (already there) aomi/{', aomi/'.join(kept)}")
    print()
    print(f"  next: fill aomi/brief.md, then work the phases in core/workflow.md")
    return 0
