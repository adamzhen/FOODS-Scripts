# read in attempt_3/all_normalized_inputs.txt

import numpy as np
import matplotlib.pyplot as plt

attempt = 'i' # attempt number
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

# find best scores
goodx = []
goodindata = []
for i in range(len(data[:, 1])):
    score = data[i, -1]
    if score < -40:
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
for i in range(0, len(params)):
  plt.scatter(x, indata[:, i], s=5, c='blue')
  plt.scatter(goodx, np.array(goodindata)[:, i], s=5, c='orange')
  plt.xlabel('Run No.')
  plt.ylabel(params[i])
  plt.title(f'{params[i]} vs Run No.')
  #plt.show()
  plt.savefig(f'optimization/attempt_{attempt}/{params[i]}_inputs.png')
  plt.close()