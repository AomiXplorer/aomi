# Recon: understanding an existing product

Recon turns a product you can only observe into a map you can build from. It is
reading a product, the way a person reads it, and writing down what you saw.

## Boundaries, before any observation

Recon is lawful observation, not extraction. These are not negotiable:

- **Your own account, or public material.** Never another person's login, never a
  shared credential, never trying to get past a paywall or a permission.
- **Human pace.** Read pages a person would read. No crawling, no looping over a
  site, no bulk download.
- **No private surface.** Do not read or save source bundles, decompiled
  binaries, or intercepted network traffic in order to copy behaviour. Public
  documentation and public API references are fine.
- **Check the terms.** If the product's terms forbid using an account to build a
  competing product, say so, and work from public material only.
- **Screenshots are reference, never assets.** They inform structure. They do not
  ship, and neither does anything cropped out of them.
- **Rebuild what it does, not what it owns.** Features and flows, yes. Code,
  copy, logos, icons, illustrations, fonts under licence, colours as a signature:
  no.

If the answer to "may I do this" is unclear, do the public half and ask.

## Sources, in order of value

| source | what it yields |
| --- | --- |
| help centre and docs | the fullest feature list, including settings nobody demos |
| pricing page | what the business considers valuable, by what it gates |
| changelog | what the team is investing in, and how fast |
| app store listing | screenshots of the key screens, plus the pitch language |
| public walkthrough videos | real sequences of clicks, including mistakes |
| marketing site | the core loop, described by the people who sell it |
| your own account | every state that matters, driven at your own pace |
| public API reference | the data model, almost for free |

A source without a URL is an anecdote. Record the URL.

## The map

One file, `aomi/map.md`, with four sections.

### Screens

```
| id | screen | how you reach it | purpose | notable components | states seen |
| S01 | Today | default route | see today's appointments | day header, row list, status chips | empty, filled, overdue |
```

States matter as much as screens: empty, loading, partial, error, permission
denied, mobile. A state you did not record is a state you will not build.

### Flows

```
F01 Book an appointment
  S03 service -> S04 slot -> S05 details -> S06 confirmation
  happy path: 4 steps, 3 fields, no account
  edges: no slots this week, slot taken mid-form, different time zone
```

Count the steps and the fields. Those numbers are the bar your version has to
clear; anything longer is a regression you chose.

### Data, inferred

From the fields on screen, name the entities and their relationships, and mark
what is certain versus guessed. This feeds the architecture, so wrong guesses here
are expensive.

### Scope

What you will rebuild, what you will deliberately not rebuild, and why. Networks
and marketplaces usually belong to the company, not the product: rebuild the
feature, skip the network.

## The feature matrix

`aomi/features.csv`, one row per capability:

```csv
area,feature,priority,reference,clone,notes
booking,Public page with open slots,must,yes,no,
booking,Time zone detection,must,yes,no,
team,Round-robin across members,could,yes,no,out of scope v1
```

`priority` is `must`, `should` or `could`. `clone` moves from `no` to `partial` to
`yes`. Tools read this file, so keep it exact: `aomi.py parity` scores it, and
`must` items left undone block shipping.

## The judgement

At the end of recon, write two paragraphs:

1. What this product is genuinely good at, in one specific sentence. Not
   "polished"; the actual thing.
2. The one place it fails its users: a step that costs too much, a state that is
   handled badly, a concept the copy never explains.

The second paragraph is where your version earns the right to exist. Do not
invent it; observe it, in reviews, in help threads, in your own use.
