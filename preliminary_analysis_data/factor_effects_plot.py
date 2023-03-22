# Factor effects plots showing effect of parameters on SA:V
import matplotlib.pyplot as plt
import numpy as np

NUM_FACTORS = 11
ind = 4 # index of data to be used for sorting
nameind = 2 # index of name of parameter
loadn = 2 # load case (1 or 2)

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
with open(f'preliminary_analysis_data/PostDataLoad{loadn}.txt', 'r') as f:
    data = [row.split(', ') for row in f.read().split('\n')]
    header = data.pop(0)
    data.pop() # removes last empty row
    for i in range(len(data)): # converting strings to floats
        for j in range(nameind+1, len(data[i])):
            data[i][j] = float(data[i][j])
# read in mean data
with open(f'preliminary_analysis_data/PostDataLoad{loadn}Mean.txt', 'r') as f:
    mdata = [row.split(', ') for row in f.read().split('\n')]
    mdata.pop(0)
    mdata.pop() # removes last empty row
    mean = float(mdata[0][ind]) # changes depending on load case (just because the data for the two was formatted differently)

# Sorting Data by impact on SA:V
paramdict = {}
for i in range(0, len(data), 2):
    p1 = data[i]
    p2 = data[i+1]
    score = (p2[ind]-p1[ind]) #/ (p2[1]-p1[1])
    paramdict[p1[nameind]] = abs(score)
    #print(f"{p1[0]}: {score:.4f}")
paramdict = dict(sorted(paramdict.items(), reverse=True, key=lambda x:x[1]))

datadict = {}
for i in range(0, len(data), 2):
    datadict[data[i][nameind]] = [data[i][ind], mean, data[i+1][ind]]
for k, v in paramdict.items():
    paramdict[k] = datadict[k]

# paramdict.pop('T2')
# paramdict.pop('T')
print(paramdict)
# Plotting Data
fig, ax = plt.subplots()
c = 0
for k, v in paramdict.items():
    name = k
    x = np.array(['Min', 'Mean', 'Max'])
    y = np.array([v[0], v[1], v[2]])
    ax.plot(x,y, label=name, linewidth = 2.0, color = hexcolors()[c])
    ax.set_xlabel('Parameter')
    ax.set_ylabel('Max Mises Stress (Pa)')
    ax.set_title(f'Effect of parameters on Max Mises Stress (Load Case {loadn})')
    c+=1
ax.legend(loc='upper right', ncols=2, fontsize='medium')
plt.show()