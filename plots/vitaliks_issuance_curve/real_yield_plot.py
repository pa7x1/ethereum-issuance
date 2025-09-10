from yield_curves import vitaliks_issuance_yield
from plots.real_yield_plot import plot
from common import CIRCULATING_SUPPLY

plot(vitaliks_issuance_yield,
     title="Vitalik's Stake Capping",
     circulating_supply=CIRCULATING_SUPPLY,
     filename="vitalik_real_yield_plot.png")
