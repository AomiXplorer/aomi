# Ship

Shipping is a checklist and a decision, and the decision is the user's.

## The preflight

Run all of it, paste the output into `aomi/handoff.md`. A skipped line is a line
you do not know.

```bash
python3 scripts/aomi.py doctor                  # structure, links, frontmatter, assets
python3 scripts/aomi.py audit .                 # design signals, no blockers
python3 scripts/aomi.py parity aomi/features.csv # must-haves complete
python3 scripts/aomi.py contrast aomi/tokens.json # text pairs pass
<your test command> -q                          # functional suite green
<your build command>                            # production build passes
```

Then the manual pass: the primary journey on a real phone, on a slow connection,
keyboard only on the desktop, 200% zoom, and one look in dark mode.

## Environment

- `.env.example` lists every variable with a comment and no value. Diff it against
  production: a missing name is an outage with a clear cause.
- Every secret in production is different from every secret in staging.
- Nothing reads a development default in production. Fail loudly on a missing
  variable instead of falling back to localhost.
- The production database is migrated by the same script that migrated test, run
  against a backup you have verified restores.

## Going live

1. State what changes for users, in one sentence.
2. Deploy to a preview, verify the journey there, not only locally.
3. Confirm the rollback exists and has a time: previous build, previous schema.
4. Get an explicit go. Never infer it from silence.
5. Deploy, then verify the three things that matter: the page loads, the primary
   action works, an error path reports something useful.
6. Watch for the first hour: errors, latency, and the one metric the feature was
   supposed to move.

## Rollback

Decide before the deploy, not during the incident:

- Previous build, immediately available.
- Schema changes that can be reverted, and the ones that cannot.
- Data written by the new version: still readable by the old one?
- Who is allowed to call it, and how they are reached.

A deploy without a written rollback is a bet, not a release.

## After the first week

- Read the error logs before reading the analytics.
- Compare the metric that motivated the feature with the metric now.
- Keep the list of things users did that the interface did not anticipate. That
  list is the next version's brief.

## What not to do

- Do not announce a deployment before verifying it.
- Do not paste credentials into a chat, a log, a screenshot or a template.
- Do not deploy a rebrand of someone else's product. Identity is the owner's own:
  name, mark, palette, voice, and the copy in every state.
- Do not leave test data, seed accounts or placeholder copy in a production
  surface.
