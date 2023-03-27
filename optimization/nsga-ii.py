import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import pygmo as pg

# Define the Rosenbrock function
def rosenbrock(x):
    return np.sum(100.0*(x[1:]-x[:-1]**2.0)**2.0 + (1-x[:-1])**2.0)

# Define the constraint function for the disk
def disk_constraint(x):
    return x[0]**2 + x[1]**2 - 1.0

# Define the objective function for the NSGA-II algorithm
def rosenbrock_constrained(x):
    f1 = rosenbrock(x)
    f2 = disk_constraint(x)
    return [f1, f2]

# Define the optimization problem for the NSGA-II algorithm
class RosenbrockProblem:
    def __init__(self, dim):
        self.dim = dim
    
    def fitness(self, x):
        return rosenbrock_constrained(x)
    
    def get_bounds(self):
        return ([-5.0]*self.dim, [5.0]*self.dim)
    
    def get_name(self):
        return "RosenbrockProblem"

# Define the NSGA-II algorithm
algo = pg.algorithm(pg.nsga2(gen=100))

# Define the problem and the population
prob = pg.problem(RosenbrockProblem(dim=2))
pop = pg.population(prob, size=100)

# Run the optimization algorithm
pop = algo.evolve(pop)

# Retrieve the results
fits, vectors = pop.get_f(), pop.get_x()

# Plot the Pareto front
plt.scatter(fits[:,0], fits[:,1])
plt.xlabel('F1: Rosenbrock')
plt.ylabel('F2: Disk Constraint')
plt.title('Pareto Front for Rosenbrock Constrained to a Disk')
plt.show()


