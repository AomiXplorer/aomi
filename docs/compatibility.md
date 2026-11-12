# Compatibility

One source of instructions, several hosts. This file records what was checked,
what is only documented, and how to adapt without forking the behaviour.

## What Aomi needs from a host

1. A Markdown file with YAML frontmatter containing `name` and `description`,
   which the host uses to decide when to load the skill.
2. The ability to read other files in the same folder on demand.
3. The ability to run a shell command, if the gates are wanted.

Requirement 3 is optional. Without it the instructions still work; the
measurements in `proof.md` then have to be produced by hand.

## Status, honestly

| host | status | installs to | what that status means |
| --- | --- | --- | --- |
| A folder-based skill host | **tested** | `.agents/skills/aomi` | installed into a real skill library, loaded by the host's skill runner, and the CLI executed from the installed folder |
| Claude Code | path documented | `.claude/skills/aomi/`, `~/.claude/skills/aomi/` | layout taken from Claude Code's skills documentation; the folder was copied by `aomi install` and verified on disk |
| OpenCode | path documented | `.opencode/skills/aomi/`, `~/.config/opencode/skills/aomi/` | layout from OpenCode's skills documentation, which also reads `.claude/skills` and `.agents/skills` |
| Cursor | path documented | `.cursor/skills/aomi/`, `~/.cursor/skills/aomi/` | layout from Cursor's Agent Skills documentation; it requires the folder name to match the frontmatter `name`, which it does |
| Windsurf / Devin Local | path documented | `.windsurf/skills/aomi/`, `~/.config/devin/skills/aomi/` | layout from Windsurf's documentation, which notes `.windsurf/skills` is still read and `.devin/skills` and `.agents/skills` are also read |
| GitHub Copilot | documented, not run | `.github/skills/aomi/` | the path follows Copilot's skill documentation; it has not been exercised inside a Copilot session, and its project scoping may differ on your version |
| Codex | documented, not run | `.codex/skills/aomi/`, `~/.codex/skills/aomi/` | Codex reads `AGENTS.md` for project rules; its skill folder path was not confirmed in a session here |
| anything else | manual | any folder the host can read | the frontmatter is the only hard requirement; see [installation](installation.md) |

"Path documented" means the location comes from that agent's own documentation and
the copy on disk was verified: required files present, frontmatter readable, every
relative link resolving inside the folder. It does **not** mean Aomi was run inside
that agent. When it is, the row moves to **tested** and this file says what was done.

`aomi agents` prints the same table with `documented` or `documented, not run here`
beside each entry, and `aomi install --dir PATH` puts the skill anywhere else.

## The wrapper for script runners

Some hosts call a skill through a single entry script. Aomi's tool takes
arguments, so the wrapper is the smallest thing that makes that work: it accepts
the whole argument string, splits it, and calls the command.

```bash
# scripts/run.sh, shipped inside the installed skill
mapfile -t ARGS < <(python3 -c 'import shlex,sys
for a in shlex.split(sys.argv[1]): print(a)' "${*:-}")

if command -v aomi >/dev/null 2>&1; then
  exec aomi "${ARGS[@]}"
fi
here="$(cd "$(dirname "$0")/.." && pwd)"
if [ -f "$here/aomi/cli.py" ]; then
  exec python3 -m aomi "${ARGS[@]}"
fi
```

`run_skill("aomi", "audit ./src")` then behaves like `aomi audit ./src`. It uses the
installed command when there is one, and the checkout beside it when there is not.

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
