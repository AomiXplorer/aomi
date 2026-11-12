"""Packaging only: the skill tree is copied into the wheel here.

The repository keeps SKILL.md next to core/, design/ and the rest, because that
is what an agent reads when the folder is used straight from a checkout. A wheel
cannot carry files from outside the package, so this build step copies the same
tree into `aomi/skilldata/`. Nothing is duplicated in git and there is no second
copy to keep in sync.
"""
from __future__ import annotations

import importlib.util
import pathlib
import shutil

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py

# The payload list lives in aomi/paths.py so the installer and the wheel cannot
# disagree about what an install contains. Imported by path because setup.py runs
# before the package is importable.
_ROOT = pathlib.Path(__file__).resolve().parent
_SPEC = importlib.util.spec_from_file_location("_aomi_paths", _ROOT / "aomi" / "paths.py")
_paths = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_paths)

PAYLOAD_FILES = _paths.PAYLOAD_FILES
PAYLOAD_DIRS = _paths.PAYLOAD_DIRS
SKIP = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")


class build_py(_build_py):
    def run(self):
        super().run()
        root = _ROOT
        dest = pathlib.Path(self.build_lib) / "aomi" / "skilldata"
        dest.mkdir(parents=True, exist_ok=True)
        for name in PAYLOAD_FILES:
            source = root / name
            if source.is_file():
                (dest / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, dest / name)
        for name in PAYLOAD_DIRS:
            source = root / name
            if source.is_dir():
                shutil.copytree(source, dest / name, ignore=SKIP, dirs_exist_ok=True)


setup(cmdclass={"build_py": build_py})
