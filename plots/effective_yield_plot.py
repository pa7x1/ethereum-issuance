import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
from common import percentage_yield, CIRCULATING_SUPPLY
from yields import effective_issuance_yield, effective_holding_yield

x = np.linspace(0, CIRCULATING_SUPPLY, 240)
eff_staking_yield = percentage_yield(effective_issuance_yield(issuance_yield=1.05, supply=CIRCULATING_SUPPLY, staked=x))
eff_holding_yield = percentage_yield(effective_holding_yield(issuance_yield=1.05, supply=CIRCULATING_SUPPLY, staked=x))


fig = plt.figure(figsize=(10, 6))

plt.plot(x, eff_staking_yield, label="Effective Staking Yield", color="blue", linewidth=1)
plt.plot(x, eff_holding_yield, label="Effective Holding Yield", color="red", linewidth=1)


# Add titles and labels
plt.title("Effective Yield vs Stake Rate (y_s = 1.05)")
def custom_formatter(x, pos):
    return f'{x/1_000_000.:.0f}'


plt.gca().xaxis.set_major_formatter(FuncFormatter(custom_formatter))
plt.xlabel('Stake (Millions of ETH)')
plt.ylabel('Yield (%)')
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.axhline(y=0, color='k', linewidth=0.5)
plt.axvline(x=0, color='k', linewidth=0.5)
plt.legend(fontsize=12)
plt.show()
fig.savefig('./effective_yield.png', dpi=fig.dpi)