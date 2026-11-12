#!/usr/bin/env python3
"""Aomi's measurement engine. Standard library only, no network.

    python3 scripts/aomi.py init [dir]
    python3 scripts/aomi.py audit <dir> [--json] [--overrides FILE] [--tokens FILE]
    python3 scripts/aomi.py contrast <file.json> [--json]
    python3 scripts/aomi.py parity <features.csv> [--json]
    python3 scripts/aomi.py doctor [--root DIR] [--json]

Every command that grades something exits non-zero when the grade is a failure,
so it can be used as a gate in a build or a pre-commit hook.

The signal definitions implemented here are documented, with their weights and
what waiving them means, in design/slop-gate.md.
"""
from __future__ import annotations

import argparse
import colorsys
import csv
import json
import pathlib
import re
import sys

from . import __version__ as VERSION
from .paths import templates_dir

# --------------------------------------------------------------------------
# colour
# --------------------------------------------------------------------------

HEX = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")


def to_rgb(value: str) -> tuple[int, int, int]:
    h = value.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"not a hex colour: {value!r}")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _linear(channel: int) -> float:
    s = channel / 255
    return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4


def luminance(value: str) -> float:
    r, g, b = to_rgb(value)
    return 0.2126 * _linear(r) + 0.7152 * _linear(g) + 0.0722 * _linear(b)


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return round((hi + 0.05) / (lo + 0.05), 2)


def hue_saturation(value: str) -> tuple[float, float, float]:
    r, g, b = (c / 255 for c in to_rgb(value))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360, s, l


THRESHOLDS = {"body": 4.5, "large": 3.0, "ui": 3.0}


# --------------------------------------------------------------------------
# overrides
# --------------------------------------------------------------------------

ALLOWED_REASONS = {"brand", "content", "accessibility", "hardware", "legacy"}


def load_overrides(path: pathlib.Path | None) -> tuple[dict[str, dict], list[str]]:
    """Return {signal: entry} plus a list of problems with the file itself."""
    if not path or not path.exists():
        return {}, []
    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        return {}, [f"overrides file is not valid JSON: {exc}"]
    if isinstance(raw, dict):
        raw = raw.get("overrides", [])
    waivers, problems = {}, []
    for entry in raw if isinstance(raw, list) else []:
        sid = str(entry.get("signal", "")).upper()
        reason = str(entry.get("reason", "")).lower()
        if not sid:
            problems.append("waiver with no signal id")
            continue
        if reason not in ALLOWED_REASONS:
            problems.append(
                f"{sid}: reason {reason!r} is not one of {sorted(ALLOWED_REASONS)}"
            )
            continue
        waivers[sid] = {"reason": reason, "note": str(entry.get("note", "")).strip()}
    return waivers, problems


# --------------------------------------------------------------------------
# audit
# --------------------------------------------------------------------------

SOURCE_SUFFIXES = {".html", ".htm", ".css", ".scss", ".jsx", ".tsx", ".vue", ".svelte", ".astro", ".js", ".ts"}
SKIP_DIRS = {".git", "node_modules", "dist", "build", ".next", ".venv", "venv", "__pycache__", ".cache", "coverage", "assets"}

VIOLET_UTILITIES = re.compile(r"\b(?:bg|text|border|from|to|via|ring|fill|stroke)-(?:indigo|violet|purple|fuchsia)-\d{2,3}\b")
EMOJI = re.compile(
    "[" "\U0001F300-\U0001FAFF" "\U00002600-\U000027BF" "\U0001F000-\U0001F0FF" "\u2b00-\u2bff" "\u2190-\u21ff" "]"
)
HYPE = re.compile(
    r"\b(supercharge[ds]?|unlock(?:s|ing)?|seamless(?:ly)?|effortless(?:ly)?|revolutioni[sz]e[ds]?|"
    r"elevate[ds]?|next-generation|cutting-edge|game-chang(?:er|ing)|world-class|best-in-class|"
    r"empower(?:s|ing)?|leverage|synerg(?:y|ies))\b",
    re.I,
)
FAKE_PROOF = re.compile(
    r"(trusted by\s+[\d,.]+|[\d,]{3,}\+?\s*(?:users|customers|teams|companies|businesses)|"
    r"\b\d{2,3}(?:\.\d+)?%\s+(?:faster|better|more|increase|growth|conversion))",
    re.I,
)
TESTIMONIAL_NAME = re.compile(r"[\"'](?:[A-Z][a-z]+ [A-Z]\.)[,\s]", re.M)
GRADIENT = re.compile(r"(linear|radial|conic)-gradient\s*\(", re.I)
BLUR = re.compile(r"backdrop-(?:filter|blur)|filter\s*:\s*blur\s*\(", re.I)
GLOW = re.compile(r"box-shadow\s*:\s*[^;]*0\s+0\s+(\d{2,})px", re.I)
RADIUS = re.compile(r"border-radius\s*:\s*([^;}\n]+)", re.I)
RADIUS_UTIL = re.compile(r"\brounded(?:-[trbl]{1,2})?-(none|sm|md|lg|xl|2xl|3xl|full)\b")
HOVER_SCALE = re.compile(r"hover:scale-\d{2,3}|:hover[^{}]*\{[^}]*transform\s*:\s*scale\(", re.I)
MOTION = re.compile(r"\b(animation|transition)\s*:|animate-|transition-|@keyframes", re.I)
REDUCED_MOTION = re.compile(r"prefers-reduced-motion", re.I)
CENTERED_HERO = re.compile(r"(text-center|text-align\s*:\s*center)", re.I)
HERO = re.compile(r"\bhero\b", re.I)
INPUT_TAG = re.compile(r"<input\b[^>]*>", re.I)
LABEL_TAG = re.compile(r"<label\b", re.I)
IMG_TAG = re.compile(r"<img\b[^>]*>", re.I)
ALT_ATTR = re.compile(r"\balt\s*=", re.I)
GRID3 = re.compile(r"grid-cols-3|repeat\(\s*3\s*,\s*minmax", re.I)
PY_PADDING = re.compile(r"\bpy-(\d{1,2})\b")
CSS_PADDING = re.compile(r"padding-(?:top|block-start)\s*:\s*([^;}\n]+)", re.I)
MAP_CALL = re.compile(r"\.map\s*\(")
EMPTY_STATE = re.compile(r"(length\s*===?\s*0|isEmpty|\.empty\b|no results|nothing here)", re.I)
FONT_FAMILY = re.compile(r"font-family\s*:\s*([^;}\n]+)", re.I)
FONT_UTIL = re.compile(r"\bfont-(?!family|weight|normal|bold|medium|semibold|semilight|light|black|extrabold|thin|sans|serif|mono)([a-z0-9-]+)\b")


# The catalogue is the single source for ids, weights and titles: the audit uses
# it, `aomi config` shows it, and tests/test_aomi.py fails when design/slop-gate.md
# disagrees with it.
SIGNALS: dict[str, tuple[int, str, bool]] = {
    "SG01": (3, "violet-indigo accent with no brand basis", True),
    "SG02": (2, "one neutral typeface for every role", False),
    "SG03": (1, "a single radius on every surface", True),
    "SG04": (2, "decorative gradient, blur or glow", True),
    "SG05": (3, "emoji used as an icon", True),
    "SG06": (1, "cards scale on hover", True),
    "SG07": (3, "motion without a reduced-motion path", True),
    "SG08": (2, "hype lexicon", True),
    "SG09": (2, "centred hero with a symmetric action pair", False),
    "SG11": (3, "form control without a label", True),
    "SG12": (1, "the same three-column grid, three times or more", True),
    "SG13": (2, "image without alternative text", True),
    "SG14": (3, "a state that exists in the data but not the interface", False),
    "SG15": (4, "proof that cannot be traced", True),
    "SG16": (1, "uniform section rhythm", True),
}


def build_signals() -> dict[str, "Signal"]:
    return {sid: Signal(sid, weight, title, measured)
            for sid, (weight, title, measured) in SIGNALS.items()}


class Signal:
    def __init__(self, sid: str, weight: int, title: str, measured: bool = True):
        self.sid, self.weight, self.title, self.measured = sid, weight, title, measured
        self.evidence: list[str] = []

    def add(self, where: str, detail: str) -> None:
        if len(self.evidence) < 4:
            self.evidence.append(f"{where}: {detail}")

    @property
    def fired(self) -> bool:
        return bool(self.evidence)


def iter_sources(root: pathlib.Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        try:
            if path.stat().st_size > 1_500_000:
                continue
            yield path, path.read_text(errors="ignore")
        except OSError:
            continue


def audit(root: pathlib.Path, overrides: dict[str, dict]) -> dict:
    signals = build_signals()

    radii: set[str] = set()
    radius_hits = 0
    families: set[str] = set()
    paddings: set[str] = set()
    padding_hits = 0
    motion_seen = False
    reduced_seen = False
    grid3_hits = 0
    inputs = labels = 0
    imgs = imgs_alt = 0
    files = 0

    for path, text in iter_sources(root):
        files += 1
        where = str(path.relative_to(root))

        for match in HEX.finditer(text):
            h, s, l = hue_saturation("#" + match.group(1))
            if 245 <= h <= 300 and s > 0.45 and 0.28 < l < 0.78:
                signals["SG01"].add(where, f"{match.group(0)}")
                break
        for match in VIOLET_UTILITIES.finditer(text):
            signals["SG01"].add(where, match.group(0))
            break

        for match in EMOJI.finditer(text):
            ctx = text[max(0, match.start() - 40) : match.end() + 20].replace("\n", " ")
            if re.search(r"<button|<a\b|class=|title=", ctx, re.I):
                signals["SG05"].add(where, f"{match.group(0)} near markup")
                break

        if GRADIENT.search(text) or BLUR.search(text) or GLOW.search(text):
            hit = (GRADIENT.search(text) or BLUR.search(text) or GLOW.search(text))
            signals["SG04"].add(where, hit.group(0).strip())

        if HOVER_SCALE.search(text):
            signals["SG06"].add(where, HOVER_SCALE.search(text).group(0).strip())

        if MOTION.search(text):
            motion_seen = True
        if REDUCED_MOTION.search(text):
            reduced_seen = True

        for match in RADIUS.finditer(text):
            radii.add(match.group(1).strip().lower())
            radius_hits += 1
        for match in RADIUS_UTIL.finditer(text):
            radii.add(match.group(1))
            radius_hits += 1

        for match in HYPE.finditer(text):
            line = text[: match.start()].count("\n") + 1
            signals["SG08"].add(f"{where}:{line}", match.group(0).lower())

        for match in FAKE_PROOF.finditer(text):
            signals["SG15"].add(where, match.group(0).strip())
        for match in TESTIMONIAL_NAME.finditer(text):
            signals["SG15"].add(where, "name-shaped testimonial")

        center = CENTERED_HERO.search(text)
        if HERO.search(text) and center:
            buttons = len(re.findall(r"<button\b|<a\b[^>]*class=\"[^\"]*btn", text, re.I))
            if buttons >= 2:
                signals["SG09"].add(where, f"hero + {center.group(0)} + {buttons} actions")

        for match in INPUT_TAG.finditer(text):
            inputs += 1
            tag = match.group(0)
            if not re.search(r"\baria-label|\bid\s*=", tag, re.I):
                signals["SG11"].add(where, "input with no id or aria-label")
        labels += len(LABEL_TAG.findall(text))

        for match in IMG_TAG.finditer(text):
            imgs += 1
            if ALT_ATTR.search(match.group(0)):
                imgs_alt += 1
            else:
                signals["SG13"].add(where, "img without alt")

        grid3_hits += len(GRID3.findall(text))

        if MAP_CALL.search(text) and not EMPTY_STATE.search(text):
            signals["SG14"].add(where, "list rendered without an empty case in the same file")

        for match in PY_PADDING.finditer(text):
            paddings.add(match.group(1).strip())
            padding_hits += 1
        for match in CSS_PADDING.finditer(text):
            paddings.add(match.group(1).strip())
            padding_hits += 1

        for match in FONT_FAMILY.finditer(text):
            for name in match.group(1).split(","):
                families.add(name.strip().strip("'\"").lower())
        for match in FONT_UTIL.finditer(text):
            families.add("util:" + match.group(1))

    if files == 0:
        return {
            "root": str(root),
            "files": 0,
            "signals": [],
            "score": 100,
            "verdict": "nothing to audit",
            "penalty": 0,
            "overrides": {},
            "override_problems": [],
        }

    if motion_seen and not reduced_seen:
        signals["SG07"].add(
            "corpus", "motion or transitions present, `prefers-reduced-motion` absent"
        )

    if radius_hits >= 5 and len(radii) == 1:
        signals["SG03"].add("corpus", f"{radius_hits} surfaces, all radius {next(iter(radii))}")

    if grid3_hits >= 3:
        signals["SG12"].add("corpus", f"three-column grid {grid3_hits} times")

    if padding_hits >= 3 and len(paddings) == 1:
        signals["SG16"].add("corpus", f"{padding_hits} sections, all padding {next(iter(paddings))}")

    if len([f for f in families if not f.startswith("util:")]) == 1 and len(families) >= 1:
        signals["SG02"].add("corpus", f"one typeface only: {next(iter(families))}")

    if inputs and labels < inputs:
        signals["SG11"].add("corpus", f"{inputs} inputs against {labels} labels")

    scored, waived, penalties = [], [], 0
    for sid, signal in signals.items():
        if not signal.fired:
            continue
        entry = {"id": sid, "weight": signal.weight, "title": signal.title,
                 "measured": signal.measured, "evidence": signal.evidence}
        if sid in overrides:
            entry["waived"] = overrides[sid]
            waived.append(entry)
        else:
            penalties += signal.weight
            scored.append(entry)

    score = max(0, 100 - 7 * penalties)
    verdict = "clear" if score >= 85 else ("pass with notes" if score >= 70 else "blocked")
    return {
        "root": str(root),
        "files": files,
        "signals": scored,
        "waived": waived,
        "score": score,
        "verdict": verdict,
        "penalty": penalties,
        "overrides": overrides,
        "override_problems": [],
    }


FIXES = {
    "SG01": "use your own brand colour, or move the accent off violet-indigo",
    "SG02": "give one role a second weight or face, or choose a single-face system on purpose",
    "SG03": "vary radius with the element: inputs md, cards lg, dialogs xl",
    "SG04": "remove the gradient or glow, or write what it communicates",
    "SG05": "use one icon set rather than emoji",
    "SG06": "change colour or shadow on hover, not size",
    "SG07": "add a prefers-reduced-motion branch that drops the transition",
    "SG08": "replace the claim with the concrete outcome, or delete it",
    "SG09": "give one action the weight and demote the other to a link",
    "SG11": "add a label element, or an aria-label where the design has none",
    "SG12": "vary the grid, or say why the repetition earns its place",
    "SG13": "add alt text that says what the image shows",
    "SG14": "add the empty, error and denied branches for that list",
    "SG15": "show where the number came from, or remove it",
    "SG16": "vary section padding so sections read as different things",
}


def _severity(weight: int) -> tuple[int, str]:
    if weight >= 3:
        return 0, "critical"
    if weight == 2:
        return 1, "warning"
    return 2, "info"


def render_audit(report: dict) -> str:
    """A summary a person can read in three lines, then the findings by weight."""
    out = [f"Aomi design audit   {report['root']}", ""]
    if report["files"] == 0:
        out.append("  files scanned   0")
        out.append("")
        out.append("  Nothing to audit: no markup or style files of a known type were found.")
        out.append("  Point this at the folder that holds them, for example `aomi audit ./src`.")
        return "\n".join(out) + "\n"

    scored = report["signals"]
    counts = {"critical": 0, "warning": 0, "info": 0}
    for sig in scored:
        counts[_severity(sig["weight"])[1]] += 1
    status = {"clear": "CLEAR", "pass with notes": "REVIEW REQUIRED", "blocked": "BLOCKED"}
    label = status.get(report["verdict"], report["verdict"].upper())

    out.append(f"  files scanned   {report['files']}")
    out.append(f"  issues found    {len(scored)}"
               f"   critical {counts['critical']}, warning {counts['warning']}, info {counts['info']}")
    out.append(f"  score           {report['score']}/100")
    out.append(f"  status          {label}")

    if not scored and not report.get("waived"):
        out.append("")
        out.append("  No signals fired. That clears the sweep, not the judgement:")
        out.append("  write the Swap Test result and the hierarchy claim in proof.md.")
        return "\n".join(out) + "\n"

    ordered = sorted(scored, key=lambda s: (-s["weight"], s["id"]))
    for sig in ordered:
        _, severity = _severity(sig["weight"])
        head = f"  {sig['id']}  w{sig['weight']}  {sig['title']}"
        out.append("")
        pad = max(2, 78 - len(severity) - len(head))
        out.append(f"{head}{' ' * pad}{severity}")
        for line in sig["evidence"][:2]:
            out.append(f"        {line}")
        fix = FIXES.get(sig["id"])
        if fix:
            out.append(f"        fix: {fix}")

    for sig in report.get("waived") or []:
        reason = sig.get("waived", {}).get("reason", "")
        out.append("")
        out.append(f"  {sig['id']}  w{sig['weight']}  waived ({reason}): {sig['title']}")

    if report["score"] < 70:
        out.append("")
        out.append("  Blocked. Fix the weight-3 and weight-4 findings first: those are the")
        out.append("  ones a reader notices without being told.")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------
# contrast
# --------------------------------------------------------------------------

def resolve(token: str, tokens: dict) -> str:
    if token.startswith("#"):
        return token
    if token in tokens:
        value = tokens[token]
        if isinstance(value, dict):
            value = value.get("value") or value.get("hex")
        if isinstance(value, str):
            return value if value.startswith("#") else resolve(value, tokens)
    raise KeyError(token)


def collect_pairs(doc: dict) -> list[dict]:
    tokens = {k: v for k, v in doc.items() if k not in {"pairs", "meta", "$schema"}}
    pairs = doc.get("pairs")
    if isinstance(pairs, list) and pairs:
        normalised = []
        for item in pairs:
            if isinstance(item, dict):
                normalised.append(item)
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                normalised.append({"fg": item[0], "bg": item[1]})
            else:
                raise ValueError(f"unreadable pair: {item!r}")
        return normalised
    # No explicit pairs: pair every text-role token against the ground role.
    ground = next((k for k in tokens if re.search(r"ground|bg|background", k)), None)
    if not ground:
        raise ValueError("no 'pairs' and no ground token to pair against")
    return [
        {"fg": k, "bg": ground, "label": k}
        for k in tokens
        if re.search(r"ink|text|label|caption", k)
    ]


def command_contrast(args) -> int:
    path = pathlib.Path(args.file)
    try:
        doc = json.loads(path.read_text())
        pairs = collect_pairs(doc)
    except (OSError, json.JSONDecodeError, ValueError, KeyError) as exc:
        print(f"contrast: {exc}", file=sys.stderr)
        return 2

    tokens = {k: v for k, v in doc.items() if k not in {"pairs", "meta", "$schema"}}
    rows, failures = [], 0
    for pair in pairs:
        try:
            fg, bg = resolve(str(pair["fg"]), tokens), resolve(str(pair["bg"]), tokens)
        except (KeyError, ValueError) as exc:
            rows.append({"pair": f"{pair.get('fg')} / {pair.get('bg')}", "error": f"unresolved token {exc}"})
            failures += 1
            continue
        kind = str(pair.get("kind", "body")).lower()
        need = THRESHOLDS.get(kind, 4.5)
        ratio = contrast(fg, bg)
        ok = ratio >= need
        failures += 0 if ok else 1
        rows.append({
            "pair": str(pair.get("label") or f"{pair['fg']} on {pair['bg']}"),
            "fg": fg, "bg": bg, "ratio": ratio, "need": need, "kind": kind,
            "status": "pass" if ok else "FAIL",
        })

    if args.json:
        print(json.dumps({"rows": rows, "failures": failures}, indent=2))
    else:
        print(f"{'':6}{'ratio':>7}  {'need':>5}  pair")
        for row in rows:
            if "error" in row:
                print(f"{'ERROR':6}{'':>7}  {'':>5}  {row['pair']}: {row['error']}")
                continue
            print(f"{row['status']:6}{row['ratio']:>7}  {row['need']:>5}  {row['pair']}")
        print(f"\n{len(rows)} pairs, {failures} failing")
    return 1 if failures else 0


# --------------------------------------------------------------------------
# parity
# --------------------------------------------------------------------------

PRIORITY_WEIGHT = {"must": 3, "should": 2, "could": 1}
CLONE_VALUE = {"yes": 1.0, "partial": 0.5, "no": 0.0, "": 0.0}


def command_parity(args) -> int:
    path = pathlib.Path(args.file)
    try:
        rows = list(csv.DictReader(path.read_text().splitlines()))
    except OSError as exc:
        print(f"parity: {exc}", file=sys.stderr)
        return 2
    if not rows:
        print("parity: the file has no rows", file=sys.stderr)
        return 2

    total = earned = 0.0
    missing_must, by_area = [], {}
    for row in rows:
        priority = (row.get("priority") or "").strip().lower()
        clone = (row.get("clone") or "").strip().lower()
        reference = (row.get("reference") or "").strip().lower()
        if reference == "no":  # present in your product, not in the reference: not scored
            continue
        weight = PRIORITY_WEIGHT.get(priority)
        if weight is None:
            print(f"parity: skipping row with unknown priority {priority!r}: {row.get('feature')}", file=sys.stderr)
            continue
        value = CLONE_VALUE.get(clone, 0.0)
        total += weight
        earned += weight * value
        area = (row.get("area") or "untagged").strip()
        bucket = by_area.setdefault(area, [0.0, 0.0])
        bucket[0] += weight * value
        bucket[1] += weight
        if priority == "must" and value < 1.0:
            missing_must.append(row)

    score = round(earned / total * 100, 1) if total else 0.0
    report = {
        "score": score,
        "missing_must": [r.get("feature") for r in missing_must],
        "areas": {k: round(v[0] / v[1] * 100, 1) for k, v in by_area.items() if v[1]},
        "rows": len(rows),
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Parity {score}/100   ({len(rows)} features)")
        must_done = sum(1 for r in rows if (r.get("priority") or "").lower() == "must" and (r.get("clone") or "").lower() == "yes")
        must_all = sum(1 for r in rows if (r.get("priority") or "").lower() == "must")
        print(f"must-haves: {must_done}/{must_all}")
        if missing_must:
            print("\nNot shippable yet:")
            for row in missing_must:
                print(f"  - {row.get('area')}: {row.get('feature')} ({(row.get('clone') or 'no').strip()})")
        print("\nBy area:")
        for area, value in sorted(report["areas"].items(), key=lambda kv: kv[1]):
            print(f"  {area:24} {value:5.1f}")
    return 1 if missing_must else 0


# --------------------------------------------------------------------------
# doctor
# --------------------------------------------------------------------------

LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
CODE_PATH = re.compile(r"`([A-Za-z0-9_][\w./-]*\.(?:md|py|json|csv|svg|png))`")
UPSTREAM_FILES = ["sweep.py", "imgdiff.py", "parity.py", "reviews.py", "listing.py",
                  "contrast.py", "slop-uiux-patterns.md", "slop-code-patterns.md",
                  "ui-reasoning.csv", "recon-map.md", "features.csv.bak", "_load.py"]
# files allowed to name upstream files: the doctor defines the list, provenance
# explains the audit, and the tests assert it
UPSTREAM_ALLOWED = {"docs/provenance.md", "README.md", "tests/test_aomi.py",
                    "tests/test_cli_ux.py", "aomi/engine.py", "scripts/aomi.py"}


def command_doctor(args) -> int:
    root = pathlib.Path(args.root).resolve()
    checks: list[dict] = []

    def add(level: str, code: str, message: str) -> None:
        checks.append({"level": level, "code": code, "message": message})

    skill = root / "SKILL.md"
    if not skill.exists():
        add("error", "E100", "SKILL.md is missing")
    else:
        text = skill.read_text()
        head = text.split("---")[1] if text.startswith("---") else ""
        for field in ("name:", "description:"):
            if field not in head:
                add("error", "E101", f"SKILL.md frontmatter has no {field.rstrip(':')}")

    broken = 0
    for md in root.rglob("*.md"):
        if any(part in {".git", "node_modules", "fixtures", "build", "dist", "__pycache__"}
               for part in md.relative_to(root).parts):
            continue
        for target in LINK.findall(md.read_text(errors="ignore")):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            clean = target.split("#")[0].strip()
            if not clean:
                continue
            if not (md.parent / clean).exists():
                broken += 1
                add("error", "E110", f"{md.relative_to(root)} links to missing {clean}")
    if not broken:
        add("ok", "E110", "every relative markdown link resolves")

    licence = root / "LICENSE"
    if not licence.exists():
        add("error", "E120", "LICENSE is missing")
    elif "AOMI PERSONAL USE LICENSE" not in licence.read_text():
        add("error", "E120", "LICENSE is not the Aomi licence")

    for name in ("README.md", ".gitignore"):
        if not (root / name).exists():
            add("error", "E130", f"{name} is missing")

    readme = root / "README.md"
    if readme.exists():
        for asset in re.findall(r"assets/[\w.-]+\.(?:png|svg|jpg)", readme.read_text()):
            path = root / asset
            if not path.exists():
                add("error", "E140", f"README references missing {asset}")
            elif path.stat().st_size > 400_000:
                add("warn", "W140", f"{asset} is {path.stat().st_size // 1024} KB; consider shrinking")

    for path in root.rglob("*"):
        if path.suffix not in SOURCE_SUFFIXES | {".md", ".py"} or not path.is_file():
            continue
        rel = str(path.relative_to(root))
        if rel in UPSTREAM_ALLOWED or any(
            part in {".git", "tests", "fixtures", "build", "dist", "__pycache__"}
            for part in path.relative_to(root).parts
        ):
            continue
        body = path.read_text(errors="ignore")
        for marker in UPSTREAM_FILES:
            if marker in body and marker not in rel:
                add("warn", "W150", f"{rel} mentions {marker}, which is an upstream file name")

    for py in (root / "scripts").glob("*.py"):
        try:
            compile(py.read_text(), str(py), "exec")
        except SyntaxError as exc:
            add("error", "E160", f"{py.name} does not parse: {exc}")
    for py in (root / "tests").glob("*.py"):
        try:
            compile(py.read_text(), str(py), "exec")
        except SyntaxError as exc:
            add("error", "E160", f"tests/{py.name} does not parse: {exc}")

    errors = sum(1 for c in checks if c["level"] == "error")
    warnings = sum(1 for c in checks if c["level"] == "warn")
    if args.json:
        print(json.dumps({"checks": checks, "errors": errors, "warnings": warnings}, indent=2))
    else:
        print(f"Aomi doctor  {root}")
        for check in checks:
            if check["level"] == "ok":
                continue
            print(f"  {check['level']:5} {check['code']}  {check['message']}")
        print(f"\n{errors} errors, {warnings} warnings")
    return 1 if errors else 0


# --------------------------------------------------------------------------
# init
# --------------------------------------------------------------------------


def command_audit(args) -> int:
    root = pathlib.Path(args.dir).resolve()
    if not root.exists():
        print(f"audit: {root} does not exist", file=sys.stderr)
        return 2
    override_path = pathlib.Path(args.overrides) if args.overrides else root / "aomi" / "overrides.json"
    waivers, problems = load_overrides(override_path)
    report = audit(root, waivers)
    report["override_problems"] = problems
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        sys.stdout.write(render_audit(report))
        for problem in problems:
            print(f"override ignored: {problem}")
    return 0 if report["score"] >= 70 else 1
