import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
from issuance import issuance
from yield_curves import quadratic_burn
from common import CIRCULATING_SUPPLY
from plots.formatters import issuance_formatter, stake_formatter

x = np.linspace(3200, CIRCULATING_SUPPLY, 240)


issuance_plot = issuance(quadratic_burn, x) / CIRCULATING_SUPPLY



fig = plt.figure(figsize=(10, 6))

plt.plot(x, issuance_plot, color="blue", linewidth=1, label=r"$i(s) = R\sqrt{s} - B s^3$")

# Add titles and labels
plt.title("Ethereum's Issuance with Quadratic Stake Burn Curve")

plt.gca().xaxis.set_major_formatter(FuncFormatter(stake_formatter))
plt.gca().yaxis.set_major_formatter(FuncFormatter(issuance_formatter))

plt.xlabel('Stake (Millions of ETH)')
plt.ylabel('Issuance (%)')
plt.ylim(top=0.01, bottom=-0.03)
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.axhline(y=0, color='k', linewidth=0.5)
plt.axvline(x=0, color='k', linewidth=0.5)
plt.show()
fig.savefig('./ethereum_issuance_with_quadratic_burn_plot.png', dpi=fig.dpi)