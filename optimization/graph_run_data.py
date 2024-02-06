## Run this script to graph the run data from the optimization
## Requisite files: all_metadata.txt, all_run_data.txt

import numpy as np
import matplotlib.pyplot as plt

attempt = '3.1' # attempt number

# converts between normalized inputs and actual inputs
def normalize(x, bounds, inverse=False):
	# Check if 'x' is a numpy array
	flag = isinstance(x, np.ndarray)
	if not flag:
		x = np.array([x])

	x_normalized = np.zeros((np.size(x)))

	domain = bounds[1] - bounds[0]

	for i in range(len(x)):
		## Normalize to [0,1]
		if not inverse:
			x_normalized[i] = np.round( (x[i] - bounds[0, i]) / domain[i], 5) 
		## Denormalize
		else:
			x_normalized[i] = np.round( domain[i] * x[i] + bounds[0, i], 5)

	## If input was not an array, return a float
	return x_normalized

### READ IN METADATA ###
print(f'Attempt {attempt}')
print('\nMETADATA:')
with open(f'optimization/attempt_{attempt}/all_metadata.txt', 'r') as f:
    metadata = f.read().split('\n')
    # var_bounds
    var_bounds_ind = metadata.index('var_bounds') + 2
    var_bounds = np.array([[float(x) for x in metadata[var_bounds_ind].split(',')], [float(x) for x in metadata[var_bounds_ind+1].split(',')]])
    params_str = metadata[var_bounds_ind-1]
    print(params_str) # parameter names
    print(var_bounds) # parameter bounds (var_bounds)
    # fork script metadata
    fork_script_ind = metadata.index('fork_script') + 1
    # create dictionary from 2 lists
    fork_script_metadata = dict(zip([x.strip() for x in metadata[fork_script_ind].split(',')], [float(x) for x in metadata[fork_script_ind+1].split(',')]))
    print(fork_script_metadata)
    nDATA = fork_script_metadata['nDATA']
print()

params = params_str.split(',')

### READ IN DATA ###
with open(f'optimization/attempt_{attempt}/all_run_data.txt', 'r') as f:
    all_data = [[float(x) for x in s.split(',')] for s in f.readlines()]

good_data = []
bad_runs = []
# catches bad runs
for i in range(len(all_data)):
    if len(all_data[i]) == (nDATA):
        good_data.append(all_data[i])
    else:
        #print(i)
        bad_runs.append(all_data[i])
data = np.array(good_data)
indata = data[:, 0:len(params)]

################
### PLOTTING ###
################

# plot normalized inputs
x = np.arange(1, len(indata)+1, 1)
plt.plot(x, indata, label=params)
plt.xlabel('Run No.')
plt.ylabel('Normalized Inputs')
plt.title(f'Normalized Inputs vs Run No. (Attempt {attempt})')
plt.legend(loc='lower right')
plt.ylim(0, 1)
#plt.show()
plt.savefig(f'optimization/attempt_{attempt}/{attempt}_normalized_inputs.png')
plt.close()

# plot score in scatter plot
yvar = "Score"
x = np.arange(1, len(data)+1, 1)
plt.scatter(x, data[:, -1], s=5)
plt.xlabel('Run No.')
plt.ylabel(f'{yvar}')
plt.title(f'{yvar} vs Run No. (Attempt {attempt})')
#plt.show()
plt.savefig(f'optimization/attempt_{attempt}/{attempt}_{yvar.lower()}.png')
plt.close()

# plot stress in scatter plot
yvar = "Load_1_Stress"
x = np.arange(1, len(data)+1, 1)
plt.scatter(x, data[:, 6], s=5)
plt.xlabel('Run No.')
plt.ylabel(f'{yvar}')
plt.title(f'{yvar} vs Run No. (Attempt {attempt})')
#plt.show()
plt.savefig(f'optimization/attempt_{attempt}/{attempt}_{yvar.lower()}.png')
plt.close()

# plot stress in scatter plot
yvar = "Load_2_Stress"
x = np.arange(1, len(data)+1, 1)
plt.scatter(x, data[:, 8], s=5)
plt.xlabel('Run No.')
plt.ylabel(f'{yvar}')
plt.title(f'{yvar} vs Run No. (Attempt {attempt})')
#plt.show()
plt.savefig(f'optimization/attempt_{attempt}/{attempt}_{yvar.lower()}.png')
plt.close()

# plot buckling in scatter plot
yvar = "Buckling"
x = np.arange(1, len(data)+1, 1)
plt.scatter(x, data[:, 10], s=5)
plt.xlabel('Run No.')
plt.ylabel(f'{yvar}')
plt.title(f'{yvar} vs Run No. (Attempt {attempt})')
#plt.show()
plt.savefig(f'optimization/attempt_{attempt}/{attempt}_{yvar.lower()}.png')
plt.close()

##### FIND BEST SCORES #####

threshold = -61

# find THE best score
best_score = min(data[:, -1])
# find index of best score
best_score_ind = np.where(data[:, -1] == best_score)[0][0]

# find inputs better than threshold
best_inputs_norm = []
with open(f'optimization/attempt_{attempt}/best_inputs.txt', 'w') as f:
    for i in range(len(data[:, -1])):
        score = data[i, -1]
        if score < threshold or i == best_score_ind or i == 0:
            inputs = [x.round(4) for x in normalize(indata[i, :], bounds=var_bounds, inverse=True)] # converts from normalized to actual & rounds to 3 decimal places
            norm_inputs = [x.round(4) for x in indata[i, :]]
            best_inputs_norm.append(norm_inputs)
            f.write(f'{inputs},  {score}\n')
            # Actual inputs for initial and best score
            if i == 0: 
                print(f'Initial Guess: {inputs} => {score}')
                print(f'Initial Guess: {norm_inputs} => {score}')
            if i == best_score_ind:
                print(f'Best Score: {inputs} => {score}')
                print(f'Best Score: {norm_inputs} => {score}')
print(f'\nInputs with score < {threshold} written to best_inputs.txt')

# plot best normalized input values vs parameter name
best_inputs_norm = np.array(best_inputs_norm)
x = np.arange(1, len(params)+1, 1)
plt.plot(x, best_inputs_norm.T, 'go') # green dots
plt.xlabel('Parameter')
plt.ylabel('Normalized Input')
plt.title(f'Normalized Inputs with score < {threshold} (Attempt {attempt})')
plt.ylim(0, 1)
plt.xticks(x, params)
#plt.show()
plt.savefig(f'optimization/attempt_{attempt}/{attempt}_best_norm_inputs.png')
plt.close()

# Convert to normalized inputs
#print(list(normalize(np.array([0.423, 0.022, 0.048, 14.26, 1.146, 0.272]), bounds=var_bounds, inverse=False)))

# Convert to actual inputs
# print(normalize(np.array([1.0, 0.25, 0.308, 0.25, 0.333, 0.5]), bounds=var_bounds, inverse=True))

# plot normalized inputs on bar graph with a bar extending from the lower bound to the best value, and one extending from the best to the upper bound (superimposed on each other). Please label the bounds and the best inputs with the actual values. Remember tat best_norm_inputs only has normalized inputs, they need to be converted to actual inputs
plt.figure(figsize=(10, 5))
x = np.arange(1, len(params)+1, 1)
BEST_INPUT_NORM = data[best_score_ind, :len(params)]
BEST_INPUT = normalize(BEST_INPUT_NORM, bounds=var_bounds, inverse=True)
lower_bounds = var_bounds[0]
upper_bounds = var_bounds[1]
width = 0.3
plt.bar(x, lower_bounds, width, label='Lower Bounds', color='r')
plt.bar(x, upper_bounds, width, label='Upper Bounds', color='b')
plt.bar(x, BEST_INPUT_NORM, width, label='Best Inputs', color='g')
plt.xlabel('Parameter')
plt.ylabel('Actual Input')
plt.title(f'Actual Inputs with Bounds and Best Inputs (Attempt {attempt})')
plt.xticks(x, params)
plt.legend(loc='upper right')
plt.show()




