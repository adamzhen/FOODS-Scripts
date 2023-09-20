import numpy as np
import matplotlib.pyplot as plt

attempt = '2.0' # attempt number
params = ["T", "T1", "T2", "L", "h4", "W3"]

# read in data
with open(f'optimization/attempt_{attempt}/all_run_data.txt', 'r') as f:
    all_data = [[float(x) for x in s.split(',')] for s in f.readlines()]

good_data = []
bad_runs = []
# catches bad runs
for i in range(len(all_data)):
    if len(all_data[i]) == 11:
        good_data.append(all_data[i])
    else:
        #print(i)
        bad_runs.append(all_data[i])
data = np.array(good_data)
indata = data[:, 0:6]

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
print(f'Attempt {attempt}, Best Score: {np.min(data[:, -1])}')

# plot stress in scatter plot
yvar = "Load_1_Stress"
x = np.arange(1, len(data)+1, 1)
plt.scatter(x, data[:, 7], s=5)
plt.xlabel('Run No.')
plt.ylabel(f'{yvar}')
plt.title(f'{yvar} vs Run No. (Attempt {attempt})')
#plt.show()
plt.savefig(f'optimization/attempt_{attempt}/{attempt}_{yvar.lower()}.png')
plt.close()

# plot stress in scatter plot
yvar = "Load_2_Stress"
x = np.arange(1, len(data)+1, 1)
plt.scatter(x, data[:, 9], s=5)
plt.xlabel('Run No.')
plt.ylabel(f'{yvar}')
plt.title(f'{yvar} vs Run No. (Attempt {attempt})')
#plt.show()
plt.savefig(f'optimization/attempt_{attempt}/{attempt}_{yvar.lower()}.png')
plt.close()

#################
### BEST RUNS ###
#################

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
			x_normalized[i] = round( (x[i] - bounds[0]) / domain,  5)
		## Denormalize
		else:
			x_normalized[i] = round( domain[i] * x[i] + bounds[0, i], 5)

	## If input was not an array, return a float
	return x_normalized

# read in and print metadata
print('\nMETADATA:')
with open(f'optimization/attempt_{attempt}/all_metadata.txt', 'r') as f:
    metadata = f.read().split('\n')
    # var_bounds
    var_bounds_ind = metadata.index('var_bounds') + 2
    var_bounds = np.array([[float(x) for x in metadata[var_bounds_ind].split(',')], [float(x) for x in metadata[var_bounds_ind+1].split(',')]])
    print(metadata[var_bounds_ind-1]) # parameter names
    print(var_bounds) # parameter bounds (var_bounds)
    # fork script metadata
    fork_script_ind = metadata.index('fork_script') + 1
    # create dictionary from 2 lists
    fork_script_metadata = dict(zip([x.strip() for x in metadata[fork_script_ind].split(',')], [float(x) for x in metadata[fork_script_ind+1].split(',')]))
    print(fork_script_metadata) # script version, yield stress, safety factor, stress threshold
print()
#var_bounds = np.array([[0.2, 0.1, 0.15, 14.0, 1.2, 0.2], [0.4, 0.4, 0.35, 20.0, 1.8, 0.4]])

# find best scores
for i in range(len(data[:, -1])):
    score = data[i, -1]
    if score < 1.21:
        inputs = [x.round(3) for x in normalize(indata[i, :], bounds=var_bounds, inverse=True)] # converts from normalized to actual & rounds to 3 decimal places
        print(f'{inputs} = {score}')

#print(normalize(np.array([0.984, 0.0, -0.0, 0.19, 0.208, 0.206]), bounds=var_bounds, inverse=True))