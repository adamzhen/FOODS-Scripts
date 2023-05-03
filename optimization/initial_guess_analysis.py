# read in attempt_3/all_normalized_inputs.txt

import numpy as np
import matplotlib.pyplot as plt

attempt = 'i1' # attempt number
params = ["T", "T1", "T2", "L", "h4", "W3"]

# read in data
indata = np.loadtxt(f'optimization/attempt_{attempt}/all_normalized_inputs.txt', delimiter=',')
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
goodx = []
goodindata = []
for i in range(len(data[:, 1])):
    score = data[i, 1]
    if score < -30:
        inputs = indata[i, :]
        goodx.append(i)
        goodindata.append(inputs)
        print(f'{i}: {inputs} = {score}')

# plot successful normalized inputs
x = np.arange(1, len(indata)+1, 1)
plt.scatter(indata[:, 4], indata[:, 5], s=5, c='blue')
plt.scatter(np.array(goodindata)[:, 4], np.array(goodindata)[:, 5], s=5, c='orange')
plt.xlabel(params[4])
plt.ylabel(params[5])
plt.title(f'{params[5]} vs {params[4]}')
#plt.show()
plt.savefig(f'optimization/attempt_{attempt}/{params[5]}_vs_{params[4]}_inputs.png')
plt.close()
for i in range(4, len(params)):
  plt.scatter(x, indata[:, i], s=5, c='blue')
  plt.scatter(goodx, np.array(goodindata)[:, i], s=5, c='orange')
  plt.xlabel('Run No.')
  plt.ylabel(params[i])
  plt.title(f'{params[i]} vs Run No.')
  #plt.show()
  plt.savefig(f'optimization/attempt_{attempt}/{params[i]}_inputs.png')
  plt.close()