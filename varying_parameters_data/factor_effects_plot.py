# Factor effects plots showing effect of parameters on SA:V
import matplotlib.pyplot as plt
import numpy as np

# read in data
with open('varying_parameters_data/VaryingParametersCSV3.txt', 'r') as f:
    data = [row.split(', ') for row in f.read().split('\n')]
    header = data.pop(0)
    data.pop() # removes last empty row
    for i in range(len(data)): # converting strings to floats
        for j in range(1, len(data[i])):
            data[i][j] = float(data[i][j])

# Sorting Data by impact on SA:V
paramdict = {}
for i in range(0, len(data), 3):
    p1 = data[i]
    p2 = data[i+1]
    p3 = data[i+2]
    score = (p3[-1]-p1[-1]) #/ (p2[1]-p1[1])
    paramdict[p1[0]] = abs(score)
    #print(f"{p1[0]}: {score:.4f}")
paramdict = dict(sorted(paramdict.items(), reverse=True, key=lambda x:x[1]))

datadict = {}
for i in range(0, len(data), 3):
    datadict[data[i][0]] = [data[i][5], data[i+1][5], data[i+2][5]]
for k, v in paramdict.items():
    paramdict[k] = datadict[k]

paramdict.pop('T2')
paramdict.pop('T')

# Plotting Data
fig, ax = plt.subplots()
for k, v in paramdict.items():
    name = k
    x = np.array(['Min', 'Mean', 'Max'])
    sav = np.array([v[0], v[1], v[2]])
    ax.plot(x,sav, label=name, linewidth = 2.0)
    ax.set_xlabel('Parameter')
    ax.set_ylabel('SA:V (1/cm)')
    ax.set_title('Effect of parameters on SA:V')
ax.legend(loc='upper right', ncols=2, fontsize='small')
plt.show()