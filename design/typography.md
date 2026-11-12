# Typography

Type does most of the work of hierarchy. Get the roles and the scale right and
half of layout resolves itself.

## Roles, not fonts

Decide these six, in `decisions.md`, before choosing a family:

| role | typical size | job |
| --- | --- | --- |
| display | 32–72px | one per screen, carries the screen's single idea |
| section head | 20–28px | names a region; may be the same face as display |
| body | 15–17px | reading text; the size everything else is measured against |
| label | 12–14px | field names, table headers, metadata |
| value | 13–16px, tabular | numbers that must align in a column |
| caption | 12–13px, muted | secondary explanation, never the only place a fact lives |

If a screen has no display role, say so. A screen where everything is 16px is a
screen with no hierarchy, and no colour will fix that.

## The scale

One modular scale, three to five steps actually used. A ratio of 1.2 reads calm,
1.25 reads standard, 1.333 reads editorial. Fluid sizing between two breakpoints
is fine; a different scale per breakpoint is not.

```
--text-caption: 0.8125rem;   /* 13 */
--text-label:   0.875rem;    /* 14 */
--text-body:    1rem;        /* 16 */
--text-head:    1.25rem;     /* 20 */
--text-title:   1.5rem;      /* 24 */
--text-display: clamp(2rem, 4vw, 3.25rem);
```

## Weights

Three at most from one family: one for text, one for emphasis, one for display.
A fourth weight is always a mistake in the design, not in the font.

## Measure and leading

- Body measure: 60–75 characters. Below 45 the eye jumps; above 90 it loses the
  line. Enforce it with a width, not with manual breaks.
- Body leading: 1.5–1.65. Headings: 1.05–1.2. Labels: 1.2–1.4.
- Tracking: negative slightly on large display sizes, positive on small caps
  labels. Never track body text apart to fill a width.
- Alignment: left for prose, ever. Centred prose is for two-line statements and
  nothing longer.

## Pairing

One display face with character and one quiet text face is the reliable
combination. Two expressive faces compete; two quiet faces read as unfinished.

Choose the text face for the reading condition: high x-height and open counters
for dense screens and small sizes, a wider body for long prose, a narrower width
for tables. `references/type-pairings.md` has combinations with their
temperament and where they fail.

## Numbers

Any screen with figures in a column uses tabular figures for those figures. Mixing
proportional digits into a table is a defect the reader feels without naming.
Percentage, currency and duration formatting is a product decision: state it once
and use it everywhere.

## Loading and fallbacks

Serve the display face and the text face with a swap strategy and a matching
fallback metric, so a slow font does not reflow the page. Two families maximum
per page. If a family is unavailable at build time, substitute by metric (a
similar x-height and width), not by convenience.

## Signs the typography is wrong

- You are using size to fix spacing.
- Everything is the same weight, so emphasis is done with colour.
- The headline is smaller than the body's line length suggests.
- You need a fourth weight or a fifth size.
- Body text sits at 13px on a desktop to "fit more".
