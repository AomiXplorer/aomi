<p align="center">
  <img src="assets/hero.png" alt="Aomi banner: the mark and wordmark on cream, beside a framed panel of soft abstract artwork">
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

Two routes. The first needs nothing but Python 3.9+, which is why it comes first.

```bash
git clone https://github.com/AomiXplorer/aomi.git
cd aomi
python3 install.py
```

That puts the `aomi` command in `~/.local/bin` and asks once whether to copy the
skill into your agent. No pip, no virtualenv, no root. If the folder is not on your
PATH, it prints the one line to add.

Already have pipx? One line instead:

```bash
pipx install git+https://github.com/AomiXplorer/aomi.git && aomi install
```

`aomi install` detects your agent, offers a short list, copies the runtime files and
verifies the copy. `--agent claude`, `--global` and `--dir PATH` skip the questions.
To undo the command: `python3 install.py --uninstall`.

Termux, Windows, each agent's folder and the manual route:
[docs/installation.md](docs/installation.md).

## Usage

Start a project, then measure it.

```bash
aomi init            # three questions: name, depth, artifacts
aomi audit ./src
```

```
Aomi design audit   ./src

  files scanned   24
  issues found    2   critical 0, warning 1, info 1
  score           86/100
  status          CLEAR
```

`init` writes only what the depth needs: nothing for a sketch, four files for a
build, six for a product. `audit` names the file, the evidence and a fix for each
finding, and exits non-zero under 70.

Also `contrast` for WCAG ratios, `parity` for feature coverage, `doctor` for the
skill's own structure, `config` for brand colours and waivers. Flags, exit codes and
scripted use: [docs/cli.md](docs/cli.md).

## Compatibility

- **Documented and verified by the installer:** Claude Code, OpenCode, Cursor,
  Windsurf. `aomi install --list` prints each path and where it came from.
- **Documented, not run inside that agent:** GitHub Copilot, Codex. The path follows
  their documentation; it may differ on your version. `--dir` covers the gap.
- **Tested end to end:** an agent whose loader reads `.agents/skills/`.
- **Anything else:** the frontmatter is the only hard requirement.

Full table and caveats: [docs/compatibility.md](docs/compatibility.md).

## Documentation

- [Installation](docs/installation.md): pipx, adapters, manual copy, Termux
- [CLI](docs/cli.md): every command, flag and exit code
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
