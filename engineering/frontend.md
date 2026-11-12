# Frontend

The frontend's job: show the right state, cheaply, and never lie about what is
happening.

## Build order

1. Layout shell and tokens wired in, so every later screen inherits spacing,
   type and colour instead of inventing them.
2. The thinnest end-to-end path, with real data shape, fake data content.
3. Each screen, with all of its states.
4. Interaction and motion, last.

Screens built before the shell exists become five different design systems.

## State

Name every state a view can be in, in code, not in comments:

```
idle | loading | ready | empty | error | denied | partial
```

A view that can be in `denied` and has no branch for it will render a spinner
forever the first time a real user hits it. Every list has `empty`; every form
has `invalid`; every fetch has `error` with a retry that keeps the old data.

Model the state as a union or a discriminated value, not five booleans. Booleans
multiply into states that cannot happen and states that should but are missing.

## Components

- Pure presentational components take props and return markup. No fetching inside
  a button.
- One component per concept. If two components render a person's name differently,
  one is wrong.
- Variants are declared, not improvised with conditional class strings.
- Tokens only: no raw hex, no magic spacing. A missing value is a token to add.

## Data

- The server is the source of truth; local state is a cache with an owner and an
  invalidation rule.
- Every mutation either updates the cache precisely or invalidates it. "Refresh
  everything" is acceptable once, not as a pattern.
- Handle the three responses: success, validation failure, and transport failure.
  Most interfaces handle one.
- Debounce search, cancel stale requests, and ignore responses that arrive after
  a newer one.

## Forms

The part of an app people judge hardest and build last.

- Labels visible and associated; placeholders for examples, not names.
- Validate on blur and on submit; keep the values on failure.
- One message per field, next to the field, phrased as an instruction.
- Disable the submit button only when the action would be destructive; otherwise
  let it fail loudly with a reason.
- Announce success once, quietly, and move focus to the result.

## Performance

Measure before optimising; then the usual order applies.

- Ship less JavaScript before making JavaScript faster.
- Images: correct dimensions, modern format, lazy below the fold, explicit aspect
  ratio so nothing shifts.
- Fonts: two families, subset, swap, preloaded for the one that is used in the
  first viewport.
- Lists over 100 rows: paginate or virtualise, and test that find-in-page and
  screen readers still work.
- Budget, written down: first meaningful paint under 1.5s on a mid-range phone on
  4G, interaction under 100ms. Treat a budget as a test, not a hope.

## Before handing a screen over

- Every state reachable without editing the database.
- Keyboard only, and at 200% zoom.
- No console errors, no unused imports, no commented-out blocks.
- The screen looks deliberate at 320px wide, not merely unbroken.
