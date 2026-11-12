# Quality

Quality work is two habits: reproduce before fixing, and measure before
optimising. Everything else is style.

## Debugging

1. **Reproduce it.** Smallest input that shows the bug, written down. A bug you
   cannot reproduce is a bug you cannot confirm you fixed.
2. **Bisect the surface.** Which layer could produce this symptom: data, state,
   render, network, permission, time zone. Cut the space in half, repeatedly.
3. **Read the actual value.** Print or inspect the real input at the boundary you
   suspect. The bug is almost always a value that differs from the assumption.
4. **Fix the cause once.** If the fix is a special case in three places, the cause
   is upstream of all three.
5. **Write the test that would have caught it**, then fix. That test is the
   receipt.

Anti-patterns: changing several things between attempts, fixing by adding a
guard, closing a bug because it stopped happening.

## Reading code you did not write

- Entry points first: routes, handlers, event subscriptions.
- Then the data: what shape moves through the system.
- Then one path end to end, out loud.
- Only then the internals of the module you need to change.

Do not refactor a system you cannot yet describe.

## The review checklist

Before calling code done:

- [ ] Names say what the thing is, not how it is made.
- [ ] No dead code, no commented blocks, no debug output, no `TODO` without a date.
- [ ] Error paths exist and return something a user can act on.
- [ ] Nothing is duplicated that would drift: three copies of a rule is a bug
      waiting for its fourth.
- [ ] Boundaries validate; internals may assume.
- [ ] The diff does one thing. A diff that also renames things hides its own bug.
- [ ] Tests cover the behaviour that could break, not the lines that were easy.

## Performance

Only after measuring, and only in this order:

1. Remove work: fewer round trips, fewer renders, less data.
2. Cache the work that repeats, with an explicit invalidation.
3. Parallelise what is independent.
4. Optimise the code that remains, with a profiler open.

A speed-up with no measurement before and after is a change of mood.

## Refactor triggers

Refactor when one of these is true, not because the code looks old:

- The same change has been made in three places.
- A test cannot be written without building the world.
- A new requirement needs a concept the code does not have.
- A bug was caused twice by the same shape.

Say which trigger, then refactor in a separate commit from the behaviour change.

## Documentation

Comment the reason, never the mechanics. If a line needs a comment to explain
what it does, rename something. Decisions, trade-offs and non-obvious constraints
are the only comments worth keeping, and they belong next to the code or in
`aomi/decisions.md`.
