from yield_curves import ethereum_issuance_yield
from plots.real_yield_plot import plot
from common import CIRCULATING_SUPPLY

plot(ethereum_issuance_yield,
     title="Ethereum Issuance",
     circulating_supply=CIRCULATING_SUPPLY,
     filename="ethereum_real_yield_plot.png")
