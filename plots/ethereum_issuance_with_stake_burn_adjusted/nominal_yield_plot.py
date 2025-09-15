import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
from yield_curves import ethereum_issuance_with_burn_yield_adjusted
from common import CIRCULATING_SUPPLY, percentage_yield
from plots.formatters import issuance_formatter, stake_formatter

x = np.linspace(3200, CIRCULATING_SUPPLY, 240)


nominal_issuance_yield = percentage_yield(ethereum_issuance_with_burn_yield_adjusted(x))

fig = plt.figure(figsize=(10, 6))

plt.plot(x, nominal_issuance_yield,  color="blue", linewidth=1, label=r"$i(s) = R \frac{1}{\sqrt{s}} - B \log s$")

# Add titles and labels
plt.title("Ethereum's Issuance with Stake Burn Nominal Yield")

plt.gca().xaxis.set_major_formatter(FuncFormatter(stake_formatter))
plt.xlabel('Stake (Millions of ETH)')
plt.ylabel('Yield (%)')
plt.legend()
plt.ylim(top=10, bottom=-3)
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.axhline(y=0, color='k', linewidth=0.5)
plt.axvline(x=0, color='k', linewidth=0.5)
plt.show()
fig.savefig('./ethereum_nominal_yield_with_burn_plot.png', dpi=fig.dpi)