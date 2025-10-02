import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

def logistic_decreasing(x, x0=0.0, k=1.0):
    return 1.0 / (1.0 + np.exp(k * (x - x0)))

# Apply a global "sketch" effect: (scale, length, randomness)
mpl.rcParams["path.sketch"] = (1.0, 100.0, 2.0)

param_sets = [
    (0.0, 1.0),
    (-2.0, 0.6),
    (2.0, 1.4),
    (0.0, 0.4),
    (0.0, 2.0),
]

x = np.linspace(-20, 20, 2000)

plt.figure(figsize=(9, 6))
for (x0, k) in param_sets:
    y = logistic_decreasing(x, x0=x0, k=k)
    plt.plot(y, x, linewidth=2.0, )

plt.xlim(0, 1)
plt.ylim(-10, 10)
plt.xlabel(r"Stake Ratio")
plt.ylabel(r"$y_i$")
plt.title(r"Family of Issuance Yield Curves")
plt.grid(True, linestyle="--", alpha=0.4)
plt.tight_layout()
outpath = "./issuance_yield_family_handdrawn.png"
plt.savefig(outpath, dpi=160)
plt.show()