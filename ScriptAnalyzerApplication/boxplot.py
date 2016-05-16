import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(1)

p = ax.pcolormesh(np.random.randn(10,10))
fig.colorbar(p)
plt.show()