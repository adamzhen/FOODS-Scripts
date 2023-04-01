import subprocess as sp

import pickle
import numpy as np
from scipy.optimize import minimize

"""
Updates to the Abaqus scripts:
1. Read in design variables
2. Automatically apply pressure data
3. Call jobs and post process the odb
4. Write an output text file that writes out the max strain
"""
#----------------------------------------------------------
# GENERAL FUNCTIONS
#----------------------------------------------------------
def normalize(x, bounds, inverse=False):
    """
    Description
    -----------
    Function that normalizes (or denormalizes) x

    Parameters
    ----------
    x:              NUMPY ARRAY
                    input array to be normalized or unnormalized

    bounds:         NUMPY ARRAY
                    bounds used to normalize the vector x
                    (e.g., np.array([lower bound, upper bound]))

    inverse:        BOOLEAN
                    "True" to normalize x between [0, 1]
                    "False" to denormalize

    Returns
    -------
    x_normalized:   NUMPY ARRAY
                    output array of normalized or unnormalized values
    """

    ## Check if 'x' is a numpy array
    flag = isinstance(x, np.ndarray)
    if not flag:
        x = np.array([x])

    x_normalized = np.zeros((np.size(x)))

    domain = bounds[1] - bounds[0]
    for i in range(len(x)):
        ## Normalize to [0,1]
        if not inverse:
            x_normalized[i] = (x[i] - bounds[0]) / domain

        ## Denormalize
        else:
            x_normalized[i] = domain * x[i] + bounds[0]

    ## If input was not an array, return a float
    if not flag:
        return float(x_normalized)
    else:
        return x_normalized


#----------------------------------------------------------
# OPTIMIZATION FUNCTIONS
#----------------------------------------------------------

def objective_function(x, abaqus_script='open_aircraft_design_cae.py'):
    """
    Description
    -----------
    [TYPE DESCRIPTION HERE]

    Inputs
    ------
    x:                        NUMPY ARRAY

    abaqus_script:            STRING

    Returns
    -------
    max_strain_normalized:    FLOAT

    """

    # results = pickle.load(open('optimized_skin_thickness.pkl','rb'))

    ## Normalize input variables
    skin_thickness_bounds = np.array([0.1, 6.0]) # mm
    skin_thickness = normalize(x, bounds=skin_thickness_bounds, inverse=True)

    ## Write input variable to text file for Abaqus script to read
    with open('inputs.txt', 'w') as fileObj:
        fileObj.write(str(skin_thickness[0]))

    with open('all_inputs.txt', 'a') as fileObj:
        fileObj.write(str(skin_thickness[0]) + '\n')

    ## Call Abaqus and wait for analysis to complete
    script_name = abaqus_script
    command_file = r'abaqus cae nogui=' + script_name

    ## Define the script name and command line for the terminal
    ps = sp.Popen(command_file, shell=True)
    ps.wait()

    ## Read results file to get the maximum strain in the skin
    with open('outputs.txt', 'r') as fileObj:
        line = fileObj.readlines()[0]
        U = float(line.split()[0])

    return U

def jac(x):
    ## Open all previous inputs
    with open('all_inputs.txt', 'r') as fileObj:
        inputs = fileObj.readlines()

    ## Open all previous outputs
    with open('all_outputs.txt', 'r') as fileObj:
        outputs = fileObj.readlines()

    ## Grab the last two input values
    input_0 = float(inputs[-2].split()[0])
    input_1 = float(inputs[-1].split()[0])

    ## Grab the last two output values
    output_0 = float(outputs[-2].split()[-1])
    output_1 = float(outputs[-1].split()[-1])

    ## Calculate an approximate U' value using the finite-difference approximation
    U_prime = (output_1 - output_0) / (input_1 - input_0)

    return U_prime


#----------------------------------------------------------
# OPTIMIZATION INTERFACE
#----------------------------------------------------------
x0s = [0.0, 1.0]
for x0 in x0s:
    run_U = objective_function(np.array([x0]))

## Initial total skin thickness guess
x0 = 0.9 # [0.0, 1.0]

final_skin_thickness = minimize(objective_function, x0, method='Nelder-Mead', \
    options={'disp':True}, tol=1e-4)

## Save the optimized skin thickness to a pickle file
with open('optimized_skin_thickness.pkl', 'wb') as fileObj:
    pickle.dump(final_skin_thickness, fileObj)
