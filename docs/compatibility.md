# Compatibility

One source of instructions, several hosts. This file records what was actually
tested, what should work and has not been tested, and how to adapt without
forking the behaviour.

## What Aomi needs from a host

1. A Markdown file with YAML frontmatter containing `name` and `description`,
   which the host uses to decide when to load the skill.
2. The ability to read other files in the same folder on demand.
3. The ability to run a shell command, if the gates are wanted.

Requirement 3 is optional. Without it the instructions still work; the
measurements in `proof.md` then have to be produced by hand.

## Status, honestly

| host | status | how it loads | notes |
| --- | --- | --- | --- |
| A folder-based skill host | **tested** | `.agents/skills/aomi/` with `SKILL.md` plus a `scripts/run.sh` wrapper | installed into a real skill library, loaded by the host's skill runner, and the CLI executed from the skill folder |
| Claude Code | format compatible, not tested here | `~/.claude/skills/aomi/` or a project `.claude/skills/aomi/` | expects `SKILL.md` with `name` and `description` in frontmatter, which Aomi has; deeper files are read on demand as relative paths |
| Cursor | format compatible, not tested here | a rules or skill folder the host indexes | long instruction sets get truncated, which is why `SKILL.md` is the short file |
| Windsurf | format compatible, not tested here | rules directory | same caveat as Cursor |
| GitHub Copilot | format compatible, not tested here | repository custom instructions, or a skill folder where supported | instruction files are usually one document; point it at `SKILL.md` and keep the folder reachable |
| Codex | format compatible, not tested here | `AGENTS.md` style instructions or a skill folder | if only one file can be supplied, `SKILL.md` plus `core/workflow.md` is the minimum useful pair |
| anything else | depends | any folder the host can read | the frontmatter is the only hard requirement |

"Format compatible" means the file satisfies the documented shape the host
describes and depends on no feature specific to another host. It does **not**
mean it was run there. When it is tested somewhere, move the row to **tested**
and say what was done.

## The wrapper for script runners

Some hosts call a skill through a single entry script. Aomi's tool takes
arguments, so the wrapper is the smallest thing that makes that work: it accepts
the whole argument string and splits it.

```bash
# .agents/skills/aomi/scripts/run.sh
#!/usr/bin/env bash
set -euo pipefail
mapfile -t ARGS < <(python3 -c 'import shlex,sys
for a in shlex.split(sys.argv[1]): print(a)' "${*:-}")
exec python3 "$(dirname "$0")/aomi.py" "${ARGS[@]}"
```

`run_skill("aomi", "audit ./src")` then behaves like
`python3 scripts/aomi.py audit ./src`.

## Keeping one behaviour across hosts

- **Never copy the instructions into a second file.** Adapter files point at
  `SKILL.md`; they do not restate it. Two copies drift within a month.
- **Host quirks belong in the adapter, not in the rules.** If a host cannot run
  commands, that is a fact about the host, not a change to the method.
- **The same gates apply everywhere.** A host that cannot measure contrast does
  not get to skip it; it gets to have a person measure it.
- **Say what is untested.** This table is the record. A row claiming support
  without evidence is a bug in the documentation.

## Minimum viable install

If a host can only take three files:

```
SKILL.md
core/workflow.md
design/slop-gate.md
```

That is the method in outline plus the quality gate. Everything else sharpens a
single phase.
