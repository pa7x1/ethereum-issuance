import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, AutoMinorLocator, MaxNLocator, MultipleLocator
import numpy as np
from issuance import issuance
from yield_curves import quadratic_burn, ethereum_issuance_yield, ethereum_issuance_with_burn_yield_adjusted
from common import CIRCULATING_SUPPLY, percentage_yield
from plots.formatters import issuance_formatter, stake_formatter

x = np.linspace(3200, CIRCULATING_SUPPLY, 240)


ethereum_issuance_curve = issuance(ethereum_issuance_yield, x) / CIRCULATING_SUPPLY
quadratic_burn_curve = issuance(quadratic_burn, x) / CIRCULATING_SUPPLY
log_burn_curve = issuance(ethereum_issuance_with_burn_yield_adjusted, x) / CIRCULATING_SUPPLY


fig = plt.figure(figsize=(10, 6))

plt.plot(x, ethereum_issuance_curve,  color="red", linewidth=1, label=r"Ethereum's Issuance Curve")
plt.plot(x, quadratic_burn_curve,  color="blue", linewidth=1, label=r"Proposal with Quadratic Burn")
plt.plot(x, log_burn_curve,  color="purple", linewidth=1, label=r"Proposal with Log Burn")


# Add titles and labels
plt.title("Ethereum's Issuance Curve vs Proposed Stake Capping Issuance Curves")

plt.gca().xaxis.set_major_formatter(FuncFormatter(stake_formatter))
plt.gca().yaxis.set_major_formatter(FuncFormatter(issuance_formatter))

plt.gca().xaxis.set_major_locator(MultipleLocator(5_000_000))
plt.gca().yaxis.set_major_locator(MultipleLocator(0.005))
plt.xlabel('Stake (Millions of ETH)')
plt.ylabel('Issuance (%)')
plt.xlim(left=0, right=120_000_000)
plt.ylim(bottom=-0.03)
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.axhline(y=0, color='k', linewidth=0.5)
plt.axvline(x=0, color='k', linewidth=0.5)

plt.gca().xaxis.set_minor_locator(AutoMinorLocator(5))
plt.gca().yaxis.set_minor_locator(AutoMinorLocator(5))
plt.gca().grid(True, which='major', linestyle='--', linewidth=.6, alpha=.7)
plt.gca().grid(True, which='minor', linestyle=':',  linewidth=.4, alpha=.5)

plt.show()
fig.savefig('./issuance_curve_comparison.png', dpi=fig.dpi)