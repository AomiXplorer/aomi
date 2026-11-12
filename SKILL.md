---
name: aomi
description: >-
  A unified engineering and design skill for AI agents. Use it whenever work
  involves understanding a product, planning architecture, building or fixing
  frontend and backend code, designing an interface, choosing type and colour,
  auditing UI quality, testing, or shipping. Aomi refuses to build before it
  understands, decides architecture and visual direction together in one written
  record, proves the result with tests and a design audit, and blocks work that
  reads as generic. Trigger on: build, fix, refactor, design, redesign, review
  this UI, plan the database, clone this app's flow, audit, test, ship, or any
  request where code and interface quality both matter.
argument-hint: [what you are building or fixing]
metadata:
  version: 1.0.0
  author: Aomi
  license: AOMI-PUL-1.0
---

# Aomi

Two intelligences, one workflow. Engineering asks *will this hold*. Design asks
*will this be understood*. Aomi refuses to answer one without the other.

## Non-negotiables

1. **Say what you think is being built, and get a yes, before building.** One
   paragraph is cheaper than a rebuild.
2. **Architecture and design direction are decided together**, in one written
   record, each with a reason and the alternative that lost.
3. **Measure what can be measured.** Contrast, feature coverage, broken links and
   weights are tool answers, not opinions.
4. **Read only the files the task needs.** This skill is modular on purpose.
5. **Never call work finished while a `must` feature is undone, a test fails, or
   the Slop Gate blocks it.**

## Route the task first

Find the row, read those files, start. Do not read the whole skill.

| the task | read |
| --- | --- |
| new product, feature, or page | `core/workflow.md`, `core/depth.md`, then `design/direction.md` |
| understand an existing app or a competitor | `engineering/recon.md` |
| data model, API, auth, stack choice | `engineering/architecture.md`, `engineering/backend.md` |
| build or fix frontend | `engineering/frontend.md`, `design/components.md`, `design/layout.md` |
| choose type, colour, spacing | `design/typography.md`, `design/color.md`, `design/layout.md` |
| review or de-slop an interface | `design/slop-gate.md`, `design/accessibility.md` |
| motion, feedback, loading states | `design/interaction.md` |
| debug, refactor, performance | `engineering/quality.md` |
| tests, or "is it done" | `engineering/testing.md` |
| deploy, launch, domain, go/no-go | `engineering/ship.md` |
| which fonts and palettes fit a product | `references/type-pairings.md`, `references/palettes.md` |
| stack-specific notes | `references/stack-notes.md` |
| what this skill is made of, and its licence | `docs/provenance.md` |

When two rows apply, read the smaller set and say what you skipped.

## The loop

```
Frame -> Read -> Decide -> Make -> Prove -> Polish -> Sign
```

Each phase writes one artifact into `aomi/` in the project. `core/workflow.md`
has the detail and the mapping to a full ten-step engagement.

Declare a depth level in `brief.md` and hold to it:

- **Sketch**: a question, one component, one fix. No artifacts. Minutes.
- **Build**: a feature, a page, a flow. `brief.md`, `decisions.md`, `proof.md`.
- **Product**: several surfaces, real users, someone else maintaining it. All
  artifacts, all phases, recon and audit not optional.

Raising the level mid-task is allowed and should be said out loud. Quietly running
a full process on a small task is the most common way this skill wastes time.

## Artifacts

```
aomi/brief.md      what is being built, for whom, depth, out of scope, done-when
aomi/map.md        screens, states, flows, inferred data (recon only)
aomi/features.csv  the scope contract: area,feature,priority,reference,clone,notes
aomi/decisions.md  architecture + design direction, each with reason and rejected option
aomi/proof.md      what was tested, what passed, what was not tested, audit score
aomi/handoff.md    preflight results and the go / no-go call
```

Scaffold them with `python3 scripts/aomi.py init`. Keep them current, or delete
the one that has no reader.

## Tools

All standard-library Python. Run from the skill directory, pointing at the project.

```bash
python3 scripts/aomi.py init [dir]                 # scaffold aomi/ artifacts
python3 scripts/aomi.py audit <dir> [--json]       # Slop Gate signal sweep
python3 scripts/aomi.py contrast aomi/tokens.json  # WCAG ratios for text pairs
python3 scripts/aomi.py parity aomi/features.csv   # weighted completion score
python3 scripts/aomi.py doctor [--root .]          # structure, links, assets, provenance
```

`audit` reports measured signals and heuristic ones separately. Heuristic findings
are prompts for judgment, not verdicts.

## Putting numbers on judgement

The audit cannot tell whether the hierarchy is right or whether the words sound
like a person. For those, write a sentence someone could disagree with:

> The primary action is the only filled button on the screen, so the eye has one
> landing point at any scroll depth.

That goes in `proof.md`. "Looks clean" does not qualify.

## Working with other skills

If another skill, rule file or project convention already governs part of the
task, this skill governs the workflow and the quality gates, and the other
governs its own domain. Where they conflict on a measurement, the measurement
wins. Where they conflict on taste, the project's written design direction wins,
and the conflict goes in `decisions.md`.

## The one sentence

If a choice cannot be defended with a reason specific to this product, it is
decoration: cut it, or write the reason down.
