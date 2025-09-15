import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
from yields import real_issuance_yield, effective_holding_yield
from common import CIRCULATING_SUPPLY, percentage_yield
from plots.formatters import stake_formatter
from cost_structure import home_staking, lst_staking, institutional_staking
from yield_curves import ethereum_issuance_yield
from typing import Callable


def inverse_yield_function(yield_curve: Callable,
         title: str,
         circulating_supply: float = CIRCULATING_SUPPLY,
         filename: str = "real_yield_plot.png") -> None:

    x = np.linspace(3200, circulating_supply * 0.99, 240)


    real_staking_yield_lst = percentage_yield(
        real_issuance_yield(
            issuance_yield=yield_curve(x),
            supply=circulating_supply,
            staked=x,
            **lst_staking))

    real_holding_yield = percentage_yield(
        effective_holding_yield(
            issuance_yield=yield_curve(x),
            supply=circulating_supply,
            staked=x))

    yield_delta = real_staking_yield_lst - real_holding_yield


    fig = plt.figure(figsize=(10, 6))

    plt.plot(yield_delta, x, label="Issuance Yield Risk Premium", color="purple", linewidth=1, linestyle="--")

    # Add titles and labels
    plt.title(title)

    plt.ylabel('Stake (Millions of ETH)')
    plt.xlabel('Yield (%)')
    plt.gca().yaxis.set_major_formatter(FuncFormatter(stake_formatter))
    plt.xlim(0, 10)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.axhline(y=0, color='k', linewidth=0.5)
    plt.axvline(x=0, color='k', linewidth=0.5)
    plt.legend(fontsize=12)
    plt.show()
    fig.savefig(f'./{filename}', dpi=fig.dpi)
    return

inverse_yield_function(ethereum_issuance_yield,
                       "Stake as a Function of Issuance Yield",
                       circulating_supply=CIRCULATING_SUPPLY,
                       filename="inverse_function.png")