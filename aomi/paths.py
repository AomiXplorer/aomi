"""Where the skill files live, in a checkout and in an installed wheel.

Two situations have to work:

* a git checkout, where SKILL.md sits at the repository root next to `aomi/`;
* an installed wheel, where the skill tree was copied into `aomi/skilldata/`
  at build time.

Everything that needs a skill file asks this module, so neither case leaks into
the commands.
"""
from __future__ import annotations

import pathlib

PACKAGE = pathlib.Path(__file__).resolve().parent
REPO = PACKAGE.parent
_BUNDLED = PACKAGE / "skilldata"

# What an install copies. Directories keep their relative structure; everything
# else (tests, build tooling, the packaging files) stays in the repository.
PAYLOAD_FILES = ("SKILL.md", "LICENSE", "README.md", "scripts/run.sh")
PAYLOAD_DIRS = ("core", "engineering", "design", "references", "templates", "docs", "assets")
# Never copied, whatever else is in the tree.
EXCLUDED = {".git", ".github", "tests", "build", "dist", "__pycache__", ".venv", "node_modules"}


def skill_root() -> pathlib.Path:
    """The directory holding SKILL.md, whichever case this is."""
    if (_BUNDLED / "SKILL.md").is_file():
        return _BUNDLED
    if (REPO / "SKILL.md").is_file():
        return REPO
    raise FileNotFoundError(
        "cannot find the skill files: no SKILL.md beside the package and none bundled. "
        "Reinstall with `pipx install --force git+https://github.com/AomiXplorer/aomi.git`."
    )


def templates_dir() -> pathlib.Path:
    return skill_root() / "templates"


def payload_files():
    """Yield (relative path, absolute path) for every file an install copies."""
    root = skill_root()
    for name in PAYLOAD_FILES:
        path = root / name
        if path.is_file():
            yield name, path
    for name in PAYLOAD_DIRS:
        directory = root / name
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(root)
            if any(part in EXCLUDED for part in rel.parts):
                continue
            if path.suffix == ".pyc":
                continue
            yield str(rel), path


def payload_size() -> tuple[int, int]:
    """(file count, total bytes) for a dry run."""
    files = list(payload_files())
    return len(files), sum(path.stat().st_size for _, path in files)
