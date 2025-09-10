from yield_curves import log_issuance_with_burn_yield
from plots.real_yield_plot import plot
from common import CIRCULATING_SUPPLY

plot(log_issuance_with_burn_yield,
     title="Log Issuance with Stake Burn",
     circulating_supply=CIRCULATING_SUPPLY,
     filename="ethereum_real_yield_with_burn_plot.png")
