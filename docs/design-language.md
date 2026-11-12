# Aomi's design language

The visual identity of the project itself. Short on purpose: an identity with
twenty rules is a style guide nobody reads.

## The mark

Two circles that overlap, drawn in one weight, with a single dot where they meet.

The circles are the two intelligences: engineering and design. The dot is the
decision that belongs to both: the interface that constrains the schema, the
schema that limits the interface. It is drawn, not illustrated, and it survives
at 24px without a container.

The mark is a single SVG in `assets/logo.svg`, and the raster version in
`assets/logo.png` places it on a paper-coloured tile so it stays legible in both
GitHub themes.

## Palette

| role | value | used for |
| --- | --- | --- |
| paper | `#F6F1EA` | ground of every asset |
| ink | `#33303A` | the mark's rings, all headlines |
| rosewood | `#A2606E` | the overlap in the mark, the design lane in diagrams |
| gold | `#C9A46A` | one accent, never a fill: the dot, the threads between lanes |
| hairline | `#DFD3C8` | rules and dividers |
| muted | `#6E6570` | secondary text inside assets |

Six values. The project does not use a gradient, a glow, a drop shadow or a
second accent, which is the point: an identity made of six quiet values is
harder to mistake for someone else's than one made of effects.

## Type

A serif for the project's own voice, used only for display; a neutral sans for
labels and small text inside assets.

- Display in the assets: Noto Serif, one weight. The wordmark is set with slight
  positive tracking because it is short and sits alone.
- Labels in the diagrams: Noto Sans at 12 to 13px with wide tracking, uppercase.
  They name a column; they never carry a sentence.
- Body in the documentation: whatever the host renders. Aomi does not ship a
  stylesheet for a README it does not control.

The text inside `assets/hero.png` and `assets/workflow.png` is composed in SVG
and rasterised, never drawn by an image model, so the spelling is exact and the
files can be rebuilt byte for byte with `scripts/build_assets.py`.

## Composition

- Assets are laid out on an implied 8px grid with a wide left margin.
- One dominant element per asset. The hero's is the wordmark; the diagram's is
  the matrix of phases.
- The artwork sits in one panel and is allowed to bleed off the right edge. The
  typography is left-aligned against it, which is the asymmetry the composition
  needs to avoid reading as a template.
- A single hairline separates the two halves. One rule, never a box around
  everything.

## Voice

The documentation is in English, direct, and written to be disagreed with. The
README is in Indonesian, casual, and allowed to have a tone of voice.

Rules that apply to both:

- Say what a thing does, then why, in that order.
- No hype vocabulary. If a sentence would survive on a landing page it is
  probably empty.
- Numbers are measured or marked as examples. Never invented.
- Admit the limits in the same paragraph as the claim, not in a footnote.

## What this identity refuses

- Purple, indigo and violet: not because they are bad, but because they are the
  averaged default and Aomi cannot use a default it asks others to avoid.
- A gradient behind text, a glowing card, a floating blob.
- An emoji standing in for an icon.
- The same radius on every surface, which reads as a library nobody configured.
- A four-column footer of links that do not exist.

## Rebuilding the assets

```bash
python3 scripts/build_assets.py
```

Requires `rsvg-convert` on PATH. Pillow is optional; without it the PNGs are
larger but identical. The script prints the size of each file so a change that
doubles the README's weight is visible in the build output rather than in a
review.
