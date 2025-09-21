import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator, AutoMinorLocator
import numpy as np
from yields import real_issuance_yield, effective_holding_yield
from common import CIRCULATING_SUPPLY, percentage_yield
from plots.formatters import stake_formatter
from cost_structure import home_staking, lst_staking, institutional_staking
from typing import Callable


def plot(yield_curve: Callable,
         title: str,
         circulating_supply: float = CIRCULATING_SUPPLY,
         filename: str = "real_yield_plot.png") -> None:

    x = np.linspace(3200, circulating_supply * 0.99, 240)


    real_staking_yield_solo = percentage_yield(
        real_issuance_yield(
            issuance_yield=yield_curve(x),
            supply=circulating_supply,
            staked=x,
            **home_staking))
    real_staking_yield_lst = percentage_yield(
        real_issuance_yield(
            issuance_yield=yield_curve(x),
            supply=circulating_supply,
            staked=x,
            **lst_staking))
    real_staking_yield_institutional = percentage_yield(
        real_issuance_yield(
            issuance_yield=yield_curve(x),
            supply=circulating_supply,
            staked=x,
            **institutional_staking))

    real_holding_yield = percentage_yield(
        effective_holding_yield(
            issuance_yield=yield_curve(x),
            supply=circulating_supply,
            staked=x))

    yield_delta = real_staking_yield_lst - real_holding_yield


    fig = plt.figure(figsize=(10, 6))

    plt.plot(x, real_staking_yield_solo, label="Issuance Real Yield Home Validator", color="blue", linewidth=1)
    plt.plot(x, real_staking_yield_lst, label="Issuance Real Yield LST", color="green", linewidth=1)
    plt.plot(x, real_staking_yield_institutional, label="Issuance Real Yield Institutional", color="orange", linewidth=1)
    plt.plot(x, real_holding_yield, label="Issuance Real Holding Yield", color="red", linewidth=1)
    plt.plot(x, yield_delta, label="(LST - Holding) Issuance Real Yield Delta", color="purple", linewidth=1, linestyle="--")

    # Add titles and labels
    plt.title(title)

    plt.gca().xaxis.set_major_formatter(FuncFormatter(stake_formatter))

    plt.gca().xaxis.set_major_locator(MultipleLocator(5_000_000))
    plt.gca().yaxis.set_major_locator(MultipleLocator(1))
    plt.xlabel('Stake (Millions of ETH)')
    plt.ylabel('Yield (%)')
    plt.ylim(top=10, bottom=-3)
    plt.xlim(left=0, right=120_000_000)
    plt.axhline(y=0, color='k', linewidth=0.5)
    plt.axvline(x=0, color='k', linewidth=0.5)

    plt.gca().xaxis.set_minor_locator(AutoMinorLocator(5))
    plt.gca().yaxis.set_minor_locator(AutoMinorLocator(5))
    plt.gca().grid(True, which='major', linestyle='--', linewidth=.6, alpha=.7)
    plt.gca().grid(True, which='minor', linestyle=':', linewidth=.4, alpha=.5)


    plt.legend(fontsize=12)
    plt.show()
    fig.savefig(f'./{filename}', dpi=fig.dpi)
    return