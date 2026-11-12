"""One adapter per agent, because the install locations are not the same.

Each entry records where that agent reads skills from, and whether the path was
confirmed in that agent's own documentation. An adapter that was built from
documentation but never run inside that agent says so in `note` and is listed
as unverified by `aomi agents`. Nothing here claims a host was tested when it
was not.
"""
from __future__ import annotations

import pathlib
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Adapter:
    key: str
    label: str
    project: str                 # install path relative to the project root
    global_path: str | None      # install path relative to $HOME
    docs: str                    # where the layout came from
    verified: bool               # confirmed against official documentation
    note: str = ""
    detect: tuple[str, ...] = field(default_factory=tuple)  # markers for auto-detection

    def path_for(self, scope: str, cwd: pathlib.Path, home: pathlib.Path) -> pathlib.Path:
        if scope == "global":
            if not self.global_path:
                raise ValueError(f"{self.label} has no documented global location")
            return home / self.global_path
        return cwd / self.project

    @property
    def scope_label(self) -> str:
        if self.global_path:
            return f"project: {self.project}   global: ~/{self.global_path}"
        return f"project: {self.project}"


def for_directory(target: pathlib.Path) -> Adapter:
    """A stand-in adapter for `--dir`: the folder is given, so the agent is unknown."""
    return Adapter(
        key="custom",
        label="your agent",
        project=str(target),
        global_path=None,
        docs="",
        verified=False,
        note="a folder you chose; `aomi` does not know where this agent reads skills",
    )


ADAPTERS: tuple[Adapter, ...] = (
    Adapter(
        key="claude",
        label="Claude Code",
        project=".claude/skills/aomi",
        global_path=".claude/skills/aomi",
        docs="https://docs.claude.com/en/docs/claude-code/skills",
        verified=True,
        note="personal skills live in ~/.claude/skills/<name>/, project skills in .claude/skills/",
        detect=(".claude",),
    ),
    Adapter(
        key="opencode",
        label="OpenCode",
        project=".opencode/skills/aomi",
        global_path=".config/opencode/skills/aomi",
        docs="https://opencode.ai/docs/skills/",
        verified=True,
        note="one directory per skill, SKILL.md inside it; .claude/skills and .agents/skills are read too",
        detect=(".opencode", "opencode.json", "opencode.jsonc"),
    ),
    Adapter(
        key="cursor",
        label="Cursor",
        project=".cursor/skills/aomi",
        global_path=".cursor/skills/aomi",
        docs="https://cursor.com/docs/skills",
        verified=True,
        note="folder name must match the frontmatter name, which aomi does",
        detect=(".cursor",),
    ),
    Adapter(
        key="windsurf",
        label="Windsurf / Devin Local",
        project=".windsurf/skills/aomi",
        global_path=".config/devin/skills/aomi",
        docs="https://docs.windsurf.com/windsurf/cascade/memories",
        verified=True,
        note=".windsurf/skills is still read; new builds also read .devin/skills and .agents/skills",
        detect=(".windsurf", ".devin"),
    ),
    Adapter(
        key="copilot",
        label="GitHub Copilot",
        project=".github/skills/aomi",
        global_path=None,
        docs="https://docs.github.com/en/copilot",
        verified=False,
        note="skill folders are project scoped; Copilot also reads .github/copilot-instructions.md",
        detect=(".github/copilot-instructions.md", ".github/skills"),
    ),
    Adapter(
        key="codex",
        label="Codex",
        project=".codex/skills/aomi",
        global_path=".codex/skills/aomi",
        docs="https://developers.openai.com/codex/",
        verified=False,
        note="Codex reads AGENTS.md at the repo root; its skill folder is not confirmed in a session here",
        detect=("AGENTS.md", ".codex"),
    ),
    Adapter(
        key="agents",
        label="Any skill-aware agent (.agents/skills)",
        project=".agents/skills/aomi",
        global_path=".agents/skills/aomi",
        docs="https://github.com/AomiXplorer/aomi/blob/main/docs/compatibility.md",
        verified=True,
        note="the cross-agent folder Cursor, OpenCode and Windsurf all read",
        detect=(".agents",),
    ),
)

BY_KEY = {adapter.key: adapter for adapter in ADAPTERS}
ALIASES = {"claude-code": "claude", "claudecode": "claude", "devin": "windsurf",
           "windsurf-devin": "windsurf", "gh-copilot": "copilot", "open-code": "opencode",
           "generic": "agents", "other": "agents"}


def lookup(name: str) -> Adapter | None:
    key = (name or "").strip().lower()
    key = ALIASES.get(key, key)
    if key in BY_KEY:
        return BY_KEY[key]
    for adapter in ADAPTERS:  # allow "3" as a menu answer too
        if key == adapter.label.lower():
            return adapter
    return None


def from_number(number: str) -> Adapter | None:
    try:
        index = int(str(number).strip()) - 1
    except (TypeError, ValueError):
        return None
    return ADAPTERS[index] if 0 <= index < len(ADAPTERS) else None


def detect(cwd: pathlib.Path, home: pathlib.Path) -> list[tuple[Adapter, str]]:
    """Adapters whose marker exists here or in the home directory, with the marker found."""
    found: list[tuple[Adapter, str]] = []
    for adapter in ADAPTERS:
        for marker in adapter.detect:
            if (cwd / marker).exists():
                found.append((adapter, str(cwd / marker)))
                break
            if (home / marker).exists():
                found.append((adapter, str(home / marker)))
                break
    return found
