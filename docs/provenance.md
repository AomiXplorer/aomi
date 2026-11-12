# Provenance

Aomi claims to be an independent implementation. This document exists so the
claim can be checked instead of trusted.

## Method

The project was written under a clean-room discipline:

1. Both reference collections were read for **what they do**: the sequence of
   work they impose on an agent, the kinds of gates they add, and the problem
   each is trying to solve.
2. What they **express** was not carried over: no file, paragraph, heading
   structure, table, prompt, example, dataset, script, asset or name.
3. Every file here was written for Aomi, from Aomi's own philosophy, then tested.
4. Where a component could not be written independently, it was left out rather
   than adapted. Nothing is included because copying it would have been quicker.

The line: **a method is not the same thing as its expression.** A phased
workflow, the idea of scoring feature parity, and the idea of auditing an
interface for generic patterns are methods. The words, structures, weights and
files that express them in a particular project are not. Aomi reuses no
expressive material, and does not reuse the upstream method wholesale either:
the phases, the scoring model, the artifact set, the waivers and the command line
were designed here.

## Upstream licence audit

| source | licence as published | material used here | notice owed |
| --- | --- | --- | --- |
| Replica skill collection | MIT | none | none |
| Anti-AI-UI skill collection | MIT | none | none |

Both are permissive licences that would have allowed reuse with attribution.
They are irrelevant to this repository because none of their material is present.
The audit confirms no notice is owed; it does not excuse one that would be.

Third-party material Aomi itself relies on:

| item | licence | used for | shipped? |
| --- | --- | --- | --- |
| Python standard library | PSF licence | the command line depends on nothing else | no, it is the user's interpreter |
| `rsvg-convert` (librsvg) | LGPL-2.1 | rasterising the SVG sources in `assets/` | no, build-time tool |
| Noto Serif, Noto Sans | SIL Open Font License 1.1 | the text baked into `assets/hero.png` and `assets/workflow.png` | no font file is included |

No font file, icon set, library or dataset is redistributed here. That is why
there is nothing to attribute beyond the README's credit note, which is courtesy
rather than obligation.

## Component origin audit

| path | origin |
| --- | --- |
| `SKILL.md` | written for Aomi |
| `core/philosophy.md` | written for Aomi |
| `core/workflow.md` | written for Aomi; seven phases designed here |
| `core/depth.md` | written for Aomi |
| `engineering/` (7 files) | written for Aomi |
| `design/` (8 files) | written for Aomi |
| `references/type-pairings.md` | written for Aomi; font names are facts about third-party typefaces |
| `references/palettes.md` | written for Aomi; hex values chosen here and measured with Aomi's own tool |
| `references/stack-notes.md` | written for Aomi |
| `templates/` (6 files) | written for Aomi |
| `scripts/aomi.py` | written for Aomi |
| `scripts/build_assets.py` | written for Aomi |
| `tests/` (suite and fixtures) | written for Aomi |
| `assets/logo.svg`, `assets/workflow.svg` | designed for Aomi |
| `assets/hero.png` | artwork generated with an image model from an Aomi-authored art direction, composed with Aomi typography |
| `assets/logo.png`, `assets/workflow.png` | rasterised from the SVG sources above |
| `assets/artwork-seed.png` | the unmodified artwork used in the hero, kept so the build is reproducible |
| `docs/` | written for Aomi |
| `README.md`, `LICENSE` | written for Aomi |

Nothing above is marked as derived, because nothing is.

## How the claim is checked

```bash
python3 scripts/aomi.py doctor
```

The doctor command scans every instruction, code and documentation file for file
names that would betray a copied component, for example a script that only exists
upstream, and reports any hit. Two files are allowed to name an upstream project:
this one and the README credit line, because naming an influence is attribution,
not reuse.

The same command verifies the `SKILL.md` frontmatter, that every relative link
resolves, that the licence is the Aomi licence, and that every asset the README
references exists.

## What was deliberately left out

- Upstream fixtures, example projects and benchmark data: not needed, and not
  transferable without copying.
- Upstream reference tables and their wording: Aomi's references are shorter and
  written to be argued with.
- Upstream scoring formulas: Aomi's Slop Gate uses a different signal set,
  different weights, a documented waiver mechanism, and a separate measurement
  path for contrast. The weights in `design/slop-gate.md` are enforced by
  `scripts/aomi.py`, and a test keeps the documentation and the code in step.
- Any component whose provenance could not be established as original.

## Maintenance rule

If a future change borrows material from anywhere, it goes in the table above
with its licence and its required notice before it is committed. A committed file
with unclear provenance is a defect, and this file is where the defect is
recorded.
