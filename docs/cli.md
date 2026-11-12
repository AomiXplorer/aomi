# The command line

One command, ten subcommands, standard-library Python only. This page is the
reference; the [README](../README.md) has the three lines most people need.

```bash
pipx install git+https://github.com/AomiXplorer/aomi.git
aomi --help
```

From a checkout with no install, `python3 -m aomi` takes the same arguments.

## How output behaves

Quiet by default: one line per fact, no spinners, no progress bars, no emoji.
Colour is used only when the stream is a terminal and nothing says otherwise, so
a log file, a pipe, Termux and a CI job all get clean text.

```
NO_COLOR=1              no colour, ever (the conventional opt out)
FORCE_COLOR=1           colour even through a pipe
CLICOLOR=0              same as NO_COLOR
TERM=dumb               plain text
AOMI_NONINTERACTIVE=1   never ask a question, use the flags instead
```

## Exit codes

| code | meaning |
| --- | --- |
| 0 | the command did what it said |
| 1 | a gate failed: the audit is blocked, a contrast pair fails, a `must` is missing, a verification found a problem |
| 2 | the request was wrong: unknown flag, missing path, unknown agent, a folder that is not Aomi |
| 130 | interrupted with Ctrl-C |

Every gate command returns 1 on failure, so `aomi audit ./src && git commit` works
without a wrapper.

## install

Copy the skill into the folder an agent reads.

```
aomi install                     ask which agent, then copy
aomi install --agent cursor      no questions
aomi install --list              every adapter, its paths, and what is detected here
aomi install --global            the user-wide path, not this project
aomi install --dir PATH          an exact folder, for an agent not in the list
aomi install --dry-run           show the plan, write nothing
aomi install --force             replace a folder that is not an Aomi skill
```

The installer detects agents from markers in the project and the home directory,
prints the exact target path, copies the runtime files only, then verifies what it
wrote: required files present, frontmatter readable, every relative link resolving
inside the new folder. Nothing else is written, no state file, no manifest.

Running it twice updates in place. Files this version no longer ships are pruned
from the folders Aomi manages, so an upgrade cannot leave a stale page behind.

`tests/`, `.git/`, the packaging files and the build scripts are never copied.

## update

Refresh installed copies to the version of the command you are running.

```
aomi update                 every Aomi folder found for the adapters
aomi update --agent claude  just that one
aomi update --dir PATH      just that folder
```

Run `pipx upgrade aomi` first if you want the newer release; `aomi update` copies
whatever version the command itself is. An edited `SKILL.md` is restored, so keep
your own notes outside the skill folder.

## uninstall

```
aomi uninstall              remove every Aomi folder found, after asking
aomi uninstall --yes        no question, for a script
aomi uninstall --agent cursor
aomi uninstall --dir PATH
```

It refuses any folder that is not an Aomi skill and says so. The `aomi` command
itself is removed with `pipx uninstall aomi`.

## agents

```
aomi agents          adapters, install paths, what is detected here, what is installed
aomi agents --docs   add the documentation each path came from
```

An adapter marked `documented, not run here` has a path taken from that agent's own
docs but was not exercised inside a session of that agent. Use `--dir` if the path
differs on your machine.

## init

Scaffold the artifacts a project actually uses.

```
aomi init                ask three questions: name, depth, write the files
aomi init .              same, in the current folder
aomi init ./my-project   create the folder
aomi init --yes          no questions, the full set, safe for CI
aomi init --depth build --name "buku kas" --yes
aomi init --no-artifacts --yes
```

Depth decides what is written, because a placeholder file nobody reads is clutter:

| depth | files |
| --- | --- |
| `sketch` | none. One fix does not earn a paper trail |
| `build` | `brief.md`, `decisions.md`, `proof.md`, `features.csv` |
| `product` | the above plus `map.md` and `handoff.md` |

`--yes` with no `--depth` writes the five files it has always written, so existing
scripts keep working. An existing file is never overwritten.

## audit

Sweep a project for the Slop Gate signals.

```
aomi audit               the current folder
aomi audit ./src         one folder
aomi audit --json        machine-readable, same score
aomi audit --overrides my-waivers.json
```

The report leads with counts and a status, then each finding with its file, its
evidence, and a suggested fix. Weights are documented in
[design/slop-gate.md](../design/slop-gate.md); the score is
`100 - 7 × the weight of every signal that is not waived`.

Exit code 1 when the score is under 70.

## contrast

WCAG ratios for the pairs your design declares.

```
aomi contrast aomi/tokens.json
aomi contrast aomi/tokens.json --json
```

Body text needs 4.5:1, large text and interface parts 3:1. Exit code 1 if any pair
fails. A `tokens.json` with no `pairs` list is paired against the ground role.

## parity

Weighted completion from a feature contract.

```
aomi parity aomi/features.csv
```

`must` counts 3, `should` 2, `could` 1; `clone` is `yes` 1.0, `partial` 0.5,
`no` 0. Rows whose `reference` is `no` are not scored. Exit code 1 while any `must`
is unfinished.

## doctor

Check a skill tree: frontmatter, every relative link, the licence, the assets the
README needs, that the Python files parse.

```
aomi doctor                     the current folder
aomi doctor --root .claude/skills/aomi   an installed copy
aomi doctor --json
```

This is the command to run after installing somewhere new: it proves the copy is
whole. Exit code 1 on any error.

## config

The three optional files, without reading a spec.

```
aomi config              the wizard, on a terminal
aomi config --show       what is active
aomi config --check      validate, and say what to fix
```

The wizard can write `tokens.json` from three colours and check the contrast
immediately, add a waiver for a Slop Gate signal with an allowed reason, and add a
row to `features.csv`.

No configuration is required. A project with no `aomi/` folder still audits,
initialises and ships; these files only sharpen the answers.
