# Workflow

Seven phases. Each one ends with something written down, and the next phase reads
it. That is the whole method.

```
Frame → Read → Decide → Make → Prove → Polish → Sign
```

## The phases

| phase | the job | leaves |
| --- | --- | --- |
| **Frame** | what is being built, for whom, at what depth, and what is out of scope | `brief.md` |
| **Read** | the existing product, if there is one: screens, states, flows, implied data | `map.md`, `features.csv` |
| **Decide** | architecture and design direction in one record, each with the option that lost | `decisions.md` |
| **Make** | the thinnest path end to end, then the shell, then every screen with all of its states | the build |
| **Prove** | functional tests and the design audit, both, with output pasted | `proof.md` |
| **Polish** | fix by impact, and record which decision would have prevented the flaw | the fixes |
| **Sign** | final verification and an explicit go or no-go | `handoff.md` |

Two phases are skipped more often than they should be. **Read** is skipped when
the product already exists, which is exactly when it matters. **Prove** is
skipped when the work looks finished, which is when it is easiest to be wrong.

## The ten steps, mapped

The long form of this workflow is ten steps. They map onto the seven phases
without a separate process:

| ten steps | phase |
| --- | --- |
| understand, analyse | Frame |
| research | Read |
| plan | Decide |
| design direction | Decide |
| build | Make |
| test, audit | Prove |
| refine | Polish |
| verify | Sign |

The compression exists because "research" and "plan" are one act when the plan is
written as decisions with reasons, and because design direction is a decision,
not a step that happens after architecture.

## Depth

A workflow that cannot shrink will be abandoned on small tasks. Depth is declared
in `brief.md` and held to.

| level | for | artifacts | typical size |
| --- | --- | --- | --- |
| **Sketch** | one question, one component, one fix | none | minutes |
| **Build** | one feature, one page, one flow | `brief`, `decisions`, `proof` | hours |
| **Product** | several surfaces, real users, someone else maintaining it | all six | days |

Raising the level mid task is allowed and has to be said out loud. Quietly running
the full process on a small task is the most common way this workflow wastes
someone's afternoon.

The signals that the level was chosen too low: a second screen appears, two people
start editing the same rule, or a decision gets re-argued in review because nobody
wrote it down.

## What "done" means at each phase

- Frame is done when a stranger could read `brief.md` and say what will exist and
  what will not.
- Read is done when every state of every screen has been seen, including the ones
  that require an error to reach.
- Decide is done when every entry has a reason and a rejected alternative.
- Make is done when the thinnest path works with real data shape and no
  placeholder logic.
- Prove is done when the suite and the audit both have output in `proof.md`, and
  the untested parts are named there too.
- Polish is done when the remaining findings are either fixed or written down as
  accepted.
- Sign is done when a person with authority said go. Not when the build is green.

## Running it

The commands behind the measurable phases:

```bash
aomi init .
aomi audit .
aomi contrast aomi/tokens.json
aomi parity aomi/features.csv
aomi doctor
```

The phase instructions themselves live in `core/workflow.md` (the loop and the
phase list), `core/depth.md` (choosing a level), and the two folders that hold the
work: `engineering/` and `design/`.
