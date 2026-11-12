# Layout

Layout answers three questions: what is biggest, what stays put, and where does
the pattern break.

## The skeleton

Write the primary screen's skeleton in words before markup:

```
Frame: full viewport
├ Top bar: product, current record, primary action (fixed, 56px)
├ Rail: navigation by day (fixed, 240px, collapses under 900px)
└ Main: scrolls
  ├ Header block: oversized day count, then the note for the day
  ├ Row list: 72px rows, one line plus a status
  └ Detail: panel 480px, slides over main, never replaces it
```

If this cannot be written, the layout is being discovered by accident during
implementation, which is the most expensive way to discover it.

## One dominant element

Each region has exactly one element that wins: 1.5× the size, or the only filled
colour, or the only image. Everything else supports it. When two elements are
equally loud, the user reads neither.

## Rhythm, deliberately uneven

Repeating the same section anatomy is what makes a long page feel machine-made.
Vary at least two of: container width (narrow for prose, wide for grids, full for
one break), vertical padding (large at the top, tighter later), column structure
(two, four, asymmetric spans).

A page needs at least one moment that breaks its own grid on purpose, with a
reason: an oversized figure, a full-bleed image, a paragraph that starts in the
margin.

## Spacing

One 4px-based scale; the tokens actually used are usually six values. Grouping is
done with proximity, not with boxes: internal spacing smaller than external
spacing, always. If two things are related, they sit closer to each other than to
anything else.

```
--space-1: 4px;  --space-2: 8px;  --space-3: 12px;
--space-4: 16px; --space-6: 24px; --space-8: 32px;
--space-12: 48px; --space-16: 64px; --space-24: 96px;
```

## Responsive

Design the narrow case first, because it forces the priority order. Then:

- One breakpoint at the width where the layout genuinely stops working, not at a
  device name.
- Navigation collapse is a priority decision: what survives in the bar when the
  rail disappears.
- Tables become lists, not horizontal scrolls, unless comparison across columns
  is the job.
- Test at 320, 390, 768, 1024, 1440 and at 200% browser zoom. Zoom is the real
  accessibility breakpoint.
- Tap targets at least 44×44px with 8px between them.

## Density

Density follows the job. A screen consulted 200 times a day can carry 32px rows
and 12px labels; a screen read once needs air. State the choice. The common
failure is a data tool built at marketing density, where every row requires a
scroll.

## What a layout is not allowed to do

- Hide the primary action below the fold on a screen whose job is that action.
- Centre prose, except for a statement of one or two lines.
- Use the same 1200px container for a paragraph and a dashboard.
- Rely on hover for information that matters on touch.
- Break the reading order to achieve a visual effect: DOM order and visual order
  must agree.
