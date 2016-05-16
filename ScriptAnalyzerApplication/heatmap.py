import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(1)

np.random.seed(10)

p = np.asarray([[1,2],[2,3]])

#ax.pcolor(np.random.randn((10,10)))
#ax.pcolor(np.random.randn(10), np.random.randn(10))
p = ax.pcolormesh(p)
fig.colorbar(p)
plt.show()