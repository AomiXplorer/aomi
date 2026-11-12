<p align="center">
  <img src="assets/logo.png" width="72" alt="Aomi mark: two overlapping circles with a single dot where they meet">
</p>

<h1 align="center">aomi.</h1>

<p align="center"><strong>Reverse Engineering &amp; Anti-AI-Slop Skill</strong></p>

<p align="center">A development skill for AI agents to analyze existing products, engineer better applications, and create distinctive interfaces without generic AI-generated design patterns.</p>

<p align="center">
  <img src="assets/hero.png" alt="Aomi banner: the mark and wordmark on cream, beside a framed panel of soft abstract artwork">
</p>

## Introduction

Aomi gives an AI agent a method instead of a mood. Given an existing product, it
maps what is really there, plans an architecture that can carry the next feature,
builds the thinnest working path, then proves the result with tests and a design
audit. The work scales to the ask: one component, one flow, or a product other
people will maintain.

Two halves, held together. Reverse engineering and engineering decide what to
build and how it holds up. Anti-AI-Slop design decides what it looks like, and
refuses the defaults a model reaches for when nobody is looking. What can be
measured is measured by a small command line, so "it looks fine" is not an
available answer.

## Features

**Reverse Engineering & Engineering**

- Product analysis: what it does, for whom, and what it costs to change.
- Feature and workflow mapping: screens, states, and the path between them.
- Architecture planning: data first, constraints in the database.
- Frontend and backend implementation: the smallest path that works.
- Testing and validation: reproduce, fix, then prove it.

**Anti-AI-Slop Design**

- UI/UX analysis: hierarchy, density, and where the eye lands.
- Design direction: a written brief per project, not a mood board.
- Design system: type and colour as roles, before any hex value.
- Visual hierarchy: one dominant element per section.
- Accessibility: contrast measured, keyboard reachable, reduced motion honoured.
- Design audit: fifteen weighted signals, scored and gated.

## Installation

Three commands, Python 3.9 or newer, no pip and no root:

```bash
git clone https://github.com/AomiXplorer/aomi.git
cd aomi
python3 install.py
```

`install.py` puts the `aomi` command on your PATH and asks once whether to copy
the skill into your agent. It runs the command it wrote and prints the version, so
you can see the install worked:

```bash
aomi --version
```

If you already have pipx, one line instead:

```bash
pipx install git+https://github.com/AomiXplorer/aomi.git && aomi install
```

Nothing installed at all: `python3 -m aomi` from this folder runs the same
commands. Every agent path, the manual route, updating and removing:
[docs/installation.md](docs/installation.md).

## Usage

Place the skill where your agent reads it, then start a project:

```bash
aomi install              # detects your agent, offers the list, verifies the copy
aomi init                 # project name, depth, artifacts
```

Depth decides how much is written: a sketch leaves nothing behind, a build leaves
four artifacts, a product leaves six. Then measure what you built:

```bash
aomi audit ./src                    # Slop Gate signals in markup and styles
aomi contrast aomi/tokens.json      # WCAG ratios for declared text pairs
aomi parity aomi/features.csv       # weighted feature completion
aomi doctor                         # links, assets and licence of a skill tree
```

```
Aomi design audit   .../shop/src

  files scanned   2
  issues found    2   critical 1, warning 1, info 0
  score           65/100
  status          BLOCKED

  SG01  w3  violet-indigo accent with no brand basis                  critical
        styles.css: #7c3aed
        fix: use your own brand colour, or move the accent off violet-indigo

  SG08  w2  hype lexicon                                               warning
        index.html:2: supercharge
        fix: replace the claim with the concrete outcome, or delete it

  Blocked. Fix the weight-3 and weight-4 findings first: those are the
  ones a reader notices without being told.
```

Each gate exits 1 when it fails and 2 when the request is wrong, so
`aomi audit ./src && git commit` works without a wrapper. Configuration is
optional: `aomi config` writes it, `aomi config --check` validates it, and
without it the defaults still hold.

More detail, kept out of this page: [commands and exit codes](docs/cli.md),
[method and phases](docs/workflow.md), [architecture and
structure](docs/architecture.md), [engineering](docs/engineering.md),
[design](docs/design.md).

## Supported Agents

One adapter per agent, because the folder each one reads is different.

| Agent | Skill folder | Status |
| --- | --- | --- |
| Claude Code | `.claude/skills/aomi` | documented, verified |
| OpenCode | `.opencode/skills/aomi` | documented, verified |
| Cursor | `.cursor/skills/aomi` | documented, verified |
| Windsurf / Devin Local | `.windsurf/skills/aomi` | documented, verified |
| Any skill-aware agent | `.agents/skills/aomi` | folder convention, verified |
| GitHub Copilot | `.github/skills/aomi` | built from docs, not yet run in a session |
| Codex | `.codex/skills/aomi` | built from docs, not yet run in a session |

`aomi agents --docs` prints each path with the page it came from, and
`aomi install --dir PATH` covers an agent that is not in this list.
Details: [docs/compatibility.md](docs/compatibility.md).

## License & Credits

Source-available under the [Aomi Personal Use License v1.0](LICENSE): free for
personal use, commercial use needs written permission, and the attribution stays.
It is not an OSI open-source license.

Written and maintained by Aomi ([@AomiXplorer](https://github.com/AomiXplorer)).
Code, prose and images are original; the reference points and the licence audit
are named in [docs/provenance.md](docs/provenance.md).
