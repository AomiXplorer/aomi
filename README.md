<p align="center">
  <img src="assets/hero.png" alt="Aomi: a cream banner with the mark and the line understand first, build once, design on purpose">
</p>

<p align="center">
  <img src="assets/logo.png" width="72" alt="Aomi mark: two overlapping circles with a single dot where they meet">
</p>

<h1 align="center">Aomi</h1>

<p align="center"><strong>Understand first. Build once. Design on purpose.</strong></p>

<p align="center"><sub>a skill for AI agents · python 3.9+ · no dependencies · source-available</sub></p>

Aomi is a skill for AI agents that would rather understand the job than start
typing. It reads the task, opens only the few files that answer it, and keeps
engineering and design in the same conversation instead of two.

One method carries from a single component fix to a product other people will
maintain: frame the work, decide in writing, build the thinnest path, then prove
it with tests and a design audit. The parts that can be measured are measured by a
small command line, so "it looks fine" is not an available answer.

## Features

### Engineering

- Recon that maps an existing product screen by screen, within what you may see.
- Data-first architecture, with constraints in the database, not only in code.
- View state as one value, so empty, error and denied have somewhere to go.
- Authorisation in one place, migrations as files, secrets server side.
- Debugging that reproduces before it edits, and a test written for each fix.

### Design

- A written direction per project: reader, obligation, feel, and what it refuses.
- Type and colour chosen as roles with sizes, before any hex value.
- A Slop Gate: three tests and fifteen weighted signals, not a ban list.
- Contrast measured against WCAG by `aomi.py contrast`, never estimated.
- Motion with a time budget, and `prefers-reduced-motion` treated as required.

## Workflow

**Frame** → **Read** → **Decide** → **Make** → **Prove** → **Polish** → **Sign**

Each phase leaves one artifact and the next phase reads it. Depth is declared up
front, so a small fix does not quietly become a full engagement: **Sketch** for
one component or one question, **Build** for a feature or a flow, **Product** for
several surfaces and real users.

Phases, artifacts and the ten-step mapping: [docs/workflow.md](docs/workflow.md).

## Installation

```bash
git clone https://github.com/AomiXplorer/aomi.git
cd aomi
python3 scripts/aomi.py --version
```

Then put it where your agent looks for skills:

```bash
# agents that read .agents/skills/
git clone --depth 1 \
  https://github.com/AomiXplorer/aomi.git \
  .agents/skills/aomi
rm -rf .agents/skills/aomi/.git

# Claude Code
git clone --depth 1 \
  https://github.com/AomiXplorer/aomi.git \
  ~/.claude/skills/aomi
rm -rf ~/.claude/skills/aomi/.git
```

Copy the whole directory, not just `SKILL.md`: it refers to files beside it.
Python is only needed for the command line. The skill itself is Markdown.

## Usage

`init` writes `aomi/` with `brief.md`, `decisions.md`, `proof.md`,
`handoff.md` and `features.csv`. Then the audit, on an existing project:

```bash
$ python3 scripts/aomi.py audit ./src
SG01  w3  violet-indigo accent with no brand basis
    - landing.html: #a855f7
SG15  w4  proof that cannot be traced
    - landing.html: Trusted by 12,400

penalty 7  ->  score 51/100  ->  BLOCKED
```

One evidence line per signal here; the real output lists every hit.

Five commands: `init`, `audit`, `contrast`, `parity`, `doctor`. The four that grade
exit non-zero when they fail, so a pre-commit hook or a CI step needs no wrapper.
Every one of them takes `--json`.

```bash
$ python3 scripts/aomi.py contrast \
    aomi/tokens.json
pass    14.85    4.5  body on ground
FAIL     1.96    4.5  faint on ground

4 pairs, 1 failing
```

If an accent is genuinely the brand, say so rather than fight the score:

```json
[{ "signal": "SG01", "reason": "brand",
   "note": "Print and logo use #6D4AA6." }]
```

That goes in `aomi/overrides.json`. Only five reasons are accepted: `brand`,
`content`, `accessibility`, `hardware`, `legacy`.

## Compatibility

- **Tested:** an agent whose skill loader reads `.agents/skills/`. Installed,
  loaded by its runner, and the command line executed from the skill folder.
- **Format-compatible, not run here:** Claude Code, Cursor, Windsurf, Copilot,
  Codex. Each reads Markdown skill or rule files, which Aomi satisfies. Nothing
  beyond that is claimed.
- **Anything else:** the frontmatter is the only hard requirement.

The full table, the caveats and the wrapper for script runners are in
[docs/compatibility.md](docs/compatibility.md).

## Documentation

- [Architecture](docs/architecture.md): how the skill is split, and why
- [Workflow](docs/workflow.md): seven phases, three depths, the artifacts
- [Engineering](docs/engineering.md): recon, architecture, frontend, backend,
  quality, testing, ship
- [Design](docs/design.md): direction, type, colour, layout, the Slop Gate
- [Compatibility](docs/compatibility.md): hosts tested, hosts assumed, and what
  that means
- [Provenance](docs/provenance.md): the origin of every part, checked by a command
- [Design language](docs/design-language.md): the project's own mark, palette and
  voice

## License

Aomi ships under the **Aomi Personal Use License v1.0**. Read it, learn from it, use
it for personal work. Commercial use needs written permission, redistribution and
resale do not happen without it, and attribution stays. It is source-available, not
an OSI open-source license, and the text says plainly where it is not legal advice.

The terms are in [LICENSE](LICENSE).

## Credits

Aomi was written from scratch after studying two public skill collections: one
about rebuilding an existing app, one about anti-slop interface work. They shaped
how the problem was framed and nothing else. No file, paragraph, asset or line of
code from either appears here, and [docs/provenance.md](docs/provenance.md) records
file by file, and `aomi.py doctor` checks the trail.

Hero artwork was generated with an image model and composed with typography in SVG;
the mark and the workflow diagram were drawn as SVG in `assets/`. Text inside every
asset is rendered rather than painted, so the spelling is exact.

Maintained by Aomi ([@AomiXplorer](https://github.com/AomiXplorer)). Bug reports and
questions are welcome in the issue tracker.
