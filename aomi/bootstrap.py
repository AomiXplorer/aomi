"""Install Aomi from a checkout, with nothing but Python.

pipx is the tidy route when it is installed. This is the route when it is not:
clone, then `python3 install.py`. No pip, no virtualenv, no root, no network.

It does two separate jobs, because they are separate:

* the *command*: puts the package in a data folder and a small launcher in
  `~/.local/bin`, so `aomi` keeps working from any directory;
* the *skill*: copies the runtime files into the folder an agent reads, which is
  the part an agent actually loads.

Running it again updates in place. `--uninstall` removes the command again.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import shutil
import subprocess
import sys

from . import __version__, adapters, installer, paths, ui

LAUNCHER_LINES = """#!/bin/sh
# The aomi command, written by install.py. Rerun that to update it.
PY="${AOMI_PYTHON:-%(python)s}"
PYTHONPATH="%(app)s${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONPATH
exec "$PY" -m aomi "$@"
"""
MARKER = "written by install.py"


# --------------------------------------------------------------------------
# where things go
# --------------------------------------------------------------------------

def data_home(env: dict | None = None) -> pathlib.Path:
    env = os.environ if env is None else env
    if env.get("XDG_DATA_HOME"):
        return pathlib.Path(env["XDG_DATA_HOME"]).expanduser()
    return pathlib.Path(env.get("HOME", "~")).expanduser() / ".local" / "share"


def default_app_dir(env: dict | None = None) -> pathlib.Path:
    return data_home(env) / "aomi"


def default_bin_dir(env: dict | None = None) -> pathlib.Path:
    return pathlib.Path((os.environ if env is None else env).get("HOME", "~")).expanduser() / ".local" / "bin"


def install_files() -> list[tuple[str, pathlib.Path]]:
    """The skill payload plus the package itself: what the command needs to run."""
    files = list(paths.payload_files())
    for source in sorted(paths.PACKAGE.glob("*.py")):
        files.append((f"aomi/{source.name}", source))
    return files


def launcher_text(app: pathlib.Path, python: str) -> str:
    return LAUNCHER_LINES % {"python": python, "app": app}


def path_advice(bin_dir: pathlib.Path, env: dict | None = None) -> tuple[str, str]:
    """The line that puts `bin_dir` on PATH, and the file it belongs in."""
    env = os.environ if env is None else env
    shell = pathlib.Path(env.get("SHELL", "")).name
    if shell == "fish":
        return f"fish_add_path {bin_dir}", "~/.config/fish/config.fish"
    if shell == "zsh":
        return f'export PATH="{bin_dir}:$PATH"', "~/.zshrc"
    return f'export PATH="{bin_dir}:$PATH"', "~/.profile"


def on_path(bin_dir: pathlib.Path, env: dict | None = None) -> bool:
    env = os.environ if env is None else env
    wanted = bin_dir.expanduser().resolve()
    for part in env.get("PATH", "").split(os.pathsep):
        if part and pathlib.Path(part).expanduser().resolve() == wanted:
            return True
    return False


# --------------------------------------------------------------------------
# the command
# --------------------------------------------------------------------------

def install_command(app: pathlib.Path, bin_dir: pathlib.Path, python: str | None = None,
                    dry_run: bool = False) -> dict:
    python = python or sys.executable or "python3"
    files = install_files()
    launcher = bin_dir / "aomi"
    report = {"action": "dry-run" if dry_run else "installed", "files": len(files),
              "app": app, "launcher": launcher, "python": python, "problems": []}

    if dry_run:
        return report

    app.mkdir(parents=True, exist_ok=True)
    # a build left a bundled copy behind in some checkouts; it would shadow the
    # real payload, so it never travels with the command
    stale = app / "aomi" / "skilldata"
    if stale.is_dir():
        shutil.rmtree(stale)

    for rel, source in files:
        dest = app / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
        shutil.copymode(source, dest)
        if dest.suffix == ".sh":
            dest.chmod(dest.stat().st_mode | 0o111)

    bin_dir.mkdir(parents=True, exist_ok=True)
    launcher.write_text(launcher_text(app, python))
    launcher.chmod(0o755)

    check = subprocess.run([str(launcher), "--version"], capture_output=True, text=True)
    if check.returncode != 0:
        report["problems"].append(f"the launcher did not run: {(check.stderr or check.stdout).strip()}")
    else:
        report["version"] = check.stdout.strip()
    return report


def uninstall_command(app: pathlib.Path, bin_dir: pathlib.Path, dry_run: bool = False) -> dict:
    launcher = bin_dir / "aomi"
    removed = []
    if launcher.is_file() and MARKER in launcher.read_text(errors="replace"):
        removed.append(str(launcher))
        if not dry_run:
            launcher.unlink()
    if app.is_dir():
        removed.append(str(app))
        if not dry_run:
            shutil.rmtree(app)
    return {"action": "dry-run" if dry_run else "removed", "removed": removed, "problems": []}


def render_command_result(report: dict) -> str:
    if report["action"] == "dry-run":
        return (f"  would copy {report['files']} files to {report['app']}\n"
                f"  would write {report['launcher']}")
    files = str(report["files"]) + " files"
    lines = [ui.field("installed", files),
             ui.field("command", str(report["launcher"])),
             ui.field("files at", str(report["app"]))]
    if report.get("version"):
        lines.append(ui.field("checked", report["version"]))
    for problem in report["problems"]:
        lines.append(ui.bad(problem))
    return "\n".join("  " + line for line in lines)


# --------------------------------------------------------------------------
# the menu
# --------------------------------------------------------------------------

def _ask_mode() -> str:
    print(ui.title(f"Aomi {__version__}"))
    print()
    print("  what should this do?")
    print("    [1]  set up the `aomi` command      no pip, no root")
    print("    [2]  copy the skill into an agent   the files your agent reads")
    print("    [3]  both")
    print()
    answer = ui.ask("Select", "3")
    return {"1": "command", "2": "skill", "3": "both"}.get(answer.strip(), "both")


def _force_scope(args) -> str | None:
    if args.directory:
        return None
    if args.global_scope:
        return "global"
    if args.project_scope:
        return "project"
    return None


def _skill_target(adapter: adapters.Adapter, args, cwd: pathlib.Path) -> tuple[str, pathlib.Path]:
    if args.directory:
        return "custom", pathlib.Path(args.directory).expanduser().resolve()
    scope = _force_scope(args) or "project"
    if scope == "global" and not adapter.global_path:
        raise ValueError(f"{adapter.label} has no documented global location; use --dir")
    return scope, adapter.path_for(scope, cwd, pathlib.Path.home())


def _install_skill(args, cwd: pathlib.Path) -> int:
    adapter = adapters.lookup(args.agent) if args.agent else None
    if args.agent and not adapter:
        print(f"install.py: unknown agent {args.agent!r}.", file=sys.stderr)
        print("  one of: " + ", ".join(a.key for a in adapters.ADAPTERS), file=sys.stderr)
        return 2
    if not adapter and args.directory:
        adapter = adapters.for_directory(pathlib.Path(args.directory).expanduser())
    if not adapter:
        if not (ui.is_interactive() and not args.yes):
            print("install.py: which agent? pass --agent, or run this in a terminal.", file=sys.stderr)
            print("  aomi install --list shows the names.", file=sys.stderr)
            return 2
        found = {a.key: where for a, where in adapters.detect(cwd, pathlib.Path.home())}
        print()
        print("  select your agent:")
        for index, candidate in enumerate(adapters.ADAPTERS, start=1):
            mark = "*" if candidate.key in found else " "
            print(f"    [{index}] {mark} {candidate.label}")
        print()
        adapter = adapters.from_number(ui.ask("Select", "1"))
        if not adapter:
            print(ui.bad("  not in the list"))
            return 2

    try:
        scope, target = _skill_target(adapter, args, cwd)
    except ValueError as exc:
        print(f"install.py: {exc}", file=sys.stderr)
        return 2

    print()
    print(installer.render_plan(adapter, target, scope))
    if ui.is_interactive() and not args.yes:
        if not ui.confirm("Copy the skill there", True):
            print("  cancelled, nothing written")
            return 0
    report = installer.install(adapter, target, dry_run=args.dry_run, force=args.force)
    print()
    print(installer.render_result(report))
    if report["action"] == "refused":
        return 2
    return 1 if report["problems"] else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="install.py",
        description="Install Aomi from this checkout. No pip, no root.",
        epilog="Examples\n"
               "  python3 install.py                       menu, then do what you pick\n"
               "  python3 install.py --yes                 the command only, no questions\n"
               "  python3 install.py --yes --skill --agent cursor\n"
               "  python3 install.py --uninstall --yes\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"aomi {__version__}")
    parser.add_argument("--command", dest="do_command", action="store_true", help="set up the aomi command")
    parser.add_argument("--skill", dest="do_skill", action="store_true", help="copy the skill into an agent")
    parser.add_argument("--agent", "-a", help="claude, opencode, cursor, windsurf, copilot, codex, agents")
    parser.add_argument("--dir", dest="directory", help="copy the skill to exactly this path")
    parser.add_argument("--global", dest="global_scope", action="store_true", help="the user-wide agent folder")
    parser.add_argument("--project", dest="project_scope", action="store_true", help="the project agent folder (default)")
    parser.add_argument("--app-dir", help=argparse.SUPPRESS)
    parser.add_argument("--bin-dir", help=argparse.SUPPRESS)
    parser.add_argument("--force", action="store_true", help="replace a folder that is not an Aomi skill")
    parser.add_argument("--dry-run", action="store_true", help="show what would happen")
    parser.add_argument("--uninstall", action="store_true", help="remove the command again")
    parser.add_argument("--yes", "-y", action="store_true", help="no questions")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(sys.argv[1:] if argv is None else argv)
    cwd = pathlib.Path.cwd()
    app = pathlib.Path(args.app_dir).expanduser() if args.app_dir else default_app_dir()
    bin_dir = pathlib.Path(args.bin_dir).expanduser() if args.bin_dir else default_bin_dir()

    if args.uninstall:
        report = uninstall_command(app, bin_dir, dry_run=args.dry_run)
        print(ui.title("Aomi uninstall"))
        if not report["removed"]:
            print("  nothing installed by install.py here")
            return 0
        for item in report["removed"]:
            print(f"  removed {item}")
        return 0

    if args.do_command or args.do_skill:
        mode = "both" if (args.do_command and args.do_skill) else ("command" if args.do_command else "skill")
    elif args.yes:
        mode = "command"          # --yes alone cannot guess an agent, so it does the safe half
    elif ui.is_interactive():
        mode = _ask_mode()
    else:
        print("install.py: no terminal to ask on.", file=sys.stderr)
        print("  use --command, or --skill --agent NAME, or --yes for the command alone.", file=sys.stderr)
        return 2

    code = 0
    if mode in ("command", "both"):
        print(ui.title("Aomi command"))
        report = install_command(app, bin_dir, dry_run=args.dry_run)
        print()
        print(render_command_result(report))
        if report["problems"]:
            code = 1
        if report["action"] != "dry-run" and not on_path(bin_dir):
            line, rc = path_advice(bin_dir)
            print()
            print(ui.warn(f"  {bin_dir} is not on PATH. add it once:"))
            print(f"    echo '{line}' >> {rc}")
            print("  then open a new terminal, or call it by full path.")

    if mode in ("skill", "both"):
        skill_code = _install_skill(args, cwd)
        code = code or skill_code

    return code


if __name__ == "__main__":
    sys.exit(main())
