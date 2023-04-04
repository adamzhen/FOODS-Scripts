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

	# Check if 'x' is a numpy array
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
			x_normalized[i] = domain[i] * x[i] + bounds[0, i]
	
	## If input was not an array, return a float
	return x_normalized


#----------------------------------------------------------
# OPTIMIZATION FUNCTIONS
#----------------------------------------------------------

def objective_function(x, abaqus_script='Abaqus_Fork_Script.py', post_script='Abaqus_Post_Processing.py'):
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

	## Normalize input variables [cm]
	# T, T1, T2, L, h4, W3
	var_bounds = np.array([[0.2, 0.1, 0.15, 14.0, 1.2, 0.2], [0.4, 0.4, 0.35, 20.0, 1.8, 0.4]])
	#var_bounds = np.array([[0.2, 0.4], [0.1, 0.4], [0.15, 0.35], [14.0, 20.0], [1.2, 1.8], [0.2, 0.4]])
	vars = normalize(x, bounds=var_bounds, inverse=True)
	print vars

	## Write input variable to text file for Abaqus script to read
	strvars = ','.join([str(v) for v in vars])
	with open('inputs.txt', 'w') as fileObj:
		fileObj.write(strvars)

	with open('all_inputs.txt', 'a') as fileObj:
		fileObj.write(strvars + '\n')

	## Call Abaqus and wait for analysis to complete
	print abaqus_script
	command_file = r'abaqus cae nogui=' + abaqus_script
	ps = sp.Popen(command_file, shell=True) ## Define the script name and command line for the terminal
	ps.wait()
	
	## Run post script to get results
	# print post_script
	# command_file = r'abaqus cae nogui=' + post_script
	# ps = sp.Popen(command_file, shell=True) ## Define the script name and command line for the terminal
	# ps.wait()

	## Read results file to get the maximum strain in the skin
	with open('outputs.txt', 'r') as fileObj:
		line = fileObj.readlines()[0]
		score = float(line.split()[0])
	
	print score
	print ('Run Completed') 
	
	return score

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

with open('all_inputs.txt', 'w') as fileObj:
	fileObj.write('')

#----------------------------------------------------------
# OPTIMIZATION INTERFACE
#----------------------------------------------------------
# x0s = [0.0, 1.0]

## Initial total skin thickness guess
# T, T1, T2, L, h4, W3
x0 = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0]) # [0.0, 1.0]

#run_U = objective_function(x0)

final_sav = minimize(objective_function, x0, method='Nelder-Mead', 
    options={'disp':True}, tol=1e-4)

## Save the optimized skin thickness to a pickle file
with open('optimized_sav.pkl', 'wb') as fileObj:
    pickle.dump(final_sav, fileObj)
