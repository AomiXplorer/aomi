# Handoff

> Filled by Sign. This is the document someone reads when they inherit the work,
> so it is written for them and not for the person who wrote it.

## What changed

<!-- One paragraph a user of the product would understand. -->

## Preflight results

Paste the real output, not a summary of it.

```text
$ python3 scripts/aomi.py doctor
$ python3 scripts/aomi.py audit .
$ python3 scripts/aomi.py parity aomi/features.csv
$ python3 scripts/aomi.py contrast aomi/tokens.json
$ <test command>
$ <build command>
```

## Accepted gaps

<!-- Features from features.csv not done, with the reason and who accepted it.
     An empty section here is a claim that nothing is missing. -->

| feature | status | why | accepted by |
| --- | --- | --- | --- |
|  |  |  |  |

## Not tested

<!-- Named honestly. An implied test is a liability. -->

## How to run it

<!-- The three commands a new maintainer needs, and the environment variables. -->

## Where to look first when it breaks

<!-- The three places failures show up: logs, the boundary, the state. -->

## Rollback

<!-- Previous build, schema reversibility, who can call it. Decide now, not
     during an incident. -->

## The go / no-go call

- [ ] every must-have done or accepted above
- [ ] tests and audits re-run after the last fix
- [ ] no secrets, placeholders, or dead links
- [ ] a person with authority said go

Decision:
Date:
