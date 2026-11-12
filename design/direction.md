# Design direction

Direction is decided once, in `decisions.md`, before any screen is built. It is
four sentences and three lists, not a mood board.

## The four sentences

1. **Who reads this, and where.** Device, distance, light, how much time they
   have, how often they have seen it before.
2. **What the screen must make obvious.** One thing. If everything is obvious,
   nothing is.
3. **What the product should feel like, in a comparison, not an adjective.**
   "A reference manual, not a brochure" beats "professional and modern".
4. **What it deliberately is not.** Naming the nearby wrong answer is the
   cheapest guard against drifting into it.

## The three lists

**Type.** One display face and one text face (or one family used at clearly
different weights and widths). Name the roles, not just the fonts: which size
carries the headline, which carries the body, which carries labels.

**Colour.** One brand hue, plus neutrals, plus semantic roles with fixed meanings
(success, warning, danger, info). Distribution before shade: how much of the
screen is neutral, how much is support, how much is accent. Typically 60/30/10.
Every text-on-surface pair is checked with `aomi.py contrast` before it is used.

**Structure.** The skeleton of the primary screen, in words: what sits at the
top, what is persistent, what scrolls, what is a panel versus a page. Then the
one place the pattern is broken on purpose, because a page that never breaks its
own grid reads as a template.

## Direction archetypes

Use these to disagree with, not to pick from. Most real products are a blend of
two, and the blend is where the specificity comes from.

| archetype | type | colour | structure | fits |
| --- | --- | --- | --- | --- |
| Reference | text face only, tight scale, generous measure | near-monochrome, one signal colour for state | sidebar of chapters, long body column | documentation, specs, catalogues |
| Instrument | narrow grotesque, tabular figures, small caps labels | dark neutral, two data hues, no accent decoration | persistent toolbar, dense table, detail as a panel | operations, finance, monitoring |
| Workshop | one display face with personality, plain text face | paper neutrals, one warm accent, nothing glossy | canvas in the middle, tools at the edges | creation tools, editors, planning |
| Shopfront | display face for headlines only, calm text face | warm neutral ground, one saturated brand colour used sparingly | image-led, asymmetric, wide margins | commerce, hospitality, portfolios |
| Terminal | mono for values, sans for prose, hard scale steps | high contrast, semantic colour only | split pane, log region, pinned controls | developer tools, logs, agents |
| Editorial | serif display, sans text, strong measure control | ink on paper, single accent | magazine grid with at least one full-bleed break | content, publishing, reports |

## Deciding when the brand already exists

If there is a logo, a print piece, a previous product or a colour the client
already uses, the direction starts there and earns specificity elsewhere:
structure, type scale, spacing, voice. Do not "modernise" an existing brand into
the current average; that is how two brands become one.

## Recording it

In `aomi/decisions.md`:

```markdown
## Design direction
Reader: a clinic receptionist, desktop, 8 hours a day, harsh daylight, has seen
this screen 200 times.
Must be obvious: today's appointments and what is unfinished.
Feels like: a paper daybook that has been used for years, not a dashboard.
Not: a marketing page, not a dark mode, not animated.

Type: [display face] for the day count and section heads; [text face] for rows
and forms. Scale 1.25 from 15px. Labels at 12px uppercase with 0.08em tracking.
Colour: [brand] as the only saturated hue, 5% of the screen. Neutrals from a
warm grey ramp. Semantic: green, amber, red, all contrast-checked.
Structure: persistent left rail of days, main column of rows, detail slides over
the column rather than replacing it. Breaks: the day count sits oversized in the
top-left corner, ignoring the grid.
```

If that paragraph is hard to write, the direction is not decided yet, and no
amount of building will decide it for you.
