import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import TwoSlopeNorm

minN = 20
maxN = 25
visLen = 1000
save = False
vis = np.zeros((visLen, visLen))

for n in range(minN, maxN + 1):
    data = np.loadtxt(f"../../data/Sorted_Costas_arrays_N={n}.txt", skiprows=1, dtype=int)
    count = len(data)
    print(f"N={n}: {count} arrays")

    grid = np.zeros((n, n))
    np.add.at(grid, (data, np.arange(n)), 1)

    grid = grid / count * n

    idx = np.arange(visLen) * n // visLen
    vis += grid[np.ix_(idx, idx)]

vis /= (maxN - minN + 1)

plt.imshow(vis, origin="lower", cmap="RdBu_r", norm=TwoSlopeNorm(vcenter=1))
plt.colorbar(label="relative density of solutions")
plt.title(f"Costas @ N={minN}..{maxN} overlaid")

if save:
    plt.savefig(f"../../art/costas_density_N={minN}-{maxN}.png", dpi=200, bbox_inches="tight")

plt.show()
