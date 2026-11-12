# The Aomi loop

Seven phases. Each one produces an artifact, and the next one reads it. Nothing
is skipped; small work simply spends fewer minutes in each.

The seven phases carry the ten steps of a full engagement like this:

| step | phase |
| --- | --- |
| 1. understand the request | Frame |
| 2. analyze the product | Read |
| 3. research requirements | Read |
| 4. plan the architecture | Decide |
| 5. define the design direction | Decide |
| 6. build the implementation | Make |
| 7. run functional tests | Prove |
| 8. run design audits | Prove |
| 9. refine | Polish |
| 10. final quality verification | Sign |

Steps 4 and 5 deliberately share a phase. Architecture constrains the interface
(what can be shown, how fast, in what state) and the interface constrains the
architecture (what must be stored, what must be instant). Deciding them apart
produces two documents that argue with each other in week three.

---

## Frame

Turn the request into a brief someone else could build from.

- One paragraph: the product, the user, the job.
- What is explicitly out of scope, named so it cannot creep back.
- A depth level (see `depth.md`).
- What "done" will be checked against, written before the work makes it
  convenient.

Ask at most three questions, and only ones whose answers change the plan. Propose
an answer with each question so the user can say "yes" instead of writing an
essay.

Leaves: `aomi/brief.md`.

## Read

Build the picture of the product and the ground it stands on.

- If an existing app is the reference: inventory its screens, the states of each
  screen, the flows, and the data it implies. See `engineering/recon.md`.
- If it is greenfield: the jobs to be done, the vocabulary the users actually
  use, and the three screens that carry the product.
- Note the constraints: stack, hosting, money, existing brand, legal.

Leaves: `aomi/map.md`, `aomi/features.csv`.

## Decide

One document, two halves that must agree.

- Engineering: data shape, boundaries, auth, failure modes, what will be
  measured.
- Design: direction, type, colour, layout strategy, component strategy, motion.
- Each choice carries a reason and the alternative that lost.

If a design decision changes the data model, that is a finding, not an
annoyance. Write it down and resolve it here.

Leaves: `aomi/decisions.md`.

## Make

Build in the order that fails earliest.

1. The thinnest path that proves the product works end to end, ugly is fine.
2. The shell and navigation.
3. Each screen, with its states: empty, loading, error, denied, mobile.
4. Polish passes only after the path is complete.

Write every line fresh. If the reference is another product, copy what it does,
never how it is written, worded, coloured or drawn.

Leaves: the implementation, plus `aomi/build-log.md` for deviations from
`decisions.md`.

## Prove

Two questions, answered with evidence rather than confidence.

- Does it work? Paths tested, cases that should fail, and what happens when the
  network, the input or the permission is wrong.
- Does it hold up to a designer's eye and a keyboard? The Slop Gate
  (`design/slop-gate.md`), plus the accessibility checks in
  `design/accessibility.md`.

Both results go in one file. A passing test suite does not excuse a failing
audit, and a beautiful screen does not excuse a broken path.

Leaves: `aomi/proof.md`.

## Polish

Fix in order of consequence: broken behaviour, then unreadable interface, then
taste. Each fix gets a line saying what decision would have prevented it, so the
same class of bug does not return in the next feature.

Leaves: the refined build, and a short list in `aomi/proof.md`.

## Sign

Final verification, then a go / no-go call that is written, not implied.

- Every must-have feature in `features.csv` is done or explicitly dropped.
- Tests and audits re-run after the last fix, not before it.
- No secrets, no placeholder copy, no dead links, no unexplained asset.

Leaves: `aomi/handoff.md`.

---

## What adapts

The loop does not change with scale; the minutes per phase do.

- A one-line question never enters the loop. Answer it.
- A component or a single page: Frame and Decide collapse into a few sentences
  in the reply, then Make, Prove, Sign.
- A product: all seven phases, all artifacts, no shortcuts on Prove.

Depth is declared in `brief.md` so that everyone, later, can see how much
process was promised.
