# Backend

The backend's job: keep the rules true even when the client is not.

## Rules that hold

- **Everything from the client is untrusted.** Validate on arrival, again at the
  boundary where it changes something, and never trust a role the client sent.
- **Authorisation is per record**, in one function used by every path. Scattered
  `if user.id === row.owner` checks are how data leaks.
- **Constraints live in the database.** Unique indexes, foreign keys, not-null.
  Application code loses races; the database does not.
- **Mutations are idempotent** when they can be retried: a key, a natural unique
  constraint, or a state machine that cannot go backwards.
- **Secrets stay server-side.** The client gets a token scoped to the operation,
  never a long-lived key. `.env` is never committed; `.env.example` lists every
  name with no values.
- **Logs are for operating, not for storing user data.** No tokens, no passwords,
  no full request bodies containing personal data.

## Schema work

- Migrations are files, committed, ordered, and run by a script. A schema change
  made by hand in a console is a change that will be missing in production.
- Every migration has a way back, or a stated reason why it cannot be reverted.
- Add nullable, backfill, then constrain. Never add a required column to a table
  with rows in one step.
- Indexes follow queries, not tables: the filter and sort in the actual request.

## API shape

```json
{ "data": { }, "page": { "cursor": "…", "has_more": true } }
{ "error": { "code": "slot_taken", "message": "That time was just booked.",
             "field": "starts_at" } }
```

- One convention for success, one for failure, across the whole surface.
- Error codes are stable; messages are for humans and may change.
- The API validates and reports every failing field, not the first one.
- Rate limits are per identity, stated, and return a retry hint.

## Auth flows that must exist

Sign up, verify, sign in, reset, refresh, sign out everywhere, invite, accept
invite, remove a member, delete an account. Each one is a flow with states, not a
button. Account deletion states what is deleted, what is retained, and for how
long.

## Jobs and integrations

- Every job records what it processed, so a retry does not repeat the effect.
- Third-party calls: timeout, retry with backoff and jitter, and a dead-letter
  path. Assume the provider will be slow and will occasionally return 200 with a
  broken body.
- Inbound webhooks verify their signature and tolerate replay.
- Use documented APIs with the account owner's own keys. Never call a third
  party's private endpoints, and never reuse another product's client credentials.

## Before shipping the backend

- Every endpoint: who may call it, what happens when they may not.
- Every table: how rows are deleted, and what happens to dependants.
- Every job: what happens if it runs twice, and if it never runs.
- Every secret: where it lives, who can read it, how it rotates.
