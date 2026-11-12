# Engineering

Engineering asks one question: will this hold? This document is the map of how
Aomi answers it. The instructions themselves live in [`engineering/`](../engineering/).

## The seven areas

| area | the question it forces | file |
| --- | --- | --- |
| Recon | what already exists, screen by screen and state by state | [recon.md](../engineering/recon.md) |
| Architecture | what shape is the data, and where are the boundaries | [architecture.md](../engineering/architecture.md) |
| Frontend | what state can this view be in, and does it have a branch for it | [frontend.md](../engineering/frontend.md) |
| Backend | which rules must stay true when the client lies | [backend.md](../engineering/backend.md) |
| Quality | how do we reproduce it before changing it | [quality.md](../engineering/quality.md) |
| Testing | what would make this test able to fail | [testing.md](../engineering/testing.md) |
| Ship | what is the rollback, decided before the deploy | [ship.md](../engineering/ship.md) |

## Recon

For a product that already exists, public pages, docs, the app store listing and
your own account are the sources. Screens get stable ids (`S01`), flows get ids
and a step count (`F01`, four steps, six fields), and the data model is inferred
and marked as inferred.

The boundary is deliberate. Human-paced reading of what the owner can already see,
no source code, no private endpoints, no scraping behind a login, no third-party
client credentials reused. Recon produces a map, not a copy: the rebuild is
written fresh against the map.

## Architecture

Order of decisions: data, boundaries, paths, failure modes, operability. Not the
reverse. A schema chosen after the screens exist will be a schema that describes
the screens.

Two rules that survive contact with production:

- Constraints live in the database. Application code loses races; a unique index
  does not.
- Anything that can be retried is idempotent: a natural key, a request key, or a
  state machine that cannot go backwards.

## Frontend

View state is one discriminated value, not five booleans. The named states are
`idle`, `loading`, `ready`, `empty`, `error`, `denied`, `partial`, and a view that
can be in `denied` and has no branch for it will sit on a spinner the first time a
real user reaches it.

Build order inside a screen: shell, thinnest path with real data shape, then every
state, then interaction.

## Backend

Authorisation is per record and lives in one function used by every path.
Scattered owner checks are how data leaks. Migrations are files, the environment
is validated at boot, secrets stay server side, and account deletion states what
is deleted, what is retained, and for how long.

## Quality

Reproduce, bisect the surface, read the actual value, fix the cause once, then
write the test that would have caught it. The anti-pattern list is short and
specific: changing several things between attempts, fixing by adding a guard, and
closing a bug because it stopped happening.

## Testing

| layer | use it for | cost |
| --- | --- | --- |
| unit | pure rules: pricing, dates, validation, permissions | cheapest |
| integration | the boundary that actually breaks: database, third party, auth | medium |
| end to end | the three or four journeys that carry the product | expensive |
| manual pass | keyboard, zoom, screen reader, reduced motion | necessary |

A suite of only unit tests stays green while the product is broken. A suite of
only end to end tests gets skipped.

## Ship

Preflight output pasted, not summarised. Environment diffed against production.
A rollback written before the deploy. An explicit go from the person who owns the
consequence. Then verify three things after deploying: the page loads, the primary
action works, an error path says something useful.

## What goes in `proof.md`

Functional result with the command and duration, the manual pass, what was **not**
tested and why, the audit score with the signals that fired, and the accessibility
passes. An untested area named honestly is engineering. An untested area implied
to be covered is a liability.
