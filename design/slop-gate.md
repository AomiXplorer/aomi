# The Slop Gate

Most "avoid AI design" advice is a ban list, and a ban list fails in both
directions: it forbids a purple that was the client's brand, and it permits a
grey interface that means nothing. Aomi runs three tests instead. Two are
judgment, one is measurement, and every flag can be argued with in writing.

The target is not "unusual". It is **specific**: a screen that could only belong
to this product.

---

## Test 1: The Swap Test (run before building)

Write the product name on the page. Now write a competitor's name over it. Read
it again.

If nothing contradicts, the design is interchangeable and the work is not done.
Nothing needs to be unusual; one thing needs to be *only true here*: the
vocabulary, the numbers shown, the order of the fields, the shape of the empty
state, the thing the user came to do being physically largest.

Run this at Decide, not at the end. It is cheap before there is a layout and
expensive after.

## Test 2: The Derivation Test (run per visible decision)

For each of: colour, typeface, spacing rhythm, layout skeleton, component
structure, motion: there must be a sentence in `aomi/decisions.md` explaining
where it came from, and a line naming what lost.

Four legitimate derivations:

- **From the product's job**: dense data wants density and numbers, a reading
  product wants measure and quiet.
- **From the audience's environment**: clinic daylight, warehouse gloves, a
  phone at 60 cm, a laptop at 4 pm with the sun behind it.
- **From existing brand material**: a logo, a legacy colour, a print system.
  Inheriting a brand is not slop even when the brand is purple.
- **From an accessibility need**: a larger base size, a stronger focus ring, a
  shape that does not rely on hue.

"Because it looks modern" is not a derivation. Neither is "it is the default".

## Test 3: The Signal Sweep (measured)

Fifteen surface signals. Each has a weight, and each can be waived with a reason.
The weights are not moral judgments; they are how strongly the signal predicts
"the interface was averaged rather than designed".

### Visual

| id | signal | weight |
| --- | --- | --- |
| SG01 | accent colour sits in the violet–indigo band (`#6366f1`–`#a855f7` family) with no brand basis | 3 |
| SG02 | display and body are the same neutral grotesque, so nothing signals rank | 2 |
| SG03 | one radius value applied to every surface, so nothing signals scale | 1 |
| SG04 | decorative gradient, glow or blur on a surface that carries no information | 2 |
| SG05 | emoji standing in for an icon | 3 |
| SG06 | repeated cards lift or scale on hover, moving their neighbours | 1 |
| SG12 | the same three-column card grid appears three or more times | 1 |
| SG16 | every section uses the same vertical padding and the same container width | 1 |

### Language

| id | signal | weight |
| --- | --- | --- |
| SG08 | hype lexicon: supercharge, unlock, seamless, effortless, elevate, revolutionise, next-generation | 2 |
| SG09 | centred hero with two symmetric calls to action as the only structure | 2 |
| SG13 | an image without alternative text | 2 |
| SG15 | proof that cannot be traced: invented percentages, testimonial names, logo walls | 4 |

### Function

| id | signal | weight |
| --- | --- | --- |
| SG07 | animation or transition with no `prefers-reduced-motion` counterpart | 3 |
| SG11 | a form control with no programmatic label | 3 |
| SG14 | a state that exists in the data but not in the interface (empty, error, denied) | 3 |

### Scoring

```
penalty = sum of weights of the signals that fired and were not waived
score   = max(0, 100 - 7 * penalty)
```

| score | verdict |
| --- | --- |
| 85–100 | clear. Ship it. |
| 70–84 | pass with notes. Fix what costs nothing; justify the rest in the decision file. |
| below 70 | blocked. Do not call the work finished. |

Text contrast has no sweep signal on purpose: guessing which colour pairs meet in
a stylesheet produces false alarms. It is measured properly, pair by pair, by
`aomi contrast aomi/tokens.json`, which must pass before Sign.

A weight-4 signal alone drops a perfect page to 72. That is intentional: invented
proof is the one thing that cannot be justified.

### Waiving a signal

A waiver is a line in `aomi/overrides.json`:

```json
[
  { "signal": "SG01", "reason": "brand",
    "note": "The logo and print system use #6D4AA6; the interface inherits it." }
]
```

Allowed reasons: `brand`, `content`, `accessibility`, `hardware`, `legacy`. A
waiver with any other reason is not counted, and the report says so. The point is
not to forbid the colour; it is to force the sentence that says why.

---

## What the sweep cannot see

It cannot tell whether the hierarchy is right, whether the words sound like a
person, whether the screen is calm, or whether the product's one important action
is the most obvious thing on the page. Those go in `proof.md` as sentences
someone could disagree with, for example:

> The primary action is the only filled button on the screen; every secondary
> action is a text link, so the eye has one landing point at any scroll depth.

That sentence can be checked. "Looks clean" cannot.

## When the design still feels generic after passing

The cause is almost never a visual signal. It is one of these:

1. **The content is generic.** Placeholder names, round numbers, lorem states.
   Fix the data before the layout.
2. **The hierarchy is flat.** Three things are equally loud, so nothing speaks.
   Pick one, make it 1.5× its neighbours.
3. **The structure is the default structure.** Hero, three features, testimonial,
   pricing. Reorder around what the user actually does first.
4. **The voice is borrowed.** Hype words, passive constructions, no first person.
   Write as the product's owner, not as its brochure.

Fix in that order. Restyling a page with generic content produces a better
dressed generic page.
