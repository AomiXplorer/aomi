# Design

Design asks one question: will this be understood? This document is the map of how
Aomi answers it. The instructions live in [`design/`](../design/).

## Direction comes first

Before a colour or a font, four sentences go into `decisions.md`:

1. Who reads this, on what device, in what light, how often.
2. The one thing that must be obvious in the first second.
3. What it should feel like, written as a comparison with another product or
   place, never as an adjective.
4. What it is deliberately not.

If a visual choice cannot be traced back to those four sentences, it is
decoration.

## Typography

Six roles with a size and a job each: display, heading, subheading, body, label,
caption. One modular scale, at most three weights, body measure between 60 and 75
characters, line height that tightens as size grows, tabular figures anywhere
numbers align in a column.

The text face carries the argument and is optimised for the smallest size it will
be read at. The display face appears once or twice per screen; five times and its
character becomes noise. See [typography.md](../design/typography.md) and the
pairings in [type-pairings.md](../references/type-pairings.md).

## Colour

Nine roles, chosen before any hex value: ground, surface, surface raised, ink,
ink muted, line, brand, brand on, and the semantic four. Distribution is 60/30/10
and the brand is almost always inside the ten.

Contrast is a gate, not an opinion: `aomi contrast` measures
declared text pairs against 4.5:1 for body and 3:1 for large text and UI. Dark
mode is a second palette, not an inversion. See
[color.md](../design/color.md) and the six measured starting points in
[palettes.md](../references/palettes.md).

## Layout

One dominant element per area. Rhythm that varies on purpose, so the eye can tell
a section break from a paragraph. One place per page that deliberately leaves the
grid. Containers sized to content rather than to a single max-width repeated
everywhere.

The responsive plan is decided per element, not per breakpoint: what reflows, and
what becomes something else entirely. See [layout.md](../design/layout.md).

## Components

Inventory before code. A product usually needs eight to twelve components, not
forty. Each one lists its states: default, hover, focus, active, disabled,
loading, error, empty, and whatever the data can produce.

Radius and elevation are scales that state hierarchy, not one value applied to
everything. See [components.md](../design/components.md).

## Interaction

Motion is feedback or it is noise. Each animation names which it is, with a
budget: 100 to 150ms for a response to input, 200 to 300ms for an entrance,
faster to leave. Transform and opacity only. `prefers-reduced-motion` is
mandatory, and its absence is an accessibility failure rather than a preference.
See [interaction.md](../design/interaction.md).

## Accessibility

Gates that can be answered with evidence: keyboard reachable and in a sensible
order, visible focus, 200 percent zoom without horizontal scroll, images with
alternative text, colour never the only signal, form errors announced, and a
screen reader pass over the primary journey. See
[accessibility.md](../design/accessibility.md).

## The Slop Gate

Three tests, in order, because they catch different failures.

| test | question | catches |
| --- | --- | --- |
| **Swap Test** | swap in a competitor's logo. Does anything contradict it? | interchangeable work |
| **Derivation Test** | can each visible choice be traced to the product? | taste presented as reasoning |
| **Signal Sweep** | what does the tool measure? | the specific tells |

The sweep reports fifteen weighted signals over markup and styles: a violet or
indigo accent with no brand basis, one typeface for every role, a single radius,
decorative gradient or glow, emoji as icons, cards that scale on hover, motion
with no reduced-motion path, hype vocabulary, a centred hero with a symmetric
action pair, an unlabelled input, a repeated three-column grid, an image without
alt text, a data state the interface has no branch for, proof that cannot be
traced, and uniform section rhythm.

```
score = 100 - (7 × the weight of every signal that fired)
```

85 or above is clear, 70 and above passes with notes, below 70 is blocked. A
signal can be waived, but only with one of five reasons: `brand`, `content`,
`accessibility`, `hardware`, `legacy`. Text contrast is measured separately by
`contrast`, because guessing which colour pairs meet in a stylesheet produces
false alarms.

Weights, waivers and the full definitions are in
[slop-gate.md](../design/slop-gate.md). The weights there are read by a test that
fails when the code disagrees with the document.

## Design tested like code

- A fixture page exercises every type role, every colour pair, every component
  state. The audit runs against it.
- Screenshots of key screens are compared deliberately after a change that touches
  tokens, not eyeballed.
- The audit score goes into `proof.md` as a result, with the signals that fired.
