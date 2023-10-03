import numpy as np
import pickle
from scipy.optimize import differential_evolution

# Define the function to minimize
def simple_function(x):
    return x[0]**2 + np.sin(x[1])

# Define the bounds for each parameter
bounds = [(-5, 5), (-5, 5)]  # Bounds for two parameters

# Run differential evolution optimization
results = differential_evolution(simple_function, bounds)

# Print the result
print("Optimal parameters:", results.x)
print("Optimal function value:", results.fun)

## Save the optimized result to a pickle file
with open('optimized_sav.pkl', 'wb') as fileObj:
    pickle.dump(results, fileObj)