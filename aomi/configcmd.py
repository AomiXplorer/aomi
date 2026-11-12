"""`aomi config`: the three files a project may need, without reading a spec.

None of this is required. The audit works with no configuration at all; this is
for the projects that have a brand colour, a waiver with a reason, or a feature
contract to score.
"""
from __future__ import annotations

import csv
import io
import json
import pathlib
import sys

from . import engine, ui

HEX_HELP = "a hex colour like #1C1A17"

REASONS = ("brand", "content", "accessibility", "hardware", "legacy")
REASON_BLURB = {
    "brand": "the colour is the product's own identity",
    "content": "the product is about this: art, fashion, a game",
    "accessibility": "a requirement forces it, such as contrast or colour blindness",
    "hardware": "a device or platform constraint",
    "legacy": "existing material that cannot change yet",
}


def config_dir(top: pathlib.Path) -> pathlib.Path:
    return top / "aomi"


def paths_for(top: pathlib.Path) -> dict[str, pathlib.Path]:
    base = config_dir(top)
    return {
        "overrides": base / "overrides.json",
        "tokens": base / "tokens.json",
        "features": base / "features.csv",
    }


def _read_json(path: pathlib.Path, fallback):
    if not path.is_file():
        return fallback
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return fallback


# --------------------------------------------------------------------------
# show and check
# --------------------------------------------------------------------------

def render_show(top: pathlib.Path) -> str:
    places = paths_for(top)
    lines = [ui.title("Aomi configuration"), "", ui.field("project", str(top)), ""]
    for key, label in (("overrides", "overrides.json"), ("tokens", "tokens.json"),
                       ("features", "features.csv")):
        path = places[key]
        state = "present" if path.is_file() else "not present"
        lines.append(ui.field(label, state))
        if key == "overrides" and path.is_file():
            raw = _read_json(path, [])
            entries = raw if isinstance(raw, list) else raw.get("overrides", [])
            for entry in entries:
                lines.append(f"      {entry.get('signal', '?')} waived: {entry.get('reason', '?')}")
        if key == "tokens" and path.is_file():
            doc = _read_json(path, {})
            pairs = len(doc.get("pairs", []) or [])
            roles = [k for k in doc if k not in {"pairs", "meta", "$schema"}]
            lines.append(f"      {len(roles)} colour roles, {pairs} checked pairs")
        if key == "features" and path.is_file():
            rows = list(csv.DictReader(path.read_text().splitlines()))
            musts = sum(1 for r in rows if (r.get("priority") or "").lower() == "must")
            lines.append(f"      {len(rows)} features, {musts} must")
    lines.append("")
    lines.append("  nothing here is required. A project with no configuration still audits.")
    return "\n".join(lines)


def check(top: pathlib.Path) -> tuple[int, list[str]]:
    """Return (exit code, lines). Problems are stated with the fix."""
    places = paths_for(top)
    lines, problems = [], 0
    lines.append(ui.title("Aomi configuration check"))
    lines.append("")

    if places["overrides"].is_file():
        raw = _read_json(places["overrides"], None)
        if raw is None:
            lines.append(ui.bad("  overrides.json: not valid JSON"))
            problems += 1
        else:
            entries = raw if isinstance(raw, list) else raw.get("overrides", [])
            for entry in entries if isinstance(entries, list) else []:
                sid = str(entry.get("signal", "")).upper()
                reason = str(entry.get("reason", "")).lower()
                if sid not in engine.SIGNALS:
                    lines.append(ui.bad(f"  overrides.json: {sid or '(no signal)'} is not a signal"))
                    problems += 1
                elif reason not in engine.ALLOWED_REASONS:
                    lines.append(ui.bad(f"  overrides.json: {sid} reason {reason!r} is not allowed"))
                    problems += 1
                else:
                    lines.append(ui.ok(f"  overrides.json: {sid} waived ({reason})"))

    if places["tokens"].is_file():
        doc = _read_json(places["tokens"], None)
        if doc is None:
            lines.append(ui.bad("  tokens.json: not valid JSON"))
            problems += 1
        else:
            tokens = {k: v for k, v in doc.items() if k not in {"pairs", "meta", "$schema"}}
            try:
                pairs = engine.collect_pairs(doc)
            except (ValueError, KeyError) as exc:
                lines.append(ui.bad(f"  tokens.json: {exc}"))
                problems += 1
                pairs = []
            for pair in pairs:
                try:
                    fg = engine.resolve(str(pair["fg"]), tokens)
                    bg = engine.resolve(str(pair["bg"]), tokens)
                except (KeyError, ValueError):
                    lines.append(ui.bad(f"  tokens.json: {pair.get('fg')} does not resolve to a colour"))
                    problems += 1
                    continue
                need = engine.THRESHOLDS.get(str(pair.get("kind", "body")).lower(), 4.5)
                ratio = engine.contrast(fg, bg)
                if ratio >= need:
                    lines.append(ui.ok(f"  tokens.json: {pair.get('label', 'pair')} {ratio}:1"))
                else:
                    lines.append(ui.bad(f"  tokens.json: {pair.get('label', 'pair')} {ratio}:1, needs {need}"))
                    problems += 1

    if places["features"].is_file():
        text = places["features"].read_text()
        rows = list(csv.DictReader(io.StringIO(text)))
        header = (text.splitlines() or [""])[0].lower()
        if "area,feature,priority" not in header.replace(" ", ""):
            lines.append(ui.bad("  features.csv: header must start area,feature,priority"))
            problems += 1
        else:
            lines.append(ui.ok(f"  features.csv: {len(rows)} rows"))
        for row in rows:
            if (row.get("priority") or "").lower() not in engine.PRIORITY_WEIGHT:
                lines.append(ui.warn(f"  features.csv: {row.get('feature')} has priority "
                                     f"{(row.get('priority') or '').strip()!r}, it will be skipped"))
            if (row.get("clone") or "").lower() not in engine.CLONE_VALUE:
                lines.append(ui.warn(f"  features.csv: {row.get('feature')} has clone "
                                     f"{(row.get('clone') or '').strip()!r}, it will be skipped"))

    if len(lines) <= 2:
        lines.append("  no configuration files. That is a valid setup.")
    lines.append("")
    lines.append(ui.ok(f"  {problems} problem(s)") if not problems else ui.bad(f"  {problems} problem(s)"))
    return (1 if problems else 0), lines


# --------------------------------------------------------------------------
# writers
# --------------------------------------------------------------------------

def write_tokens(top: pathlib.Path, ground: str, ink: str, brand: str) -> dict:
    on_brand = "#FFFFFF" if engine.contrast("#FFFFFF", brand) >= 4.5 else "#111111"
    doc = {
        "ground": ground,
        "ink": ink,
        "brand": brand,
        "brand-on": on_brand,
        "pairs": [
            {"fg": "ink", "bg": "ground", "kind": "body", "label": "body on ground"},
            {"fg": "brand", "bg": "ground", "kind": "large", "label": "brand on ground"},
            {"fg": "brand-on", "bg": "brand", "kind": "large", "label": "on brand"},
        ],
    }
    target = paths_for(top)["tokens"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(doc, indent=2) + "\n")
    return doc


def add_override(top: pathlib.Path, signal: str, reason: str, note: str) -> pathlib.Path:
    target = paths_for(top)["overrides"]
    target.parent.mkdir(parents=True, exist_ok=True)
    raw = _read_json(target, [])
    entries = raw if isinstance(raw, list) else raw.get("overrides", [])
    entries = [e for e in entries if str(e.get("signal", "")).upper() != signal.upper()]
    entries.append({"signal": signal.upper(), "reason": reason.lower(), "note": note})
    target.write_text(json.dumps(entries, indent=2) + "\n")
    return target


def add_feature(top: pathlib.Path, area: str, feature: str, priority: str,
                reference: str = "yes", clone: str = "no", notes: str = "") -> pathlib.Path:
    target = paths_for(top)["features"]
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.is_file():
        target.write_text("area,feature,priority,reference,clone,notes\n")
    with target.open("a", newline="") as handle:
        csv.writer(handle).writerow([area, feature, priority, reference, clone, notes])
    return target


# --------------------------------------------------------------------------
# wizard
# --------------------------------------------------------------------------

def _menu() -> str:
    return "\n".join([
        "  [1] brand colours and a contrast check   (tokens.json)",
        "  [2] waive a Slop Gate signal, with a reason (overrides.json)",
        "  [3] add a feature to match               (features.csv)",
        "  [4] check the configuration",
        "  [5] show what is active",
        "  [6] done",
    ])


def wizard(top: pathlib.Path) -> int:
    print(render_show(top))
    while True:
        print()
        print(_menu())
        choice = ui.ask("Select", "6")
        if choice in {"6", "", "q"}:
            return 0
        if choice == "1":
            print()
            ground = ui.ask("Ground colour", "#F7F4EE")
            ink = ui.ask("Ink colour", "#1C1A17")
            brand = ui.ask("Brand colour", "#8C3B52")
            try:
                for value in (ground, ink, brand):
                    engine.to_rgb(value)
            except ValueError as exc:
                print(ui.bad(f"  {exc}"))
                continue
            doc = write_tokens(top, ground, ink, brand)
            print(ui.ok(f"  wrote {paths_for(top)['tokens']}"))
            for pair in doc["pairs"]:
                fg = engine.resolve(pair["fg"], doc)
                bg = engine.resolve(pair["bg"], doc)
                need = engine.THRESHOLDS[pair["kind"]]
                ratio = engine.contrast(fg, bg)
                mark = ui.ok("pass") if ratio >= need else ui.bad("FAIL")
                print(f"    {mark}  {ratio:>6}:1  needs {need}  {pair['label']}")
        elif choice == "2":
            print()
            for sid, (weight, title, _measured) in engine.SIGNALS.items():
                print(f"    {sid}  w{weight}  {title}")
            sid = ui.ask("Signal id", "").upper()
            if sid not in engine.SIGNALS:
                print(ui.bad(f"  {sid or '(empty)'} is not a signal id"))
                continue
            print("  reason:")
            for index, reason in enumerate(REASONS, start=1):
                print(f"    [{index}] {reason.ljust(15)} {REASON_BLURB[reason]}")
            answer = ui.ask("Select reason", "1")
            reason = REASONS[int(answer) - 1] if answer.isdigit() and 1 <= int(answer) <= len(REASONS) else answer.lower()
            if reason not in REASONS:
                print(ui.bad(f"  {reason!r} is not an allowed reason"))
                continue
            note = ui.ask("One sentence explaining why", "")
            if not note:
                print(ui.warn("  a waiver with no sentence is refused by the audit; write one"))
                continue
            print(ui.ok(f"  wrote {add_override(top, sid, reason, note)}"))
        elif choice == "3":
            print()
            area = ui.ask("Area (for example: booking)", "core")
            feature = ui.ask("Feature", "")
            if not feature:
                continue
            priority = ui.ask("Priority (must / should / could)", "should").lower()
            if priority not in engine.PRIORITY_WEIGHT:
                print(ui.bad(f"  {priority!r} is not must, should or could"))
                continue
            clone = ui.ask("Your progress (yes / partial / no)", "no").lower()
            if clone not in engine.CLONE_VALUE:
                print(ui.bad(f"  {clone!r} is not yes, partial or no"))
                continue
            print(ui.ok(f"  wrote {add_feature(top, area, feature, priority, 'yes', clone)}"))
        elif choice == "4":
            code, lines = check(top)
            print()
            print("\n".join(lines))
        elif choice == "5":
            print()
            print(render_show(top))
        else:
            print(f"  {choice!r} is not one of the numbers above")


def command(args) -> int:
    top = pathlib.Path(getattr(args, "dir", ".") or ".").resolve()
    if not top.is_dir():
        print(f"config: {top} is not a directory", file=sys.stderr)
        return 2
    if getattr(args, "show", False):
        print(render_show(top))
        return 0
    if getattr(args, "check", False):
        code, lines = check(top)
        print("\n".join(lines))
        return code
    if not ui.is_interactive():
        print(render_show(top))
        print()
        print("  not a terminal, so nothing was asked. Use --show or --check,")
        print("  or run `aomi config` from a terminal.")
        return 0
    return wizard(top)
