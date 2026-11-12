# Architecture

Aomi is one skill, not a shelf of them. This document explains how it is put
together, why it is split the way it is, and where a new piece belongs.

## The premise

Instructions cost context. A skill that must be read end to end before work
starts will be skimmed instead, and a skimmed rule is a rule that gets ignored at
the moment it matters.

So Aomi has one routing file and many reference files. `SKILL.md` reads the task,
names the two or three files that answer it, and stops. Everything else is loaded
on demand.

```
SKILL.md            the router: task table, non-negotiables, tool commands
```

## Layers

| layer | holds | loaded when |
| --- | --- | --- |
| `SKILL.md` | routing, the rules that cannot be broken, CLI surface | always |
| `core/` | philosophy, the loop, how to pick a depth level | starting any task |
| `engineering/` | recon, architecture, frontend, backend, quality, testing, ship | the task is technical |
| `design/` | direction, typography, colour, layout, components, interaction, accessibility, slop gate | the task has a surface |
| `references/` | font pairings, palettes with measured contrast, stack notes | a specific choice is being made |
| `templates/` | the artifact skeletons | writing an artifact |
| `aomi/` | the command line: a package, installable, one module per job | running a command |
| `scripts/` | the asset build, and a shim kept for old invocations | rebuilding assets |
| `tests/` | the suite, fixtures, scenarios | changing the tool |

Each file owns one subject and links to its neighbours rather than restating
them. A rule that exists in two files will disagree with itself within a month.

## The artifact set

Work leaves traces in `aomi/` inside the project being built, not in this
repository.

| artifact | written by | read by |
| --- | --- | --- |
| `brief.md` | Frame | every later phase |
| `map.md` | Read, when a reference product exists | Decide |
| `features.csv` | Read | Prove, Sign |
| `decisions.md` | Decide | Make, Polish, Sign |
| `proof.md` | Prove | Polish, Sign |
| `handoff.md` | Sign | whoever inherits the work |

The artifacts are plain Markdown and one CSV, for three reasons: a person can
read them without the skill, a diff shows what changed, and nothing depends on
the tool being installed.

## The command line

A package, standard library only, installed with pipx as `aomi`. The same code runs
from a checkout as `python3 -m aomi`, so nothing about the skill requires an
install.

| module | holds |
| --- | --- |
| `aomi/cli.py` | the parser, the dispatch, the exit codes |
| `aomi/engine.py` | the measurements: signals, colour maths, parity, links |
| `aomi/installer.py` | copy, update, prune, verify an installed skill |
| `aomi/adapters.py` | one entry per agent: its paths and where they came from |
| `aomi/initcmd.py`, `aomi/configcmd.py` | the two wizards |
| `aomi/paths.py` | where the skill files are, in a checkout or a wheel |
| `aomi/ui.py` | colour when the terminal supports it, plain text otherwise |

| command | grades something | exit code |
| --- | --- | --- |
| `install` | copies the skill into an agent's folder | 2 on a refused folder |
| `update` | refreshes installed copies | 2 when nothing is installed |
| `uninstall` | removes installed copies | 2 on a folder that is not Aomi |
| `init` | scaffolds `aomi/` | 0 |
| `audit` | Slop Gate signal sweep | 1 when below 70 |
| `contrast` | WCAG ratios for declared pairs | 1 on any failing pair |
| `parity` | weighted feature completion | 1 when a `must` is unfinished |
| `doctor` | the skill's own structure and links | 1 on any error |
| `config` | writes and validates the optional files | 1 on an invalid value |

Anything that grades exits non-zero, so it can be used as a gate in a pre-commit
hook or a CI step without wrapping it. `--json` is available on every grading
command for the same reason. `docs/cli.md` is the full reference.

The skill files and the command line ship together: `setup.py` copies `SKILL.md`,
`core/`, `engineering/`, `design/`, `references/`, `templates/`, `docs/`, `assets/`
and `LICENSE` into the wheel at build time, so an installed `aomi install` carries
the same tree a checkout has. Nothing is duplicated in git.

`scripts/build_assets.py` is separate: it rasterises the SVG sources in `assets/`
and is not part of the skill's behaviour. `scripts/aomi.py` is a small shim so an old
`python3 scripts/aomi.py ...` line in someone's script keeps working.

## Optional configuration

Nothing is required. These three files change what the tool can measure.

| file | effect | without it |
| --- | --- | --- |
| `aomi/overrides.json` | accepts specific Slop Gate signals, with a reason | every signal counts as it is |
| `aomi/tokens.json` | colour tokens and text pairs for the contrast gate | `contrast` is skipped |
| `aomi/features.csv` | the scope contract and the parity score | `parity` is skipped |

An override must carry one of five reasons: `brand`, `content`, `accessibility`,
`hardware`, `legacy`. Any other reason is refused and reported as refused. The
point is not to control the colour, it is to demand the sentence that explains
why.

## Adding a new area

A new engineering or design subject gets its own file in the matching folder, one
row in the `SKILL.md` task table, and nothing else. It does not get a copy of the
rules it shares with its neighbours, and it does not get a second entry point.
If the new file would restate an existing one, it is a section, not a file.

## What this architecture refuses

- A single long instruction file, because it will be skimmed.
- Two files that both claim to define the workflow.
- A rule enforced by documentation but not by `aomi/engine.py`. The weights in
  `design/slop-gate.md` are read by a test that fails when the code and the
  document disagree.
- Generated artifacts committed back into the skill. The skill holds instructions
  and tools; the project holds what the work produced.
