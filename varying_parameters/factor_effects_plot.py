# Factor effects plots showing effect of parameters on SA:V
import matplotlib.pyplot as plt
import numpy as np

NUM_FACTORS = 18
def hexcolors(): # generates NUM_FACTORS RGB colors in a spectrum from blue to red
  colors = []
  for i in range(NUM_FACTORS):
    n = i * 1024 / (NUM_FACTORS-1)
    if (n <= 255):
      r = 0
      g = n
      b = 255
    elif (n <= 511):
      r = 0
      g = 255
      b = 511 - n
    elif (n <= 767):  
      r = n - 512
      g = 255
      b = 0
    elif (n < 1024):
      r = 255
      g = 1023 - n
      b = 0
    else:
      r = 255
      g = 0
      b = 0
    colors.append((r/255, g/255, b/255))
  colors.reverse()
  return colors

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
c = 0
for k, v in paramdict.items():
    name = k
    x = np.array(['Min', 'Mean', 'Max'])
    sav = np.array([v[0], v[1], v[2]])
    ax.plot(x,sav, label=name, linewidth = 2.0, color = hexcolors()[c])
    ax.set_xlabel('Parameter')
    ax.set_ylabel('SA:V (1/cm)')
    ax.set_title('Effect of parameters on SA:V')
    c+=1
ax.legend(loc='upper right', ncols=2, fontsize='small')
plt.show()