#!/usr/bin/env python3
"""Build Aomi's raster assets from the authored SVG sources.

Run from the repository root:  python3 scripts/build_assets.py

Inputs
  assets/logo.svg              hand-authored mark (the source of truth)
  assets/workflow.svg          hand-authored workflow diagram
  assets/artwork-seed.png      the generated editorial artwork used on the cover

Outputs
  assets/logo.png              mark on a paper-coloured tile, for READMEs on any theme
  assets/hero.png              1600x560 cover: artwork on the right, typography on the left

Only the standard library is required, plus rsvg-convert on PATH for
rasterisation. If Pillow is installed the PNGs are also palette-optimised so the
README stays light; without it the build still succeeds, the files are just
larger. Text is composed in SVG rather than drawn inside the image model
so that wording and spelling stay exact.
"""
from __future__ import annotations

import base64
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

INK = "#33303A"
ROSE = "#A2606E"
GOLD = "#C9A46A"
PAPER = "#F6F1EA"
HAIRLINE = "#DFD3C8"
MUTED = "#6E6570"
LABEL = "#8B8078"

MARK = """  <g transform="translate({x} {y}) scale({s})">
    <circle cx="156" cy="128" r="58" fill="{rose}" clip-path="url(#clip-a)"/>
    <g fill="none" stroke="{ink}" stroke-width="8">
      <circle cx="100" cy="128" r="58"/>
      <circle cx="156" cy="128" r="58"/>
    </g>
    <circle cx="128" cy="128" r="10" fill="{gold}"/>
  </g>"""


def need_rsvg() -> str:
    exe = shutil.which("rsvg-convert")
    if not exe:
        sys.exit("rsvg-convert is required (librsvg2-bin). Without it, keep the SVG assets as they are.")
    return exe


def optimise(png: pathlib.Path, colours: int = 128) -> None:
    """Shrink flat artwork without visible loss. Optional: needs Pillow."""
    try:
        from PIL import Image
    except ImportError:
        return
    with Image.open(png) as im:
        im.convert("RGB").quantize(colors=colours, dither=Image.FLOYDSTEINBERG).save(
            png, optimize=True
        )


def rasterise(exe: str, svg: pathlib.Path, out: pathlib.Path, width: int | None = None) -> None:
    cmd = [exe, "-f", "png"]
    if width:
        cmd += ["-w", str(width)]
    cmd += [str(svg), "-o", str(out)]
    subprocess.run(cmd, check=True)
    optimise(out)
    print(f"  {out.relative_to(ROOT)}  ({out.stat().st_size // 1024} KB)")


def tile_logo(exe: str) -> None:
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" width="640" height="640">
  <defs><clipPath id="clip-a"><circle cx="100" cy="128" r="58"/></clipPath></defs>
  <rect width="640" height="640" rx="96" fill="{PAPER}"/>
  <g transform="translate(132 92) scale(1.5)">
    <circle cx="156" cy="128" r="58" fill="{ROSE}" clip-path="url(#clip-a)"/>
    <g fill="none" stroke="{INK}" stroke-width="8">
      <circle cx="100" cy="128" r="58"/>
      <circle cx="156" cy="128" r="58"/>
    </g>
    <circle cx="128" cy="128" r="10" fill="{GOLD}"/>
  </g>
</svg>"""
    tmp = pathlib.Path("/tmp/aomi-logo-tile.svg")
    tmp.write_text(svg)
    rasterise(exe, tmp, ASSETS / "logo.png", width=512)


def build_hero(exe: str) -> None:
    seed = ASSETS / "artwork-seed.png"
    if not seed.exists():
        sys.exit("assets/artwork-seed.png is missing; the cover artwork lives there.")
    # Trim the artwork to its useful region so the cover does not show empty paper twice.
    b64 = base64.b64encode(seed.read_bytes()).decode("ascii")

    art_x, art_size = 1000, 560
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 560" width="1600" height="560">
  <defs>
    <clipPath id="clip-a"><circle cx="100" cy="128" r="58"/></clipPath>
    <clipPath id="art"><rect x="{art_x}" y="0" width="{art_size}" height="560"/></clipPath>
  </defs>
  <rect width="1600" height="560" fill="{PAPER}"/>
  <image href="data:image/png;base64,{b64}" x="{art_x}" y="0" width="{art_size}" height="560"
         preserveAspectRatio="xMidYMid slice" clip-path="url(#art)"/>
  <rect x="{art_x - 26}" y="40" width="{art_size}" height="480" fill="none" stroke="{ROSE}" stroke-width="1.5" opacity="0.55"/>
  <line x1="912" y1="96" x2="912" y2="464" stroke="{HAIRLINE}" stroke-width="1.5"/>

{MARK.format(x=128, y=92, s=0.52, ink=INK, rose=ROSE, gold=GOLD)}

  <text x="128" y="316" font-family="Noto Serif, Georgia, serif" font-size="112" fill="{INK}" letter-spacing="1">Aomi</text>
  <line x1="132" y1="364" x2="700" y2="364" stroke="{HAIRLINE}" stroke-width="1.5"/>
  <text x="132" y="456" font-family="Noto Sans, Helvetica, Arial, sans-serif" font-size="13" fill="{LABEL}" letter-spacing="3.6">ENGINEERING INTELLIGENCE  &#215;  DESIGN INTELLIGENCE</text>
</svg>"""
    tmp = pathlib.Path("/tmp/aomi-hero.svg")
    tmp.write_text(svg)
    rasterise(exe, tmp, ASSETS / "hero.png", width=1600)


def main() -> None:
    exe = need_rsvg()
    print("building Aomi assets")
    tile_logo(exe)
    build_hero(exe)
    if (ASSETS / "workflow.svg").exists():
        rasterise(exe, ASSETS / "workflow.svg", ASSETS / "workflow.png", width=1200)
    print("done")


if __name__ == "__main__":
    main()
