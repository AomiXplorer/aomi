# Palettes

Six starting points, one per kind of product. They are starting points, not
answers: take the ground, the ink and the temperature, then choose the brand hue
from the product and check every pair with the tool.

Every ratio below was computed with `aomi contrast` against the
values in the table, with `#FFFFFF` on light grounds and `#101216` on dark ones.

| palette | ground | surface | ink | muted ink | brand |
| --- | --- | --- | --- | --- | --- |
| Paper and ink | `#F7F4EE` | `#FFFFFF` | `#221F23` | `#6E6560` | `#7C2D3A` |
| Clinic daylight | `#F4F7F6` | `#FFFFFF` | `#1E2A2B` | `#5A6A69` | `#16626B` |
| Warm ledger | `#FBF7F2` | `#FFFFFF` | `#25201B` | `#6B6156` | `#8A4B1F` |
| Studio | `#FAF7F5` | `#FFFFFF` | `#2A2326` | `#6E6266` | `#A63D5C` |
| Field | `#FFFFFF` | `#F4F6F7` | `#1B1D1F` | `#5C6165` | `#2A5D34` |
| Night instrument | `#14161A` | `#1C1F25` | `#ECEEF1` | `#9AA3AD` | `#7FB2E8` |

Contrast, as measured:

| palette | ink on ground | muted on ground | brand on ground | text on brand |
| --- | --- | --- | --- | --- |
| Paper and ink | 14.85 | 5.18 | 8.34 | 9.16 |
| Clinic daylight | 13.71 | 5.26 | 6.51 | 7.02 |
| Warm ledger | 15.13 | 5.67 | 6.34 | 6.76 |
| Studio | 14.40 | 5.47 | 5.72 | 6.10 |
| Field | 16.91 | 6.26 | 7.74 | 7.74 |
| Night instrument | 15.58 | 7.09 | 8.14 | 8.42 |

## When each one fits

**Paper and ink.** Long reading, catalogues, documentation, anything where the
content is the interface. Warm neutrals, a wine brand that never appears more than
five percent of the screen. Fails when the product needs to signal many states
quickly; one brand hue cannot carry them.

**Clinic daylight.** Appointment, health, service booking. A cool ground that
stays readable under fluorescent light, a teal brand that reads as care rather
than as finance. Keep the ground genuinely light; tinted greys turn green under
office lighting.

**Warm ledger.** Money, invoicing, operations reviewed on paper or in daylight. A
burnt brand that signals "record" rather than "alert". Do not pair it with a
second warm accent; the whole screen turns to sepia.

**Studio.** Creative tools, portfolios, small commerce. Rose-leaning brand, warm
ground, wide margins. Fails at density: this palette cannot carry 32px table rows
without looking like a boutique receipt.

**Field.** Mobile-first, used outdoors, gloves, one hand. The highest contrast of
the six, a saturated brand that survives sunlight. Avoid thin type and low-weight
icons here; the palette is only half of outdoor legibility.

**Night instrument.** Monitoring, dashboards read for hours, developer tools.
Raised surfaces, desaturated brand, muted ink at 7:1 so secondary text does not
vanish. Do not use pure black; the glare costs more than the contrast gains.

## Building a seventh

1. Choose the ground from the room the product lives in, not from a trend.
2. Choose the neutral temperature to agree with the brand hue.
3. Choose the brand hue last, at a value that passes 4.5:1 as text on the ground
   and 4.5:1 with white or near-black on top of it.
4. Then write the semantic four. If a semantic colour is the same hue as the
   brand, change one of them.
