# Depth: choosing how much process to spend

Aomi refuses to run a product-sized process on a component-sized task. Declare
the level in `brief.md` before starting, and change it out loud if the work
turns out bigger than it looked.

## Sketch

*For: a question, one component, a copy fix, a single colour or spacing change,
a bug with an obvious cause.*

- Phases: Frame (two sentences) → Make → Prove (one check) → Sign.
- Artifacts: none required. The reasoning lives in the reply.
- Still mandatory: the Swap Test on anything visual, and a check that the change
  did not break the surrounding state.
- Budget: minutes, not hours. If it needs a decision record, it was not a Sketch.

## Build

*For: a feature, a page, a flow, a small app, a redesign of one surface.*

- Phases: all seven, compressed.
- Artifacts: `brief.md`, `decisions.md`, `proof.md`. A `map.md` only when the
  reference product is complex enough that you would otherwise re-inspect it
  three times.
- Swappable: recon. Note what you observed inline instead of building a full
  screen inventory.
- Budget: a session.

## Product

*For: a whole product, several surfaces, anything that will be maintained by
someone else, anything going to real users.*

- Phases: all seven, in full, in order.
- Artifacts: all of them, kept current. `features.csv` is the contract for scope.
- Not swappable: recon, prove, sign. These are where product-scale mistakes hide.
- Additions: a decision review after Decide, before Make, where the user agrees
  to the direction before code exists.
- Budget: multiple sessions. Carry state in the artifacts, not in memory.

---

## Signals that you chose too shallow

- You are writing architecture inside the component library.
- You have rewritten the same block three times for reasons you cannot name.
- The user keeps correcting the same misunderstanding.
- You cannot say what you will check to know you are done.

Move up a level, say so, and rebuild the brief.

## Signals that you chose too deep

- The artifacts are longer than the code.
- You are inventing screens that the request did not ask for.
- Recon is gathering detail that no decision will use.
- You are writing a process document to explain the process.

Move down a level. Delete the artifact that has no reader.
