from functools import partial
from pathlib import Path
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator, AutoMinorLocator

from curve_picker.candidates import *
from curve_picker.fix_parameters import fix_parameters
from common import CIRCULATING_SUPPLY, percentage_yield
from cost_structure import home_staking, lst_staking, institutional_staking
from plots.formatters import stake_formatter, issuance_formatter
from yields import real_issuance_yield, effective_holding_yield
from issuance import issuance


curves = [
    log_burn_baguette,
    aggressive_log_burn_baguette,
    quadratic_burn_baguette,
    linear_burn_baguette,
    constant_burn_baguette,
]


def _plot_real_yield(curve_fn, title: str, output_path: Path) -> None:
    x = np.linspace(3200, CIRCULATING_SUPPLY * 0.99, 240)
    issuance_yield = curve_fn(x)

    solo = percentage_yield(
        real_issuance_yield(
            issuance_yield=issuance_yield,
            supply=CIRCULATING_SUPPLY,
            staked=x,
            **home_staking,
        )
    )
    lst = percentage_yield(
        real_issuance_yield(
            issuance_yield=issuance_yield,
            supply=CIRCULATING_SUPPLY,
            staked=x,
            **lst_staking,
        )
    )
    institutional = percentage_yield(
        real_issuance_yield(
            issuance_yield=issuance_yield,
            supply=CIRCULATING_SUPPLY,
            staked=x,
            **institutional_staking,
        )
    )
    holding = percentage_yield(
        effective_holding_yield(
            issuance_yield=issuance_yield,
            supply=CIRCULATING_SUPPLY,
            staked=x,
        )
    )
    lst_premium = lst - holding

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x, solo, label="Home Validator", color="blue", linewidth=2)
    ax.plot(x, lst, label="LST", color="green", linewidth=2)
    ax.plot(x, institutional, label="Institutional", color="orange", linewidth=2)
    ax.plot(x, holding, label="Holding", color="red", linewidth=2)
    ax.plot(
        x,
        lst_premium,
        label="LST - Holding Premium",
        color="purple",
        linewidth=2,
        linestyle="--",
    )

    ax.set_title(f"{title} Real Yields")
    ax.xaxis.set_major_formatter(FuncFormatter(stake_formatter))
    ax.xaxis.set_major_locator(MultipleLocator(5_000_000))
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
    ax.legend(fontsize=12)

    fig.savefig(output_path, dpi=fig.dpi)
    plt.close(fig)


def _plot_nominal_yield(curve_fn, title: str, output_path: Path) -> None:
    x = np.linspace(3200, CIRCULATING_SUPPLY, 240)
    nominal = percentage_yield(curve_fn(x))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x, nominal, color="blue", linewidth=2)
    ax.set_title(f"{title} Nominal Yield")
    ax.xaxis.set_major_formatter(FuncFormatter(stake_formatter))
    ax.set_xlabel("Stake (Millions of ETH)")
    ax.set_ylabel("Yield (%)")
    ax.set_ylim(bottom=-3, top=10)
    ax.set_xlim(left=0, right=CIRCULATING_SUPPLY)
    ax.grid(True, which="both", linestyle="--", linewidth=0.5)
    ax.axhline(y=0, color="k", linewidth=0.5)
    ax.axvline(x=0, color="k", linewidth=0.5)

    fig.savefig(output_path, dpi=fig.dpi)
    plt.close(fig)


def _plot_issuance_curve(curve_fn, title: str, output_path: Path) -> None:
    x = np.linspace(3200, CIRCULATING_SUPPLY, 240)
    issuance_ratio = issuance(curve_fn, x) / CIRCULATING_SUPPLY

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x, issuance_ratio, color="blue", linewidth=2)
    ax.set_title(f"{title} Issuance Curve")
    ax.xaxis.set_major_formatter(FuncFormatter(stake_formatter))
    ax.yaxis.set_major_formatter(FuncFormatter(issuance_formatter))
    ax.set_xlabel("Stake (Millions of ETH)")
    ax.set_ylabel("Issuance (%)")
    ax.set_xlim(left=0, right=CIRCULATING_SUPPLY)
    ax.set_ylim(bottom=-0.03, top=0.02)
    ax.grid(True, which="both", linestyle="--", linewidth=0.5)
    ax.axhline(y=0, color="k", linewidth=0.5)
    ax.axvline(x=0, color="k", linewidth=0.5)

    fig.savefig(output_path, dpi=fig.dpi)
    plt.close(fig)


def _title_for(curve) -> str:
    return curve.__name__.replace("_", " ").title()


plots_root = Path(__file__).resolve().parent / "plots"
plots_root.mkdir(parents=True, exist_ok=True)

stake_cap_catalogue = {}
curve_functions = []

for curve in curves:
    params = fix_parameters(curve)
    stake_cap_catalogue[curve.__name__] = params

    curve_fn = partial(curve, params["k"], params["b"])
    curve_functions.append((_title_for(curve), curve_fn))

    curve_plot_dir = plots_root / curve.__name__
    curve_plot_dir.mkdir(parents=True, exist_ok=True)

    title = _title_for(curve)
    _plot_real_yield(curve_fn, title, curve_plot_dir / "real_yield_plot.png")
    _plot_nominal_yield(curve_fn, title, curve_plot_dir / "nominal_yield_plot.png")
    _plot_issuance_curve(curve_fn, title, curve_plot_dir / "issuance_curve_plot.png")


combined_plot_dir = plots_root / "combined"
combined_plot_dir.mkdir(parents=True, exist_ok=True)

x = np.linspace(3200, CIRCULATING_SUPPLY, 240)

fig, ax = plt.subplots(figsize=(10, 6))

for title, curve_fn in curve_functions:
    nominal = percentage_yield(curve_fn(x))
    ax.plot(x, nominal, linewidth=2, label=f"{title}")

ax.set_title("Nominal Yield Comparison")
ax.xaxis.set_major_formatter(FuncFormatter(stake_formatter))
ax.set_xlabel("Stake (Millions of ETH)")
ax.set_ylabel("Yield (%)")
ax.set_ylim(bottom=-3, top=10)
ax.set_xlim(left=0, right=CIRCULATING_SUPPLY)
ax.grid(True, which="both", linestyle="--", linewidth=0.5)
ax.axhline(y=0, color="k", linewidth=0.5)
ax.axvline(x=0, color="k", linewidth=0.5)
ax.legend(fontsize=12)

fig.savefig(combined_plot_dir / "nominal_yield_comparison_baguette.png", dpi=fig.dpi)
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 6))

for title, curve_fn in curve_functions:
    issuance_ratio = issuance(curve_fn, x) / CIRCULATING_SUPPLY
    ax.plot(x, issuance_ratio, linewidth=2, label=f"{title}")

ax.set_title("Issuance Curve Comparison")
ax.xaxis.set_major_formatter(FuncFormatter(stake_formatter))
ax.yaxis.set_major_formatter(FuncFormatter(issuance_formatter))
ax.set_xlabel("Stake (Millions of ETH)")
ax.set_ylabel("Issuance (%)")
ax.set_xlim(left=0, right=CIRCULATING_SUPPLY)
ax.set_ylim(bottom=-0.03, top=0.02)
ax.grid(True, which="both", linestyle="--", linewidth=0.5)
ax.axhline(y=0, color="k", linewidth=0.5)
ax.axvline(x=0, color="k", linewidth=0.5)
ax.legend(fontsize=12)

fig.savefig(combined_plot_dir / "issuance_curve_comparison_baguette.png", dpi=fig.dpi)
plt.close(fig)
