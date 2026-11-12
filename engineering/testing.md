# Testing

A test earns its place by being able to fail. If you cannot describe the failure
it would catch, it is documentation of current behaviour, and it will happily
protect a bug.

## What to test, in order

1. **The rules of the product.** A slot cannot be booked twice. A guest cannot
   read another guest's record. Money adds up.
2. **The paths users take**, end to end, on the real surface.
3. **The states nobody clicks**: empty, error, denied, partial, long content.
4. **The boundaries**: validation, permissions, idempotency, time zones.
5. **Regression for every bug fixed**, written before the fix.

Skip: framework behaviour, trivial getters, and anything whose only assertion is
that the code did not change.

## Layers

| layer | use for | cost |
| --- | --- | --- |
| unit | pure rules: pricing, dates, validation, permissions | cheapest |
| integration | the boundary that fails in practice: database, third party, auth | medium |
| end to end | the three or four journeys that carry the product | expensive, so few |
| manual pass | keyboard, zoom, screen reader, reduced motion | necessary, cannot be automated |

A suite that is only unit tests will be green while the product is broken. A suite
that is only end to end will be slow and skipped.

## Writing the test

```python
def test_slot_cannot_be_booked_twice():
    # Arrange: the state that makes the rule meaningful
    slot = given_a_slot(starts_at="2026-03-04T09:00Z")
    first = book(slot, guest="a@example.test")

    # Act: the second attempt, exactly as a user would make it
    second = book(slot, guest="b@example.test")

    # Assert: the observable outcome, not the implementation
    assert first.succeeded
    assert second.code == "slot_taken"
    assert count_bookings(slot) == 1
```

Rules: one behaviour per test, a name that reads as a sentence, no assertion on
internals, and deterministic data. A test that fails one run in twenty will be
deleted within a month, and its bug will come back.

## Test data

Fixtures should be boring and explicit. Avoid shared factories that quietly grow
fields nobody reads: the test then asserts on a state the reader cannot see. Where
time matters, inject the clock. Where identity matters, create the two accounts
the test needs and no more.

## Evidence, not confidence

`aomi/proof.md` records what was run, not that things "look good":

```markdown
## Functional
- 24 tests, 24 passing, `pytest -q`, 2.1s
- Manual: booking as guest in a private window, slot taken mid-form returns 409
  and keeps the entered fields.
- Not tested: concurrent bookings under load (needs >=2 clients); refunds, no
  payment provider in test mode yet.

## Design and access
- aomi.py audit: 94/100, no signals fired
- Keyboard pass: full booking flow reachable, no trap
- 200% zoom: no horizontal scroll, table becomes a list
- Reduced motion: panels appear, do not slide
```

Name what was not tested. An untested area named honestly is engineering; an
untested area implied to be covered is a liability.

## Design tested like code

Design regressions happen the same way code regressions do: someone changes a
token and four screens quietly lose their hierarchy. So:

- Keep a fixture page that exercises the design system: every type role, every
  colour pair, every component state. Run the audit against it.
- Screenshot the key screens before and after a change that touches tokens, and
  compare them deliberately.
- Treat the Slop Gate score as a test result: it goes in `proof.md`, with the
  signals that fired and the waivers that were accepted.
