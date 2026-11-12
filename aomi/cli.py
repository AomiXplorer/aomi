"""The `aomi` command line.

Every subcommand keeps the behaviour it had in 1.0. What is new is the front
door: an installer that knows where each agent reads skills, an interactive
init, and a configuration wizard. Gate commands still exit non-zero when they
fail, so a build can depend on them.
"""
from __future__ import annotations

import argparse
import difflib
import pathlib
import sys

from . import __version__, adapters, engine, initcmd, installer, paths, ui
from . import configcmd

COMMANDS = ("install", "update", "uninstall", "init", "audit", "contrast",
            "parity", "doctor", "config", "agents")


class Parser(argparse.ArgumentParser):
    """argparse, but a typo gets a suggestion instead of a wall of usage."""

    def error(self, message: str):
        if "invalid choice" in message:
            for word in message.split("'"):
                close = difflib.get_close_matches(word, COMMANDS, n=1)
                if close and word in message:
                    self.exit(2, f"aomi: {message}\n  did you mean `aomi {close[0]}`?\n")
        self.exit(2, f"aomi: {message}\n  run `aomi --help` for the command list.\n")


def build_parser() -> Parser:
    parser = Parser(
        prog="aomi",
        description="Aomi: engineering and design gates for AI agents.",
        epilog="Examples\n"
               "  aomi install                     pick an agent, copy the skill\n"
               "  aomi install --agent cursor      same, without the questions\n"
               "  aomi init                        start a project, three questions\n"
               "  aomi audit ./src                 sweep markup and styles\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"aomi {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="<command>", parser_class=Parser)

    p = sub.add_parser("install", help="copy the skill into an agent's folder")
    p.add_argument("--agent", "-a", help="claude, opencode, cursor, windsurf, copilot, codex, agents")
    p.add_argument("--global", dest="global_scope", action="store_true", help="install for this user, not this project")
    p.add_argument("--project", dest="project_scope", action="store_true", help="install into the current project (default)")
    p.add_argument("--dir", help="install to exactly this path")
    p.add_argument("--force", action="store_true", help="replace a folder that is not an Aomi skill")
    p.add_argument("--dry-run", action="store_true", help="show what would be copied")
    p.add_argument("--yes", "-y", action="store_true", help="no questions")
    p.add_argument("--list", action="store_true", help="list adapters and exit")
    p.set_defaults(func=command_install)

    p = sub.add_parser("update", help="refresh installed copies to this version")
    p.add_argument("--agent", "-a")
    p.add_argument("--global", dest="global_scope", action="store_true", help="the user-wide path")
    p.add_argument("--project", dest="project_scope", action="store_true", help="the project path (default)")
    p.add_argument("--dir")
    p.add_argument("--yes", "-y", action="store_true")
    p.set_defaults(func=command_update)

    p = sub.add_parser("uninstall", help="remove installed copies")
    p.add_argument("--agent", "-a")
    p.add_argument("--global", dest="global_scope", action="store_true", help="the user-wide path")
    p.add_argument("--project", dest="project_scope", action="store_true", help="the project path (default)")
    p.add_argument("--dir")
    p.add_argument("--yes", "-y", action="store_true")
    p.set_defaults(func=command_uninstall)

    p = sub.add_parser("agents", help="show adapters, where they read skills, and what is detected")
    p.add_argument("--docs", action="store_true", help="include the documentation each path came from")
    p.set_defaults(func=command_agents)

    p = sub.add_parser("init", help="scaffold the aomi/ artifacts")
    p.add_argument("dir", nargs="?", default=".", help="project directory (default: .)")
    p.add_argument("--name", help="project name, used in brief.md")
    p.add_argument("--depth", help="sketch, build or product")
    p.add_argument("--no-artifacts", action="store_true", help="write nothing, just report")
    p.add_argument("--yes", "-y", action="store_true", help="no questions, safe for CI")
    p.set_defaults(func=initcmd.command)

    p = sub.add_parser("audit", help="sweep a project for the Slop Gate signals")
    p.add_argument("dir", nargs="?", default=".", help="directory to scan (default: .)")
    p.add_argument("--json", action="store_true")
    p.add_argument("--overrides", help="waiver file; defaults to <dir>/aomi/overrides.json")
    p.set_defaults(func=engine.command_audit)

    p = sub.add_parser("contrast", help="WCAG ratios for declared text pairs")
    p.add_argument("file", help="a tokens.json file")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=engine.command_contrast)

    p = sub.add_parser("parity", help="weighted feature completion from features.csv")
    p.add_argument("file", help="a features.csv file")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=engine.command_parity)

    p = sub.add_parser("doctor", help="check a skill tree: links, assets, licence, provenance")
    p.add_argument("--root", default=".", help="skill root to check (default: .)")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=engine.command_doctor)

    p = sub.add_parser("config", help="tokens, waivers and features without reading a spec")
    p.add_argument("dir", nargs="?", default=".", help="project directory (default: .)")
    p.add_argument("--show", action="store_true", help="print the active configuration")
    p.add_argument("--check", action="store_true", help="validate the files and report problems")
    p.set_defaults(func=configcmd.command)
    return parser


# --------------------------------------------------------------------------
# install, update, uninstall
# --------------------------------------------------------------------------

def _home() -> pathlib.Path:
    return pathlib.Path.home()


def _scope(args) -> str:
    if getattr(args, "global_scope", False) and getattr(args, "project_scope", False):
        raise ValueError("--global and --project cannot both be set")
    return "global" if getattr(args, "global_scope", False) else "project"


def _adapter_table(cwd: pathlib.Path, home: pathlib.Path, show_docs: bool) -> str:
    found = {adapter.key: where for adapter, where in adapters.detect(cwd, home)}
    installed = {adapter.key: path for adapter, path in installer.existing_installs(cwd, home)}
    lines = [ui.title("Aomi adapters"), ""]
    for index, adapter in enumerate(adapters.ADAPTERS, start=1):
        status = "documented" if adapter.verified else ui.warn("documented, not run here")
        marks = []
        if adapter.key in installed:
            marks.append(f"installed at {installed[adapter.key]}")
        if adapter.key in found:
            marks.append(f"detected {found[adapter.key]}")
        head = f"  [{index}] {adapter.label}"
        lines.append(f"{head.ljust(42)} {status}")
        lines.append(f"        {adapter.scope_label}")
        if adapter.note:
            lines.append(f"        {ui.dim(adapter.note)}")
        if marks:
            lines.append(f"        {ui.ok('; '.join(marks))}")
        if show_docs:
            lines.append(f"        docs {adapter.docs}")
    lines.append("")
    lines.append("  no adapter writes outside the path it prints.")
    return "\n".join(lines)


def _ask_agent(cwd: pathlib.Path, home: pathlib.Path) -> adapters.Adapter | None:
    found = {adapter.key: where for adapter, where in adapters.detect(cwd, home)}
    print(ui.title("Aomi installer"))
    print()
    if found:
        print("  detected here:")
        for adapter in adapters.ADAPTERS:
            if adapter.key in found:
                print(f"    {adapter.label}  ({found[adapter.key]})")
        print()
    print("  select your agent:")
    for index, adapter in enumerate(adapters.ADAPTERS, start=1):
        mark = "*" if adapter.key in found else " "
        print(f"    [{index}] {mark} {adapter.label}")
    print()
    answer = ui.ask("Select", "1")
    adapter = adapters.from_number(answer) or adapters.lookup(answer)
    if not adapter:
        print(ui.bad(f"  {answer!r} is not in the list"))
    return adapter


def _target_for(adapter: adapters.Adapter, args, cwd: pathlib.Path, home: pathlib.Path) -> tuple[str, pathlib.Path]:
    if getattr(args, "dir", None):
        return "custom", pathlib.Path(args.dir).expanduser().resolve()
    scope = _scope(args)
    if scope == "global" and not adapter.global_path:
        raise ValueError(f"{adapter.label} has no documented global location; use --dir")
    return scope, adapter.path_for(scope, cwd, home)


def command_install(args) -> int:
    cwd, home = pathlib.Path.cwd(), _home()
    if getattr(args, "list", False):
        print(_adapter_table(cwd, home, show_docs=True))
        return 0

    adapter = adapters.lookup(args.agent) if args.agent else None
    if args.agent and not adapter:
        print(f"install: unknown agent {args.agent!r}. Use one of:", file=sys.stderr)
        print("  " + ", ".join(a.key for a in adapters.ADAPTERS), file=sys.stderr)
        print("  or `aomi install --list` to see where each one reads skills.", file=sys.stderr)
        return 2

    if not adapter and args.dir:
        adapter = adapters.for_directory(pathlib.Path(args.dir).expanduser())

    if not adapter:
        if not (ui.is_interactive() and not args.yes):
            print("install: no --agent given and no terminal to ask on.", file=sys.stderr)
            print("  try `aomi install --agent claude` or `aomi install --list`.", file=sys.stderr)
            return 2
        adapter = _ask_agent(cwd, home)
        if not adapter:
            return 2

    try:
        scope, target = _target_for(adapter, args, cwd, home)
    except ValueError as exc:
        print(f"install: {exc}", file=sys.stderr)
        return 2

    print(installer.render_plan(adapter, target, scope))
    if not getattr(args, "dry_run", False) and ui.is_interactive() and not args.yes:
        if not ui.confirm("Copy the skill there", True):
            print("  cancelled, nothing written")
            return 0

    report = installer.install(adapter, target, dry_run=getattr(args, "dry_run", False),
                               force=getattr(args, "force", False))
    print()
    print(installer.render_result(report))
    if report["action"] == "refused":
        return 2
    if report["problems"]:
        return 1
    if report["action"] != "dry-run":
        if scope == "project":
            instruction = f"open {adapter.label} in {cwd}"
        elif scope == "global":
            instruction = f"restart {adapter.label}"
        else:
            instruction = f"point {adapter.label} at that folder"
        print()
        print(f"  {instruction} and ask it to use aomi.")
        print("  the `aomi` command stays on your PATH; `aomi update` refreshes this copy.")
    return 0


def command_update(args) -> int:
    cwd, home = pathlib.Path.cwd(), _home()
    if args.dir:
        targets = [("custom", pathlib.Path(args.dir).expanduser().resolve())]
    elif args.agent:
        adapter = adapters.lookup(args.agent)
        if not adapter:
            print(f"update: unknown agent {args.agent!r}", file=sys.stderr)
            return 2
        targets = [(adapter.label, adapter.path_for(_scope(args), cwd, home))]
    else:
        targets = [(adapter.label, path) for adapter, path in installer.existing_installs(cwd, home)]

    if not targets:
        print("update: no installed copy found here.", file=sys.stderr)
        print("  run `aomi install` first, or name the folder with `aomi update --dir PATH`.", file=sys.stderr)
        return 2

    code = 0
    print(ui.title("Aomi update"))
    for label, target in targets:
        print()
        print(f"  {label}: {target}")
        if not installer.is_aomi_skill(target):
            print(ui.bad("  not an Aomi skill, skipped"))
            code = code or 2
            continue
        report = installer.install(_adapter_or_none(label), target, force=True)
        print(installer.render_result(report))
        if report["problems"]:
            code = 1
    return code


def _adapter_or_none(label: str) -> adapters.Adapter:
    for adapter in adapters.ADAPTERS:
        if adapter.label == label:
            return adapter
    return adapters.BY_KEY["agents"]


def command_uninstall(args) -> int:
    cwd, home = pathlib.Path.cwd(), _home()
    if args.dir:
        targets = [("custom", pathlib.Path(args.dir).expanduser().resolve())]
    elif args.agent:
        adapter = adapters.lookup(args.agent)
        if not adapter:
            print(f"uninstall: unknown agent {args.agent!r}", file=sys.stderr)
            return 2
        targets = [(adapter.label, adapter.path_for(_scope(args), cwd, home))]
    else:
        targets = [(adapter.label, path) for adapter, path in installer.existing_installs(cwd, home)]

    if not targets:
        print("uninstall: no installed copy found here.", file=sys.stderr)
        print("  nothing to remove.", file=sys.stderr)
        return 0

    print(ui.title("Aomi uninstall"))
    for label, target in targets:
        print(f"  {label}: {target}")
    if ui.is_interactive() and not args.yes:
        if not ui.confirm("Remove the folders above", False):
            print("  cancelled, nothing removed")
            return 0

    code = 0
    for label, target in targets:
        report = installer.uninstall(target)
        print(installer.render_result(report))
        if report["action"] == "refused":
            code = 2
    return code


def command_agents(args) -> int:
    cwd, home = pathlib.Path.cwd(), _home()
    print(_adapter_table(cwd, home, show_docs=getattr(args, "docs", False)))
    return 0


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    argv = list(sys.argv[1:] if argv is None else argv)
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        print(f"{ui.title('aomi')} {__version__}: engineering and design gates for AI agents.")
        print()
        print("  aomi install      copy the skill into your agent")
        print("  aomi init         start a project")
        print("  aomi audit ./src  sweep a project")
        print()
        print("  aomi --help for every command, docs/cli.md for the details.")
        return 0
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\nstopped", file=sys.stderr)
        return 130
    except FileNotFoundError as exc:
        print(f"aomi: {exc}", file=sys.stderr)
        print("  if this is a fresh install, reinstall: pipx install --force git+https://github.com/AomiXplorer/aomi.git",
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
