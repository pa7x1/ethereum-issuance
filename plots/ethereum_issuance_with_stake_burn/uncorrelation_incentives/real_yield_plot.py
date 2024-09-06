import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
from yield_curves import ethereum_issuance_with_burn_yield
from yields import real_issuance_yield, effective_holding_yield
from common import CIRCULATING_SUPPLY, percentage_yield

x = np.linspace(3200, CIRCULATING_SUPPLY, 240)


real_staking_yield_solo = percentage_yield(
    real_issuance_yield(
        issuance_yield=ethereum_issuance_with_burn_yield(x),
        supply=CIRCULATING_SUPPLY,
        staked=x,
        fixed_costs=1 / 1000,
        scaling_costs=0.35,
        anticorrelation_incentives=0.))
real_staking_yield_lst_correlated = percentage_yield(
    real_issuance_yield(
        issuance_yield=ethereum_issuance_with_burn_yield(x),
        supply=CIRCULATING_SUPPLY,
        staked=x,
        fixed_costs=0.,
        scaling_costs=0.14,
        anticorrelation_incentives=-0.004))
real_staking_yield_lst_uncorrelated = percentage_yield(
    real_issuance_yield(
        issuance_yield=ethereum_issuance_with_burn_yield(x),
        supply=CIRCULATING_SUPPLY,
        staked=x,
        fixed_costs=0.,
        scaling_costs=0.14,
        anticorrelation_incentives=-0.002))
real_staking_yield_institutional = percentage_yield(
    real_issuance_yield(
        issuance_yield=ethereum_issuance_with_burn_yield(x),
        supply=CIRCULATING_SUPPLY,
        staked=x,
        fixed_costs=1 / 10000,
        scaling_costs=0.25,
        anticorrelation_incentives=-0.006))

real_holding_yield = percentage_yield(
    effective_holding_yield(
        issuance_yield=ethereum_issuance_with_burn_yield(x),
        supply=CIRCULATING_SUPPLY,
        staked=x))

fig = plt.figure(figsize=(10, 6))

plt.plot(x, real_staking_yield_solo, label="Real Issuance Yield Home Validator", color="blue", linewidth=1)
plt.plot(x, real_staking_yield_lst_correlated, label="Real Issuance Yield LST Correlated", color="green", linewidth=1)
plt.plot(x, real_staking_yield_lst_uncorrelated, label="Real Issuance Yield LST Uncorrelated", color="purple", linewidth=1)
plt.plot(x, real_staking_yield_institutional, label="Real Issuance Yield Institutional", color="orange", linewidth=1)
plt.plot(x, real_holding_yield, label="Real Holding Yield", color="red", linewidth=1)

# Add titles and labels
plt.title("Ethereum with Stake Burn and Uncorrelation Real Issuance Yield")


def custom_formatter(x, pos):
    return f'{x / 1_000_000.:.0f}'


plt.gca().xaxis.set_major_formatter(FuncFormatter(custom_formatter))
plt.xlabel('Stake (Millions of ETH)')
plt.ylabel('Yield (%)')
plt.ylim(top=10, bottom=-3)
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.axhline(y=0, color='k', linewidth=0.5)
plt.axvline(x=0, color='k', linewidth=0.5)
plt.legend(fontsize=12)
plt.show()
fig.savefig('./ethereum_real_yield_with_burn_uncorrelation_plot.png', dpi=fig.dpi)