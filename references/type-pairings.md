# Type pairings

Nine combinations of openly licensed families, with what each one is good at and
where it goes wrong. All are available under the SIL Open Font License, so they
can be self-hosted. Check the licence file of the version you ship; versions and
reserved font names change.

The pairing is not the decision. The decision is the reading condition, the
hierarchy, and the scale. These are shortcuts to a defensible start.

| display | text | temperament | fits | fails at |
| --- | --- | --- | --- | --- |
| Fraunces | Public Sans | warm, editorial, slightly literary | reading products, hospitality, subscription content | dense tables, dashboards |
| Instrument Serif | Inter Tight | sharp, contemporary, magazine | publishing, reports, launch pages | long body text at small sizes |
| Newsreader | Work Sans | calm, newsroom, trustworthy | newsletters, documentation, civic | playful or youthful products |
| Bricolage Grotesque | Source Sans 3 | characterful, industrial, friendly | creative tools, indie products, workshops | legal, medical, enterprise trust |
| Space Grotesk | IBM Plex Sans | technical, engineered | developer tools, infrastructure, specs | consumer warmth, hospitality |
| Fraunces (soft axis) | Atkinson Hyperlegible | gentle and unusually legible | accessibility-first, health, education | brand-led marketing |
| Archivo (expanded) | Archivo | one family, two widths, disciplined | instruments, dense UI, systems | anything needing editorial voice |
| Spectral | Karla | quiet, refined, slightly serious | finance, research, long reports | playful apps, marketing headlines |
| Bitter | Libre Franklin | sturdy, readable, unfashionable in a good way | public services, logistics, field tools | luxury, editorial |

## Rules that survive any pairing

- Two families maximum. One family used at three weights and two widths beats two
  families used badly.
- The text face carries the argument: optimise it for the smallest size it will
  actually be read at.
- The display face appears once or twice per screen. If it appears five times, its
  character becomes noise, and the hierarchy collapses.
- Do not pair two expressive faces. The competition is visible on every screen.
- Check digits: any number in a column needs tabular figures, and many expressive
  display faces do not have them.
- Check language coverage before committing. A face without the diacritics or the
  script your users write in is not a candidate, whatever it looks like.

## Avoid by default

- The same neutral geometric sans for both roles, which is what "clean" defaults
  to and produces the interchangeable look.
- A serif display over a serif body: the reading texture becomes uniform and the
  hierarchy has to be carried by size alone.
- Monospace used for non-code content "for a technical feel". It costs reading
  speed and signals a costume.
- Trend faces at their default settings. If the type is recognisable as this
  year's choice, it will date the product to this year.

## Fallback metrics

When a family is swapped or fails to load, the layout must not reflow. Define a
fallback with a similar x-height and width, and set size and spacing adjustments
for it. If your only fallback is the browser default, the first paint will be a
different design.
