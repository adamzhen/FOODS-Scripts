import numpy as np
from scipy.optimize import minimize, Bounds

bounds = Bounds([0.2, 0.02, 0.02, 13.0, 1.0, 0.1], [0.4, 0.1, 0.15, 17.0, 1.6, 0.3])

print(bounds.lb)