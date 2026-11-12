# Colour

Colour is a role system, not a mood. Decide the roles, derive the values, check
the pairs, then stop.

## Roles

| role | how many | what it is for |
| --- | --- | --- |
| ground | 1 (+1 dark) | the page background |
| surface | 1–2 | panels, cards, inputs that sit above the ground |
| ink | 2–3 | primary text, secondary text, disabled text |
| line | 1–2 | borders and dividers, one for structure, one for emphasis |
| brand | 1 | the product's identity; used for the primary action and almost nothing else |
| accent | 0–1 | optional second signal for selection or highlight |
| semantic | 4 | success, warning, danger, info, each with a ground tint |

Nine roles is a complete system. If you need a twelfth, you have a component
problem, not a colour problem.

## Distribution before shade

Decide how much of the screen each role occupies before you decide which hex:
roughly 60% ground and neutrals, 30% supporting surfaces and ink, 10% brand and
semantic. A page where the brand colour covers a third of the screen cannot use
it to signal the one action that matters.

## Building the ramps

1. Pick the brand hue and one neutral temperature that agrees with it (warm
   neutrals under a warm hue, cool under a cool one).
2. Generate 7–9 steps per ramp, not 3. Disabled, hover, and focus need
   neighbours that exist.
3. Name ramps by role and step (`--ink-1`, `--surface-2`), never by colour word
   (`--grey-200`), so a theme can change without renaming every use.
4. Keep semantics separate from the brand ramp even when they share a hue.

## Contrast is a gate, not a guideline

| content | minimum |
| --- | --- |
| body text | 4.5:1 |
| large text (≥24px, or ≥19px bold) | 3:1 |
| icons and non-text UI that carry meaning | 3:1 |
| focus ring against its neighbours | 3:1 |
| purely decorative lines | not required |

Run `python3 scripts/aomi.py contrast aomi/tokens.json` and let it fail the
build. Text on tinted surfaces is where contrast quietly dies: a 12% tint of the
brand behind 16px grey text is a common and invisible failure.

## Dark mode

Dark mode is a second palette, not an inverted one.

- Raise surfaces as they come forward (lighter = closer), the reverse of light
  mode's shadow logic.
- Reduce saturation. A brand colour that works on white will vibrate on
  near-black.
- Re-check every pair. Contrast that passes in light mode routinely fails in
  dark, and the reverse.
- Never use pure black as ground and pure white as ink: the glare is worse than
  the contrast gain.

## Colour should not be the only carrier

Every state shown by colour also needs a shape, a label, an icon or a position.
Around 8% of men have a form of colour vision deficiency; a red dot next to a
green dot is a state only for the people who can see both.

## Anti-patterns that survive review

- Brand gradient behind a text block, reducing contrast unpredictably.
- A "dark accent" used for text on a coloured ground.
- The same hue for a semantic state and the brand, so an error looks like a CTA.
- Opacity-based text colour (`text-black/60`) that fails on one of the two grounds.
- Tinted borders on tinted surfaces with no line role.
