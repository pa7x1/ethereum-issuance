from yield_curves import tempered_issuance
from plots.real_yield_plot import plot
from common import CIRCULATING_SUPPLY

plot(tempered_issuance,
     title="Tempered Issuance",
     circulating_supply=CIRCULATING_SUPPLY,
     filename="tempered_issuance_real_yield_plot.png")
