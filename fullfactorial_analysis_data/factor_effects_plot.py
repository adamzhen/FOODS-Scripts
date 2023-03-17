# Analyzing parameters using SA:V data

import matplotlib.pyplot as plt
import numpy as np
from statistics import mean, stdev

# read in data
with open('fullfactorial_analysis_data/PostDataFF1Load1.txt', 'r') as f:
    data = [row.split(', ') for row in f.read().split('\n')]
    header = data.pop(0)
    data.pop() # removes last empty row
    for i in range(len(data)): # converting strings to floats
        for j in range(0, len(data[i])):
            if j==9: # this column is a string
              data[i][j] = data[i][j]
            else: # all other columns are floats
              data[i][j] = float(data[i][j])

print(header)
method = 2 # 1 for max-min, 2 for deviation from mean

# Factor Effects Analysis
NUM_FACTORS = 7
criteria = ['Max Mises Stress (Pa)', 'Max Displacement (cm)', 'Max Strain', 'Node 1 Displacement (cm)', 'Node 2 Displacement (cm)', 'SAV (1/cm)']
for c in criteria:
  if "(" in c:
     dispc = c[:c.index("(")-1] # removes units for display
  ind = header.index(c) # index of column to analyze
  alphabet = ['a','b','c','d','e','f','g','h','i'] # used for treatment combinations
  factors = alphabet[:NUM_FACTORS]
  fig, ax = plt.subplots()
  for i in range(len(factors)):
    factor = factors[i]
    mins = []
    maxs = []
    for d in data:
      if factor in d[9]:
          maxs.append(d[ind])
      else:
          mins.append(d[ind])
    # Creating factor effects plots
    name = header[i+2]
    x = np.array(['Min', 'Max'])
    y = np.array([mean(mins), mean(maxs)])
    ax.plot(x,y, label=name, linewidth = 2.0)
    ax.set_xlabel('Parameter')
    ax.set_ylabel(c)
    ax.set_title(f'Effect of parameters on {dispc}')
    ax.legend(loc='upper right', ncols=2, fontsize='small')
  plt.savefig(f'fullfactorial_analysis_data/FF1Load1 Factor Effects {dispc}.png')
  plt.close()
  print(f"{dispc}")
