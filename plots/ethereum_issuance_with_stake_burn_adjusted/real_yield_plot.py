from yield_curves import ethereum_issuance_with_burn_yield_adjusted
from plots.real_yield_plot import plot
from common import CIRCULATING_SUPPLY

plot(ethereum_issuance_with_burn_yield_adjusted,
     title="Ethereum with Stake Burn Real Issuance Yield",
     circulating_supply=CIRCULATING_SUPPLY,
     filename="ethereum_real_yield_with_burn_plot.png")
