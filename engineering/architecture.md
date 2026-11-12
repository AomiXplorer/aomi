# Architecture

Architecture is the set of decisions that are expensive to reverse. Spend the
effort there and be deliberately boring everywhere else.

## Sequence

1. **Data first.** Entities, their fields, their relationships, their lifecycle.
   A screen is easy to change; a table with the wrong shape is not.
2. **Boundaries.** Where does trust change? Server, client, third party. Each
   boundary is a place where input must be validated again.
3. **Paths.** The three or four journeys the product exists for, drawn as
   request → state → response.
4. **Failure modes.** For each path: what if the network dies, the user
   double-submits, the third party is down, the permission is missing.
5. **Operability.** How you will know it is broken, and how you would roll back.

## Choosing the stack

Prefer what the maintainer already knows, then what is managed, then what is
boring. Novelty is a cost with an interest rate.

| layer | default | when to deviate |
| --- | --- | --- |
| app | the platform's own framework | only if it cannot express the product |
| data | relational, one database | a second store needs a written reason |
| auth | managed provider | custom only when the product sells identity |
| jobs | platform scheduler | a queue only when work must survive deploys |
| files | managed storage with signed URLs | self-hosted only for residency reasons |
| payments | hosted checkout | custom form only if the flow cannot be hosted |

One database, one deploy target, no services split before there is a team to
operate them.

## Data modelling

- Name tables for the thing, not the screen. `appointment`, not `bookingPage`.
- Every table: primary key, created timestamp, and the foreign keys that make it
  meaningful. No polymorphic fields to avoid a decision.
- Enumerations live in one place, and the allowed values are written down.
- Money is stored in minor units with an explicit currency. Never a float.
- Time is stored in UTC, rendered in the user's zone, and the zone is stored when
  it changes the meaning of the record.
- Deletion is a decision: hard delete, soft delete with a retention window, or
  anonymise. Pick one per entity and write it in the decision file.
- Uniqueness constraints belong in the database, not only in application code.
  The double-booking bug is always a missing constraint.

## API design

- Resources named as nouns; verbs only for state transitions that are not CRUD.
- One response shape across the API: data, pagination, error, never three
  conventions.
- Errors are typed and carry a message a human can act on, plus a code a client
  can branch on.
- Anything that mutates and can be retried takes an idempotency key.
- Pagination from the first version. Retrofitting it breaks clients.
- Version only what is public. Internally, change it and ship both ends.

## Authentication and authorisation

- Authenticate at the edge, authorise at the record. "Is this user allowed to do
  this to this row" is one function, used everywhere.
- Roles are stored, not inferred from the UI.
- Sessions: http-only, secure, same-site cookies, with an expiry that is stated.
- Invitations, transfers and account deletion are designed as flows, not as
  admin database edits.
- Deletion actually deletes: state what is removed, what is retained for legal
  reasons, and for how long.

## Recording it

`aomi/decisions.md`, one entry per decision:

```markdown
### D3: one appointment row per slot, enforced in the database
Reason: double booking is the failure users complain about most, and application
checks lose races.
Rejected: re-check before insert (loses under concurrency).
Cost: a unique index on (provider_id, starts_at) and a friendly 409 path.
```

Every entry: the choice, the reason, the alternative that lost, and the cost. A
decision with no cost was not a decision.
