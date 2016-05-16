import mdp
import numpy as np


x = np.random.random((100, 25))
pcanode1 = mdp.nodes.PCANode(output_dim=2)

pcanode1.train(x)
pcanode1.stop_training()

print pcanode1.explained_variance

