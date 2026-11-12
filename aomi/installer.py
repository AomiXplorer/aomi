"""Copy the skill into an agent's folder, update it, remove it, and check it.

The installer copies the runtime tree and nothing else. No manifest is written:
an installed skill is recognised by its own SKILL.md, so `update` and
`uninstall` work after an upgrade, from any working directory, without state.
"""
from __future__ import annotations

import pathlib
import re
import shutil

from . import paths, ui
from .adapters import Adapter

LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
REQUIRED = (
    "SKILL.md",
    "core/workflow.md",
    "core/depth.md",
    "core/philosophy.md",
    "design/slop-gate.md",
    "design/accessibility.md",
    "engineering/recon.md",
    "templates/brief.md",
    "references/palettes.md",
    "docs/provenance.md",
    "LICENSE",
)


def is_aomi_skill(path: pathlib.Path) -> bool:
    """True when this folder is an Aomi install, not an unrelated skill folder.

    A hand edit can damage SKILL.md, so the rest of the tree counts too: an
    install that has been tampered with should be repairable by `aomi update`,
    not mistaken for someone else's skill.
    """
    skill = path / "SKILL.md"
    if skill.is_file():
        head = skill.read_text(errors="ignore")[:800]
        if re.search(r"^name:\s*aomi\s*$", head, re.M):
            return True
    markers = (path / "core" / "philosophy.md", path / "design" / "slop-gate.md")
    if all(marker.is_file() for marker in markers):
        return True
    licence = path / "LICENSE"
    return licence.is_file() and "AOMI PERSONAL USE LICENSE" in licence.read_text(errors="ignore")[:2000]


def existing_installs(cwd: pathlib.Path, home: pathlib.Path) -> list[tuple[Adapter, pathlib.Path]]:
    """Every Aomi skill folder already installed for the adapters we know."""
    found: list[tuple[Adapter, pathlib.Path]] = []
    for adapter in _adapters():
        for scope in ("project", "global"):
            try:
                target = adapter.path_for(scope, cwd, home)
            except ValueError:
                continue
            if is_aomi_skill(target) and (adapter, target) not in found:
                found.append((adapter, target))
    return found


def _adapters():
    from .adapters import ADAPTERS
    return ADAPTERS


def broken_links(root: pathlib.Path) -> list[str]:
    """Every relative markdown link inside the installed tree that does not resolve."""
    problems: list[str] = []
    for page in sorted(root.rglob("*.md")):
        if any(part in paths.EXCLUDED for part in page.relative_to(root).parts):
            continue
        for target in LINK.findall(page.read_text(errors="ignore")):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            clean = target.split("#")[0].strip()
            if clean and not (page.parent / clean).exists():
                problems.append(f"{page.relative_to(root)} -> {clean}")
    return problems


def verify(root: pathlib.Path) -> list[str]:
    """What is wrong with this install. Empty means usable."""
    problems = [f"missing {name}" for name in REQUIRED if not (root / name).is_file()]
    if not (root / "SKILL.md").is_file():
        return problems
    head = (root / "SKILL.md").read_text(errors="ignore")[:800]
    if not head.startswith("---"):
        problems.append("SKILL.md has no frontmatter block")
    else:
        for name in ("name:", "description:"):
            if name not in head:
                problems.append(f"SKILL.md frontmatter has no {name.rstrip(':')}")
    problems += [f"broken link {item}" for item in broken_links(root)]
    return problems


def install(adapter: Adapter, target: pathlib.Path, dry_run: bool = False,
            force: bool = False) -> dict:
    """Copy the payload into `target`. Returns a report; the caller renders it."""
    files = [(rel, src) for rel, src in paths.payload_files()]
    size = sum(src.stat().st_size for _, src in files)
    existed = target.exists()
    ours = is_aomi_skill(target)
    report = {"action": "install", "target": str(target), "files": 0, "bytes": size,
              "removed": 0, "problems": [], "existed": existed, "dry_run": dry_run}

    if existed and not ours and any(target.iterdir()):
        if not force:
            report["action"] = "refused"
            report["problems"].append(
                f"{target} exists and is not an Aomi skill; rerun with --force to replace it"
            )
            return report

    if dry_run:
        report["action"] = "dry-run"
        report["files"] = len(files)
        return report

    target.mkdir(parents=True, exist_ok=True)
    for rel, src in files:
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        shutil.copymode(src, dest)
        if dest.suffix == ".sh":
            # a wheel does not carry the mode bit, so set it here instead
            dest.chmod(dest.stat().st_mode | 0o111)

    # prune files this version no longer ships, inside the folders we manage
    keep = {rel for rel, _ in files}
    managed = {rel.split("/")[0] for rel in keep} | set(paths.PAYLOAD_DIRS)
    for path in sorted(target.rglob("*"), reverse=True):
        if not path.is_file():
            continue
        rel = path.relative_to(target).as_posix()
        if rel in keep:
            continue
        if rel.split("/")[0] in managed:
            path.unlink()
            report["removed"] += 1

    report["files"] = len(files)
    report["problems"] = verify(target)
    report["action"] = "updated" if existed else "installed"
    return report


def uninstall(target: pathlib.Path) -> dict:
    if not target.exists():
        return {"action": "absent", "target": str(target), "files": 0}
    if not is_aomi_skill(target):
        return {"action": "refused", "target": str(target), "files": 0,
                "problems": [f"{target} is not an Aomi skill; not touching it"]}
    count = sum(1 for path in target.rglob("*") if path.is_file())
    shutil.rmtree(target)
    # remove the parent skill folder if this was its only skill
    parent = target.parent
    try:
        if parent.name == "skills" and not any(parent.iterdir()):
            parent.rmdir()
    except OSError:
        pass
    return {"action": "removed", "target": str(target), "files": count}


def render_plan(adapter: Adapter, target: pathlib.Path, scope: str) -> str:
    count, size = paths.payload_size()
    lines = [
        ui.title("Aomi install"),
        "",
        ui.field("agent", adapter.label),
        ui.field("scope", scope),
        ui.field("target", str(target)),
        ui.field("files", f"{count} ({size // 1024} KB)"),
    ]
    if is_aomi_skill(target):
        lines.append(ui.field("existing", "yes, this will update it in place"))
    elif target.exists() and any(target.iterdir()):
        lines.append(ui.field("existing", "a folder that is not Aomi"))
    if not adapter.verified:
        lines.append(ui.warn(f"  note: {adapter.note}"))
    return "\n".join(lines)


def render_result(report: dict) -> str:
    action = report["action"]
    if action == "dry-run":
        return f"  would copy {report['files']} files to {report['target']}"
    if action == "refused":
        return "\n".join([ui.bad("  refused: " + report["problems"][0])])
    if action == "absent":
        return "  nothing installed at that path"
    if action == "removed":
        return f"  removed {report['files']} files from {report['target']}"
    lines = [f"  {ui.ok(action)}: {report['files']} files at {report['target']}"]
    if report.get("removed"):
        lines.append(f"  pruned {report['removed']} file(s) this version no longer ships")
    if report["problems"]:
        lines.append(ui.bad(f"  {len(report['problems'])} problem(s) after copying:"))
        lines += [f"    - {problem}" for problem in report["problems"][:8]]
    else:
        lines.append("  verified: required files present, every relative link resolves")
    return "\n".join(lines)
