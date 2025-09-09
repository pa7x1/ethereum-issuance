import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
from issuance import issuance
from yield_curves import ethereum_issuance_with_burn_yield_adjusted, ethereum_issuance_yield
from common import CIRCULATING_SUPPLY
from plots.formatters import issuance_formatter, stake_formatter

x = np.linspace(3200, CIRCULATING_SUPPLY, 240)


issuance_plot = issuance(ethereum_issuance_with_burn_yield_adjusted, x) / CIRCULATING_SUPPLY

yield_at_target = ethereum_issuance_with_burn_yield_adjusted(30_000_000)
ethereum_yield_at_target = ethereum_issuance_yield(30_000_000)
print(f"{float(yield_at_target)=}")
print(f"{float(ethereum_yield_at_target)=}")

current_yield = ethereum_issuance_with_burn_yield_adjusted(35_700_000)
current_ethereum_yield = ethereum_issuance_yield(35_700_000)
print(f"{float(current_yield)=}")
print(f"{float(current_ethereum_yield)=}")


fig = plt.figure(figsize=(10, 6))

plt.plot(x, issuance_plot, color="blue", linewidth=1)

# Add titles and labels
plt.title("Ethereum's Issuance with Stake Burn Curve")

plt.gca().xaxis.set_major_formatter(FuncFormatter(stake_formatter))
plt.gca().yaxis.set_major_formatter(FuncFormatter(issuance_formatter))

plt.xlabel('Stake (Millions of ETH)')
plt.ylabel('Issuance (%)')
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.axhline(y=0, color='k', linewidth=0.5)
plt.axvline(x=0, color='k', linewidth=0.5)
plt.show()
fig.savefig('./ethereum_issuance_with_burn_plot.png', dpi=fig.dpi)