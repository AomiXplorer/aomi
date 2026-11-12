# Installing Aomi

Two steps: install the command, then let it copy the skill into your agent. About
a minute, no dependencies, Python 3.9 or newer.

## 1. Install the command

### The route that needs nothing but Python: `install.py`

Clone, then run the installer that ships with the repository. It needs no pip, no
virtualenv, no root and no network:

```bash
git clone https://github.com/AomiXplorer/aomi.git
cd aomi
python3 install.py
```

It asks one question (set up the command, copy the skill into an agent, or both),
then:

* copies the package to `~/.local/share/aomi` (honours `XDG_DATA_HOME`);
* writes a launcher to `~/.local/bin/aomi`;
* runs that launcher once and prints the version it got back, so you can see it
  works before you trust it.

If `~/.local/bin` is not on your PATH, it prints the exact line to add for your
shell. It never edits your shell profile for you.

```bash
aomi --version      # aomi 1.1.0
```

Non-interactive, for a script or a CI image:

```bash
python3 install.py --yes                       # the command only
python3 install.py --yes --skill --agent cursor  # command and skill
python3 install.py --uninstall --yes           # remove the command again
```

The folder the installer needs and the folder your agent reads are different
things, which is why there are two halves. `--skill` alone does the second one
without touching `~/.local`.

### If you already have pipx

That is one line fewer, and it keeps `aomi` in its own environment:

```bash
pipx install git+https://github.com/AomiXplorer/aomi.git
aomi --version
```

If `aomi: command not found` appears, run `pipx ensurepath` and open a new shell.
`pipx upgrade aomi` updates it later.

### If you would rather install nothing at all

The checkout runs itself. Use `python3 -m aomi` wherever `aomi` is written below:

```bash
git clone https://github.com/AomiXplorer/aomi.git
cd aomi
python3 -m aomi --version
python3 -m aomi install          # still copies the skill into your agent
```

Nothing is installed, and nothing outside the folders you name is touched. This is
also the one route that needs no launcher at all, so it works in a container where
`$HOME` is read-only.

## 2. Copy the skill into your agent

```bash
aomi install
```

It lists the agents it knows, marks the ones it detected in this project or your
home directory, and asks which to use. One question, then it prints the exact path
it wrote and verifies it.

```
Aomi installer

  detected here:
    Claude Code  (/home/nana/project/.claude)

  select your agent:
    [1] * Claude Code
    [2]   OpenCode
    [3]   Cursor
    ...
```

Non-interactive, for a script or a container:

```bash
aomi install --agent claude
aomi install --agent cursor --global
aomi install --dir ~/.config/my-agent/skills/aomi
```

`aomi install --list` shows every adapter, both paths and what is already installed.

## Where each agent reads skills

Where an agent's own documentation names a skill folder, Aomi uses it. Paths are
relative to the project unless marked global.

| agent | project | global | status |
| --- | --- | --- | --- |
| Claude Code | `.claude/skills/aomi` | `~/.claude/skills/aomi` | documented |
| OpenCode | `.opencode/skills/aomi` | `~/.config/opencode/skills/aomi` | documented |
| Cursor | `.cursor/skills/aomi` | `~/.cursor/skills/aomi` | documented |
| Windsurf / Devin Local | `.windsurf/skills/aomi` | `~/.config/devin/skills/aomi` | documented |
| GitHub Copilot | `.github/skills/aomi` | not documented | documented, not run here |
| Codex | `.codex/skills/aomi` | `~/.codex/skills/aomi` | documented, not run here |
| any skill-aware agent | `.agents/skills/aomi` | `~/.agents/skills/aomi` | documented |

"Documented" means the path comes from that agent's own documentation and the
folder layout was checked. "Documented, not run here" means the path was taken from
the documentation but Aomi was not exercised inside a session of that agent, so it
may differ on your version. Nothing is claimed beyond that.

Readings differ in small ways, and the adapters keep them apart rather than
pretending one folder serves everyone:

- **Claude Code** loads project and personal skills from `.claude/skills/<name>/`.
- **OpenCode** treats a directory containing `SKILL.md` as one skill, and also reads
  `.claude/skills` and `.agents/skills`.
- **Cursor** requires the folder name to match the frontmatter `name`, which it does.
- **Windsurf** still reads `.windsurf/skills`; newer builds also read `.devin/skills`
  and `.agents/skills`.
- **Copilot** and **Codex** are project scoped in the documentation seen so far.

## Manual install

For an agent with no adapter, or a folder Aomi does not write to:

1. `aomi install --dir /some/empty/folder` copies the runtime tree there, or copy it
   yourself from a checkout.
2. Copy the whole folder into the place your agent reads skills: `SKILL.md`,
   `core/`, `engineering/`, `design/`, `references/`, `templates/`, `docs/`,
   `assets/`, `LICENSE`, `README.md`.
3. Do **not** copy `tests/`, `aomi/`, `scripts/`, `pyproject.toml`, `setup.py` or
   `.git`: they are for developing Aomi, not for using it.
4. Names matter: the folder must be named `aomi` and contain `SKILL.md` at its root.
5. Check the copy with `aomi doctor --root /that/folder`. Zero errors means every
   relative link inside the skill still resolves, so its routing table works.

If your agent reads a single instruction file instead of a skills folder, point that
file at `SKILL.md` rather than pasting the whole skill into it. One source, one copy.

## Updating

Update the command the way you installed it, then refresh the copies it placed:

```bash
# installed with install.py: in the clone you already have
git pull && python3 install.py

# installed with pipx
pipx upgrade aomi

# either way, then:
aomi update                       # rewrite every installed copy of the skill
```

Running `install.py` again copies over the previous install, removes files the new
version no longer ships, and prints the version it wrote, so you can see what you
got. `aomi update` then refreshes the skill folders.

Both halves matter: the installer refreshes the command, `aomi update` writes that
version's skill files over your installed copies and prunes anything it no longer
ships. `aomi update` finds them by reading `SKILL.md`, so it works from any
directory, with no state file to go stale. It finds them by reading `SKILL.md`, so it works after an upgrade, from any
directory, with no state file to go stale.

## Removing

```bash
aomi uninstall              # the skill copies; asks first, refuses foreign folders
python3 install.py --uninstall --yes   # the command, if installed with install.py
pipx uninstall aomi         # the command, if installed with pipx
```

`install.py --uninstall` removes only what that installer wrote: the launcher and
the data folder. It leaves your shell profile alone, and it will not touch a
launcher that came from pipx.

## Termux and other small terminals

No build step, no compiled dependency, no colour unless the terminal claims a real
one, and no full-screen redraw. Everything is text and standard-library Python.
On Termux the launcher goes to `$PREFIX/bin`, which is already on `PATH`, so there
is no profile line to add and no `~/.local/bin` to remember. The launcher is a
Python file whose first line names the interpreter that ran `install.py`, not a
`#!/bin/sh` script, because Termux has no `/bin`.

`python3 install.py` and `python3 -m aomi` both work from a clone when pipx is not
available, and `AOMI_NONINTERACTIVE=1` makes every command take its answers from
flags.

## When something looks wrong

- `python3: can't open file 'install.py': No such file or directory` means the clone
  is older than the installer. Run `git pull` in it; `install.py` landed after the
  first releases. `git log --oneline -1` shows which commit you are on.
- `cannot find the skill files` means the package and its bundled skill tree are out
  of step. Reinstall the way you installed: `python3 install.py` from a fresh clone,
  or `pipx install --force git+https://github.com/AomiXplorer/aomi.git`.
- `refused: ... is not an Aomi skill` means that folder holds something else. Point
  `--dir` somewhere empty, or add `--force` if you really mean to replace it.
- An agent does not see the skill after install: confirm the path with
  `aomi agents`, then check the agent's own documentation for the folder it reads,
  and use `--dir` if it differs.
