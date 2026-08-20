"""
Re-runs the real-yield analysis with the refined cost models in `cost_models.py`
and compares against the original `cost_structure.py` probes, focusing on two
curves: the current issuance curve (status quo) and the EIP-8363 tapered
issuance burn (ethereum/EIPs#12081, permanent state).

Generates the plots under `refined_costs/plots/` and prints the summary tables
used in REFINED_COSTS.md. Run from the repo root:

    uv run python -m refined_costs.analysis
"""

from pathlib import Path
from typing import Callable, Optional
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator, AutoMinorLocator

from common import CIRCULATING_SUPPLY, percentage_yield
from curve_picker.candidates import ethereum_issuance_yield, eip8363_tapered_burn
from cost_structure import home_staking
from cost_models import (
    StakerCostModel,
    MatchedOperatorModel,
    home_staker,
    retail_delegator,
    whale_delegator,
    industrial_self_staker,
    csm_single,
    csm_ten,
    csm_ics_ten,
    rocketpool_ten,
    home_staker_annual_fixed_usd,
    node_operator_budget,
    node_operator_mid,
    node_operator_premium,
    el_reward_yield,
    ETH_PRICE_USD,
    ETH_PRICE_APPRECIATED_USD,
    MODULE_PROGRAM_COST_USD,
    MODULE_PROGRAM_REWARD_SHARE,
    CSM_MODULE_SIZE_ETH,
    ROCKETPOOL_MODULE_SIZE_ETH,
)
from operator_economics import operator_breakeven_delegation_eth, module_program_breakeven_tvl_eth
from plots.formatters import stake_formatter
from yields import real_issuance_yield, real_staking_yield, effective_holding_yield


# Colors follow the archetype across every figure (CVD-checked set, close to the
# hues the original plots use for the equivalent archetypes).
COLOR_SOLO = "#2563eb"
COLOR_RETAIL = "#15803d"
COLOR_WHALE = "#d97706"
COLOR_HOLDING = "#b91c1c"
COLOR_BONDED = "#7c3aed"

# Curve-identity plots use one hue with distinct linestyles instead.
CURVE_STYLES = ["-", "--"]

PLOTS_DIR = Path(__file__).resolve().parent / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

STAKE_GRID = np.linspace(3200, CIRCULATING_SUPPLY * 0.99, 20_000)

# Minimum real yield premium over holding a delegator might demand, given
# perceived risks. External incentives (CEX fee rebates, points programs)
# can push the effective floor towards 0.
PREMIUM_THRESHOLDS = [0.01, 0.005, 0.0025, 0.001]


def refined_real_yield(curve_fn: Callable,
                       model: StakerCostModel,
                       staked: np.ndarray,
                       eth_price_usd: float = ETH_PRICE_USD) -> np.ndarray:
    """Real yield of a refined archetype under a given issuance yield curve."""
    return real_staking_yield(
        issuance_yield=curve_fn(staked),
        supply=CIRCULATING_SUPPLY,
        staked=staked,
        fixed_cost_ratio=model.fixed_cost_ratio(eth_price_usd),
        reward_fee=model.reward_fee,
        tax_rate=model.tax_rate,
        exogenous_yield=model.mev_capture * el_reward_yield(staked),
    )


def matched_operator_real_yield(curve_fn: Callable,
                                operator: MatchedOperatorModel,
                                staked: np.ndarray,
                                eth_price_usd: float = ETH_PRICE_USD) -> np.ndarray:
    """Real yield on own capital of a bonded matched home operator (CSM/Rocket Pool)."""
    issuance_yield = curve_fn(staked)
    reward_rate = (issuance_yield - 1.) + el_reward_yield(staked)
    gross = operator.gross_yield_on_bond(reward_rate)
    net = gross - np.maximum(0., operator.tax_rate * gross)
    fixed = operator.annual_fixed_usd / (operator.bond_eth * eth_price_usd)
    return (1. - fixed + net) / (staked * (issuance_yield - 1.) / CIRCULATING_SUPPLY + 1.)


def delegate_premium(curve_fn: Callable, staked: np.ndarray) -> np.ndarray:
    """
    Real yield premium of a retail delegator over holding, post-fee and pre-tax.
    Staker and holder share the same dilution, so the premium reduces to the
    delegator's net reward rate. This is the quantity that must meet the
    delegator's required risk premium at equilibrium.
    """
    reward_rate = (curve_fn(staked) - 1.) + el_reward_yield(staked)
    return reward_rate - np.maximum(0., retail_delegator.reward_fee * reward_rate)


def descending_crossing(staked: np.ndarray, series: np.ndarray, level: float) -> Optional[float]:
    """First stake level where the series crosses the level from above."""
    excess = series - level
    signs = np.sign(excess)
    descending = np.where((signs[:-1] > 0) & (signs[1:] <= 0))[0]
    if len(descending) == 0:
        return None
    i = descending[0]
    x0, x1 = staked[i], staked[i + 1]
    y0, y1 = excess[i], excess[i + 1]
    return x0 - y0 * (x1 - x0) / (y1 - y0)


def zero_crossing(staked: np.ndarray, real_yield: np.ndarray) -> Optional[float]:
    """First stake level where the real yield crosses from positive to negative."""
    return descending_crossing(staked, real_yield, 1.0)


def fmt_crossing(value: Optional[float]) -> str:
    return f"{value / 1e6:.1f}M" if value is not None else "never"


def _plot_real_yields(curve_fn: Callable, title: str, output_path: Path) -> None:
    x = STAKE_GRID

    series = [
        ("Solo Validator (32 ETH)", COLOR_SOLO, "-",
         refined_real_yield(curve_fn, home_staker, x)),
        ("Retail Delegator (1k ETH, 10% fee)", COLOR_RETAIL, "-",
         refined_real_yield(curve_fn, retail_delegator, x)),
        ("Whale Delegator (100k ETH, 1% fee)", COLOR_WHALE, "-",
         refined_real_yield(curve_fn, whale_delegator, x)),
        ("CSM Operator (10 validators, 3.5% share)", COLOR_BONDED, "-",
         matched_operator_real_yield(curve_fn, csm_ten, x)),
        ("Rocket Pool LEB8 (10 minipools, 14%)", COLOR_BONDED, "--",
         matched_operator_real_yield(curve_fn, rocketpool_ten, x)),
        ("Holding", COLOR_HOLDING, "-",
         effective_holding_yield(curve_fn(x), CIRCULATING_SUPPLY, x)),
    ]

    fig, ax = plt.subplots(figsize=(10, 6))
    for label, color, linestyle, values in series:
        ax.plot(x, percentage_yield(values), label=label, color=color,
                linewidth=2 if linestyle == "-" else 1.4, linestyle=linestyle)

    # Direct labels at each staking archetype's zero crossing (secondary encoding
    # beyond color). Staggered heights keep labels legible when crossings coincide.
    for i, (label, color, linestyle, values) in enumerate(series[:5]):
        crossing = zero_crossing(x, values)
        if crossing is not None:
            ax.annotate(
                f"{crossing / 1e6:.0f}M",
                xy=(crossing, 0),
                xytext=(crossing, 1.1 + 0.7 * i),
                ha="center",
                fontsize=9,
                color=color,
                bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none", alpha=0.75),
                arrowprops=dict(arrowstyle="-", color=color, linewidth=0.8, alpha=0.6),
            )

    ax.set_title(f"{title} Real Yields (Refined Costs, incl. EL Rewards)")
    ax.xaxis.set_major_formatter(FuncFormatter(stake_formatter))
    ax.xaxis.set_major_locator(MultipleLocator(10_000_000))
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.set_xlabel("Stake (Millions of ETH)")
    ax.set_ylabel("Yield (%)")
    ax.set_ylim(bottom=-4, top=10)
    ax.set_xlim(left=0, right=CIRCULATING_SUPPLY)
    ax.axhline(y=0, color="k", linewidth=0.5)
    ax.axvline(x=0, color="k", linewidth=0.5)
    ax.xaxis.set_minor_locator(AutoMinorLocator(5))
    ax.yaxis.set_minor_locator(AutoMinorLocator(5))
    ax.grid(True, which="major", linestyle="--", linewidth=0.6, alpha=0.7)
    ax.grid(True, which="minor", linestyle=":", linewidth=0.4, alpha=0.5)
    ax.legend(fontsize=9)

    fig.savefig(output_path, dpi=fig.dpi)
    plt.close(fig)


def _plot_delegate_premium(curves: list, output_path: Path) -> None:
    x = np.linspace(5e6, CIRCULATING_SUPPLY * 0.99, 5_000)

    fig, ax = plt.subplots(figsize=(10, 6))
    for (title, curve_fn), linestyle in zip(curves, CURVE_STYLES):
        ax.plot(x, 100. * delegate_premium(curve_fn, x), label=title,
                color=COLOR_RETAIL, linewidth=2, linestyle=linestyle)

    for threshold in PREMIUM_THRESHOLDS:
        ax.axhline(y=100. * threshold, color="k", linewidth=0.6, linestyle=":", alpha=0.5)
    # Label the outer thresholds only; the ruled lines carry the rest.
    for threshold, offset in [(PREMIUM_THRESHOLDS[0], 0.05), (PREMIUM_THRESHOLDS[-1], -0.32)]:
        ax.annotate(f"{100. * threshold:g}% required premium", xy=(1e6, 100. * threshold + offset),
                    ha="left", va="bottom", fontsize=8, color="#555555")

    ax.set_title("Retail Delegator Premium over Holding (post-fee, pre-tax)")
    ax.xaxis.set_major_formatter(FuncFormatter(stake_formatter))
    ax.set_xlabel("Stake (Millions of ETH)")
    ax.set_ylabel("Premium (%)")
    ax.set_ylim(bottom=-2, top=5)
    ax.set_xlim(left=0, right=CIRCULATING_SUPPLY)
    ax.axhline(y=0, color="k", linewidth=0.5)
    ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.6)
    ax.legend(fontsize=10)

    fig.savefig(output_path, dpi=fig.dpi)
    plt.close(fig)


def _plot_delegation_pull(curves: list, output_path: Path) -> None:
    x = np.linspace(5e6, CIRCULATING_SUPPLY * 0.99, 5_000)

    fig, ax = plt.subplots(figsize=(10, 6))
    for (title, curve_fn), linestyle in zip(curves, CURVE_STYLES):
        pull = percentage_yield(refined_real_yield(curve_fn, retail_delegator, x)) \
            - percentage_yield(refined_real_yield(curve_fn, home_staker, x))
        ax.plot(x, pull, label=title, color=COLOR_SOLO, linewidth=2, linestyle=linestyle)

    ax.set_title("Delegation Pull: Retail Delegator Real Yield minus Solo Real Yield")
    ax.xaxis.set_major_formatter(FuncFormatter(stake_formatter))
    ax.set_xlabel("Stake (Millions of ETH)")
    ax.set_ylabel("Real Yield Gap (percentage points)")
    ax.set_xlim(left=0, right=CIRCULATING_SUPPLY)
    ax.axhline(y=0, color="k", linewidth=0.5)
    ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.6)
    ax.legend(fontsize=10)

    fig.savefig(output_path, dpi=fig.dpi)
    plt.close(fig)


def _plot_operator_breakeven(curves: list, output_path: Path) -> None:
    x = np.linspace(5e6, CIRCULATING_SUPPLY * 0.55, 5_000)
    # Fee tiers are an ordered magnitude, so they get a sequential ramp of a
    # single hue rather than the archetype identity colors.
    operators = [
        ("0.5% fee", "#60a5fa", node_operator_budget),
        ("1% fee", "#2563eb", node_operator_mid),
        ("3% fee", "#1e3a8a", node_operator_premium),
    ]

    fig, axes = plt.subplots(1, len(curves), figsize=(5.5 * len(curves), 5), sharey=True)
    for ax, (title, curve_fn) in zip(axes, curves):
        for label, color, operator in operators:
            breakeven = operator_breakeven_delegation_eth(operator, x, curve_fn(x))
            ax.plot(x, breakeven, label=label, color=color, linewidth=2)
        ax.set_yscale("log")
        ax.set_title(title, fontsize=11)
        ax.xaxis.set_major_formatter(FuncFormatter(stake_formatter))
        ax.set_xlabel("Total Stake (Millions of ETH)")
        ax.set_ylim(bottom=1e3, top=1e6)
        ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.6)
    axes[0].set_ylabel("Break-even Delegation (ETH, log scale)")
    axes[0].legend(fontsize=10, title="Operator fee on rewards")
    fig.suptitle("Node Operator Break-even Delegation vs Total Stake")
    fig.tight_layout()

    fig.savefig(output_path, dpi=fig.dpi)
    plt.close(fig)


def _plot_eth_price_sensitivity(curves: list, output_path: Path) -> None:
    prices = np.linspace(1_000, 8_000, 60)

    fig, ax = plt.subplots(figsize=(10, 6))
    for (title, curve_fn), linestyle in zip(curves, CURVE_STYLES):
        crossings = []
        for price in prices:
            values = refined_real_yield(curve_fn, home_staker, STAKE_GRID, eth_price_usd=price)
            crossing = zero_crossing(STAKE_GRID, values)
            crossings.append(crossing / 1e6 if crossing is not None else np.nan)
        ax.plot(prices, crossings, label=title, color=COLOR_SOLO, linewidth=2, linestyle=linestyle)

    ax.axvline(x=ETH_PRICE_USD, color="k", linewidth=0.8, linestyle=":", alpha=0.7)
    y_low, y_high = ax.get_ylim()
    ax.annotate(f"assumed {ETH_PRICE_USD:.0f} USD", xy=(ETH_PRICE_USD, y_low),
                xytext=(ETH_PRICE_USD * 1.03, y_low + 0.05 * (y_high - y_low)),
                fontsize=9, color="k")
    ax.set_title("Solo Validator 0% Real Yield Crossing vs ETH Price")
    ax.set_xlabel("ETH Price (USD)")
    ax.set_ylabel("Stake at 0% Real Yield (Millions of ETH)")
    ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.6)
    ax.legend(fontsize=10)

    fig.savefig(output_path, dpi=fig.dpi)
    plt.close(fig)


def main() -> None:
    curves = [
        ("Current Issuance Curve", ethereum_issuance_yield),
        ("EIP-8363 Tapered Burn (permanent)", eip8363_tapered_burn),
    ]
    curve_slugs = ["current_curve", "eip8363"]

    bonded_operators = [csm_single, csm_ten, csm_ics_ten, rocketpool_ten]

    print("Annual fixed costs (USD):")
    print(f"  Solo staker (4y depreciation): {home_staker.annual_fixed_usd:,.0f}"
          f" ({100. * home_staker.fixed_cost_ratio():.2f}% of stake at {ETH_PRICE_USD:.0f} USD/ETH)")
    five_year = home_staker_annual_fixed_usd(hardware_lifespan_years=5.)
    print(f"  Solo staker (5y depreciation): {five_year:,.0f}"
          f" ({100. * five_year / (home_staker.stake_eth * ETH_PRICE_USD):.2f}% of stake)")
    for op in bonded_operators:
        ratio = op.annual_fixed_usd / (op.bond_eth * ETH_PRICE_USD)
        print(f"  {op.label}: same rig, {100. * ratio:.2f}% of own capital")
    print(f"  Node operator: {node_operator_mid.annual_fixed_usd:,.0f}")
    print(f"  Original home staker probe: 300 (0.23% of stake)")
    print()

    print("Bonded operator gross yield on own capital at today's stake (34M):")
    r_today = (ethereum_issuance_yield(34e6) - 1.) + el_reward_yield(34e6)
    for op in bonded_operators:
        print(f"  {op.label}: {100. * op.gross_yield_on_bond(r_today):.2f}% gross")
    print()

    print("Stake at 0% real yield (original probes vs refined models):")
    for price in (ETH_PRICE_USD, ETH_PRICE_APPRECIATED_USD):
        print(f"  --- at {price:.0f} USD/ETH ---")
        for title, curve_fn in curves:
            x = STAKE_GRID
            rows = {
                "solo (original probes)": real_issuance_yield(curve_fn(x), CIRCULATING_SUPPLY, x, **home_staking),
                "solo (refined)": refined_real_yield(curve_fn, home_staker, x, price),
                "retail delegator": refined_real_yield(curve_fn, retail_delegator, x, price),
                "whale delegator": refined_real_yield(curve_fn, whale_delegator, x, price),
                "industrial self-staker": refined_real_yield(curve_fn, industrial_self_staker, x, price),
            }
            rows.update({op.label: matched_operator_real_yield(curve_fn, op, x, price) for op in bonded_operators})
            print(f"  {title}:")
            for label, values in rows.items():
                print(f"    {label}: {fmt_crossing(zero_crossing(x, values))}")
    print()

    print("Staking-module program viability: module TVL needed for the sponsor's")
    print(f"{100. * MODULE_PROGRAM_REWARD_SHARE:g}% share of module rewards to cover a "
          f"{MODULE_PROGRAM_COST_USD / 1e6:g}M USD/yr program")
    print(f"(reference sizes: CSM ~{CSM_MODULE_SIZE_ETH / 1e3:.0f}k ETH, "
          f"Rocket Pool ~{ROCKETPOOL_MODULE_SIZE_ETH / 1e3:.0f}k ETH):")
    for price in (ETH_PRICE_USD, ETH_PRICE_APPRECIATED_USD):
        for title, curve_fn in curves:
            values = []
            for stake_level in [34e6, 45e6, 55e6, 60.25e6]:
                tvl = module_program_breakeven_tvl_eth(
                    MODULE_PROGRAM_COST_USD, MODULE_PROGRAM_REWARD_SHARE,
                    stake_level, curve_fn(stake_level), price)
                values.append(f"{stake_level / 1e6:.0f}M: " + (f"{tvl / 1e6:.2f}M" if np.isfinite(tvl) else "inf"))
            print(f"  {price:.0f} USD/ETH, {title}: " + " | ".join(values))
    print()

    print("Delegation pull (retail delegator real yield minus solo real yield, pp):")
    for stake_level in [34e6, 40e6, 48e6, 60e6]:
        row = []
        for title, curve_fn in curves:
            xs = np.array([stake_level, stake_level + 1.])
            pull = percentage_yield(refined_real_yield(curve_fn, retail_delegator, xs))[0] \
                - percentage_yield(refined_real_yield(curve_fn, home_staker, xs))[0]
            row.append(f"{title.split(' (')[0]}: {pull:+.2f}")
        print(f"  {stake_level / 1e6:.0f}M staked -> " + " | ".join(row))
    print()

    print("Equilibrium: stake where the retail delegator premium over holding")
    print("(post-fee, pre-tax) falls to the required premium:")
    x = STAKE_GRID
    for title, curve_fn in curves:
        premium = delegate_premium(curve_fn, x)
        levels = [f"{100. * t:g}%: {fmt_crossing(descending_crossing(x, premium, t))}"
                  for t in PREMIUM_THRESHOLDS]
        print(f"  {title}: " + " | ".join(levels))
    saturation_premium = delegate_premium(eip8363_tapered_burn, np.array([60_250_000.]))[0]
    end_premium = delegate_premium(eip8363_tapered_burn, np.array([CIRCULATING_SUPPLY * 0.99]))[0]
    print(f"  EIP-8363 premium floor: {100. * saturation_premium:.2f}% at saturation (60.25M),"
          f" {100. * end_premium:.2f}% at 99% of supply -- never negative (MEV-only floor)")
    print()

    print("Node operator break-even delegation (ETH):")
    for stake_level in [34e6, 45e6, 55e6, 58e6]:
        for title, curve_fn in curves:
            values = [f"{label}: {operator_breakeven_delegation_eth(op, stake_level, curve_fn(stake_level)):,.0f}"
                      for label, op in [("0.5%", node_operator_budget), ("1%", node_operator_mid), ("3%", node_operator_premium)]]
            print(f"  {stake_level / 1e6:.0f}M staked, {title}: " + " | ".join(values))
    print()

    for (title, curve_fn), slug in zip(curves, curve_slugs):
        _plot_real_yields(curve_fn, title, PLOTS_DIR / f"real_yields_{slug}.png")

    _plot_delegate_premium(curves, PLOTS_DIR / "delegate_premium.png")
    _plot_delegation_pull(curves, PLOTS_DIR / "delegation_pull.png")
    _plot_operator_breakeven(curves, PLOTS_DIR / "operator_breakeven.png")
    _plot_eth_price_sensitivity(curves, PLOTS_DIR / "home_staker_eth_price_sensitivity.png")
    print(f"Plots written to {PLOTS_DIR}")


if __name__ == "__main__":
    main()
