import numpy as np
import pickle
from scipy.optimize import differential_evolution, minimize

# Define the function to minimize
def objective_function(x):
    return x[0]**2 + np.sin(x[1])

# Define the bounds for each parameter
x0 = [0, 0]
bounds = [(-5, 5), (-5, 5)]  # Bounds for two parameters

# Run differential evolution optimization
results = minimize(objective_function, x0, method='Nelder-Mead', options={'disp':True}, tol=1e-4, bounds=bounds)

# Print the result
print("Optimal parameters:", results.x)
print("Optimal function value:", results.fun)

## Save the optimized result to a pickle file
with open('optimized_sav.pkl', 'wb') as fileObj:
    pickle.dump(results, fileObj)