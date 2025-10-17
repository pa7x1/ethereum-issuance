"""
Generate an SVG similar to presentation/design_yield_curve.svg but plotting
the ethereum_issuance_with_burn_yield_adjusted yield curve.

This script avoids heavy dependencies and uses pure Python math.
It writes the SVG to presentation/design_yield_curve_adjusted.svg

Usage:
  uv run python plots/design_yield_curve_adjusted_svg.py
"""

from __future__ import annotations

import math
from pathlib import Path


# Constants and mapping used in the original design SVG
WIDTH, HEIGHT = 800, 560
X_MIN, X_MAX = 80.0, 760.0  # drawing area along x
Y_AXIS_BASE = 400.0         # y position of 0% on the x-axis
PX_PER_PERCENT = 36.0       # 1% -> 36 px, matches the design SVG

# Stake and model constants
CIRCULATING_SUPPLY = 120_000_000


def ethereum_issuance_with_burn_yield_adjusted(staked: float) -> float:
    """
    Annualized nominal yield multiplier for the adjusted burn curve.
    Mirrors yield_curves.ethereum_issuance_with_burn_yield_adjusted but uses math only.
    Returns m such that percentage yield = 100 * (m - 1).
    """
    # Parameters as defined in yield_curves.py
    # m = 1 + 3.5 * (2.6 * 64 * staked ** -0.5 - 2.6 * log(1 + staked) / 2048.)
    return 1.0 + 3.5 * (2.6 * 64.0 * (staked ** -0.5) - 2.6 * math.log(1.0 + staked) / 2048.0)


def percent_yield(staked: float) -> float:
    return 100.0 * (ethereum_issuance_with_burn_yield_adjusted(staked) - 1.0)


def x_from_ratio(r: float) -> float:
    # Maps stake ratio in [0,1] to SVG coordinates
    return X_MIN + (X_MAX - X_MIN) * r


def y_from_percent(p: float) -> float:
    # 0% at 400; higher % up (smaller y)
    return Y_AXIS_BASE - PX_PER_PERCENT * p


def generate_curve_path(samples: int = 680) -> str:
    # Start from a small positive stake to avoid the singularity at 0
    r_min = 3_200.0 / CIRCULATING_SUPPLY  # matches other plots' lower bound
    r_max = 1.0

    parts: list[str] = []
    for i in range(samples + 1):
        r = r_min + (r_max - r_min) * (i / samples)
        s = CIRCULATING_SUPPLY * r
        p = percent_yield(s)
        x = x_from_ratio(r)
        y = y_from_percent(p)
        cmd = "M" if i == 0 else "L"
        parts.append(f"{cmd}{x:.2f} {y:.2f}")
    return " ".join(parts)


def main() -> None:
    # Compute guides for r=1, r=1/8 and r=1/4
    r_eighth = 1.0 / 8.0
    r_quarter = 1.0 / 4.0
    r_one = 1.0

    s_eighth = CIRCULATING_SUPPLY * r_eighth
    s_quarter = CIRCULATING_SUPPLY * r_quarter
    s_one = CIRCULATING_SUPPLY * r_one

    p_eighth = percent_yield(s_eighth)
    p_quarter = percent_yield(s_quarter)
    p_one = percent_yield(s_one)

    # Round labels to one decimal (e.g. 7.7) like the design SVG
    label_eighth = f"{p_eighth:.1f}"
    label_quarter = f"{p_quarter:.1f}"

    # Coordinates
    x0 = X_MIN
    x1 = X_MAX
    y0 = Y_AXIS_BASE

    x_eighth = x_from_ratio(r_eighth)
    x_quarter = x_from_ratio(r_quarter)
    x_one = x_from_ratio(r_one)
    y_eighth = y_from_percent(p_eighth)
    y_quarter = y_from_percent(p_quarter)
    y_one = y_from_percent(p_one)

    # Build SVG content
    curve_path = generate_curve_path()

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">Adjusted Burn Issuance Yield Curve</title>
  <desc id="desc">
    Issuance yield (nominal %) vs stake ratio. Highlighted axis marks 0→1; color shifts at 1/8 and 1/2.
    Curve: ethereum_issuance_with_burn_yield_adjusted.
  </desc>

  <defs>
    <linearGradient id="axisGradient" x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" gradientUnits="userSpaceOnUse">
      <stop offset="0%"    stop-color="#e11d48"/>
      <stop offset="12.5%" stop-color="#e11d48"/>
      <stop offset="15%"   stop-color="#f97316"/>
      <stop offset="17.5%" stop-color="#f59e0b"/>
      <stop offset="20%"   stop-color="#16a34a"/>
      <stop offset="42%"   stop-color="#16a34a"/>
      <stop offset="45%"   stop-color="#84cc16"/>
      <stop offset="47.5%" stop-color="#f59e0b"/>
      <stop offset="50%"   stop-color="#e11d48"/>
      <stop offset="100%"  stop-color="#e11d48"/>
    </linearGradient>

    <clipPath id="clipRightOfYAxis" clipPathUnits="userSpaceOnUse">
      <rect x="{x0}" y="0" width="{WIDTH - x0}" height="{HEIGHT}"/>
    </clipPath>

    <mask id="noAxisHaloOverlap" maskUnits="userSpaceOnUse" maskContentUnits="userSpaceOnUse">
      <rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" fill="white"/>
      <use href="#adjustedCurve" fill="none" stroke="black" stroke-width="24"
           stroke-linecap="round" stroke-linejoin="round"/>
    </mask>
  </defs>

  <style>
    .axis {{ stroke: #222; stroke-width: 2; }}
    .tick {{ stroke: #222; stroke-width: 1.5; }}
    .label {{ font: 14px system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; fill: #111; }}
    .title {{ font: 16px system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; fill: #111; font-weight: 600; }}
    .highlight {{ stroke: url(#axisGradient); stroke-width: 24; stroke-linecap: round; stroke-opacity: 0.35; }}
    .curve {{ stroke: #000000; stroke-width: 2; fill: none; }}
    .guide {{ stroke: #000; stroke-width: 1.5; stroke-dasharray: 6 6; fill: none; }}
  </style>

  <!-- X-axis highlight -->
  <path d="M{x0:.0f} {y0:.0f} L{x1:.0f} {y0:.0f}" class="highlight" clip-path="url(#clipRightOfYAxis)" mask="url(#noAxisHaloOverlap)"/>

  <!-- Curve halo (colored) -->
  <path clip-path="url(#clipRightOfYAxis)" fill="none"
        stroke="url(#axisGradient)" stroke-opacity="0.35" stroke-width="24"
        stroke-linecap="round" stroke-linejoin="round"
        d="{curve_path}"/>

  <!-- Black curve on top -->
  <path id="adjustedCurve" class="curve" clip-path="url(#clipRightOfYAxis)" d="{curve_path}"/>

  <!-- Axes -->
  <line x1="{x0:.0f}" y1="0" x2="{x0:.0f}" y2="{HEIGHT}" class="axis"/>
  <line x1="{x0:.0f}" y1="{y0:.0f}" x2="{x1:.0f}" y2="{y0:.0f}" class="axis"/>

  <!-- X Ticks: 0, 1/8, 1/4, 1/2, 1 -->
  <line x1="{x0:.0f}" y1="{y0-6:.0f}" x2="{x0:.0f}" y2="{y0+6:.0f}" class="tick"/>
  <line x1="{x_eighth:.0f}" y1="{y0-6:.0f}" x2="{x_eighth:.0f}" y2="{y0+6:.0f}" class="tick"/>
  <line x1="{x_quarter:.0f}" y1="{y0-6:.0f}" x2="{x_quarter:.0f}" y2="{y0+6:.0f}" class="tick"/>
  <line x1="{x_from_ratio(0.5):.0f}" y1="{y0-6:.0f}" x2="{x_from_ratio(0.5):.0f}" y2="{y0+6:.0f}" class="tick"/>
  <line x1="{x1:.0f}" y1="{y0-6:.0f}" x2="{x1:.0f}" y2="{y0+6:.0f}" class="tick"/>

  <!-- Guides to (stake ratio = 1/4, yield = {label_quarter}%) -->
  <line x1="{x_quarter:.0f}" y1="{y0:.0f}" x2="{x_quarter:.0f}" y2="{y_quarter:.1f}" class="guide"/>
  <line x1="{x0:.0f}" y1="{y_quarter:.1f}" x2="{x_quarter:.0f}" y2="{y_quarter:.1f}" class="guide"/>
  <circle cx="{x_quarter:.0f}" cy="{y_quarter:.1f}" r="4" fill="#000"/>

  <!-- Guides to (stake ratio = 1/8, yield = {label_eighth}%) -->
  <line x1="{x_eighth:.0f}" y1="{y0:.0f}" x2="{x_eighth:.0f}" y2="{y_eighth:.1f}" class="guide"/>
  <line x1="{x0:.0f}" y1="{y_eighth:.1f}" x2="{x_eighth:.0f}" y2="{y_eighth:.1f}" class="guide"/>
  <circle cx="{x_eighth:.0f}" cy="{y_eighth:.1f}" r="4" fill="#000"/>

  <!-- Y-axis ticks at quarter/eighth yields and 10% top -->
  <line x1="{x0-6:.0f}" y1="{y_quarter:.1f}" x2="{x0+6:.0f}" y2="{y_quarter:.1f}" class="tick"/>
  <line x1="{x0-6:.0f}" y1="{y_eighth:.1f}" x2="{x0+6:.0f}" y2="{y_eighth:.1f}" class="tick"/>
  <line x1="{x0-6:.0f}" y1="40" x2="{x0+6:.0f}" y2="40" class="tick"/>

  <!-- Labels -->
  <text x="{x0-10:.0f}" y="{y0+40:.0f}" text-anchor="middle" class="label">0</text>
  <text x="{x_eighth:.0f}" y="{y0+40:.0f}" text-anchor="middle" class="label">1/8</text>
  <text x="{x_quarter:.0f}" y="{y0+40:.0f}" text-anchor="middle" class="label">1/4</text>
  <text x="{x_from_ratio(0.5):.0f}" y="{y0+40:.0f}" text-anchor="middle" class="label">1/2</text>
  <text x="{x1:.0f}" y="{y0+40:.0f}" text-anchor="middle" class="label">1</text>

  <!-- Y-axis labels -->
  <text x="{x0-10:.0f}" y="{y_quarter:.1f}" text-anchor="end" dominant-baseline="middle" class="label">{label_quarter}</text>
  <text x="{x0-10:.0f}" y="{y_eighth:.1f}" text-anchor="end" dominant-baseline="middle" class="label">{label_eighth}</text>
  <text x="{x0-10:.0f}" y="40" text-anchor="end" dominant-baseline="middle" class="label">10</text>

  <!-- y_e^max at r=1 (dashed guide across) -->
  <line x1="{x0:.0f}" y1="{y_one:.1f}" x2="{x1:.0f}" y2="{y_one:.1f}" class="guide"/>
  <line x1="{x0-6:.0f}" y1="{y_one:.1f}" x2="{x0+6:.0f}" y2="{y_one:.1f}" class="tick"/>
  <text x="{x0-10:.0f}" y="{y_one:.1f}" text-anchor="end" dominant-baseline="middle" class="label">
    <tspan style="font-style: italic">y</tspan>
    <tspan baseline-shift="sub" font-size="11" style="font-style: italic">e</tspan>
    <tspan baseline-shift="super" font-size="11">max</tspan>
  </text>

  <!-- Axis names -->
  <text x="600" y="{y0+60:.0f}" text-anchor="middle" class="title">Stake Ratio</text>
  <text x="90" y="280" text-anchor="middle" class="title" transform="rotate(-90 32 280)">Issuance Yield (%)</text>
</svg>
'''

    out = Path("presentation/design_yield_curve_adjusted.svg")
    out.write_text(svg)
    print(f"Wrote {out} (1/8={p_eighth:.2f}%, 1/4={p_quarter:.2f}%)")


if __name__ == "__main__":
    main()
