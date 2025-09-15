from yield_curves import quadratic_burn
from plots.real_yield_plot import plot
from common import CIRCULATING_SUPPLY

plot(quadratic_burn,
     title="Quadratic Burn",
     circulating_supply=CIRCULATING_SUPPLY,
     filename="ethereum_real_yield_with_burn_plot.png")
