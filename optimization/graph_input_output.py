import numpy as np
import matplotlib.pyplot as plt

attempt = 5 # attempt number
params = ["T", "T1", "T2", "L", "h4", "W3"]

# read in data
indata = np.loadtxt(f'optimization/attempt_{attempt}/all_normalized_inputs.txt', delimiter=',')

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

# read in data
data = np.loadtxt(f'optimization/attempt_{attempt}/all_outputs.txt', delimiter=',')
data = data[data[:,0] == 2] # only taking final outputs from the 2nd run

# plot score in scatter plot
yvar = "Score"
x = np.arange(1, len(data)+1, 1)
plt.scatter(x, data[:, 1], s=5)
plt.xlabel('Run No.')
plt.ylabel(f'{yvar}')
plt.title(f'{yvar} vs Run No. (Attempt {attempt})')
#plt.show()
plt.savefig(f'optimization/attempt_{attempt}/{attempt}_{yvar.lower()}.png')
plt.close()
print(f'Attempt {attempt}, Best Score: {np.min(data[:, 1])}')

# plot stress in scatter plot
yvar = "Stress"
x = np.arange(1, len(data)+1, 1)
plt.scatter(x, data[:, 3], s=5)
plt.xlabel('Run No.')
plt.ylabel(f'{yvar}')
plt.title(f'{yvar} vs Run No. (Attempt {attempt})')
#plt.show()
plt.savefig(f'optimization/attempt_{attempt}/{attempt}_{yvar.lower()}.png')
plt.close()

# find best scores
# for i in range(len(data[:, 1])):
#     score = data[i, 1]
#     if score < -40:
#         inputs = indata[i, :]
#         print(f'{inputs} = {score}')
