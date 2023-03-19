# Analyzing parameters using SA:V data

import matplotlib.pyplot as plt
import numpy as np
from statistics import mean, stdev

NUM_FACTORS = 7
loadn = 2
# read in data
with open(f'fullfactorial_analysis_data/PostDataFF1Load{loadn}.txt', 'r') as f:
    data = [row.split(', ') for row in f.read().split('\n')]
    header = data.pop(0)
    data.pop() # removes last empty row
    for i in range(len(data)): # converting strings to floats
        for j in range(0, len(data[i])):
            if j==9: # this column is a string
              data[i][j] = data[i][j]
            else: # all other columns are floats
              data[i][j] = float(data[i][j])

# print(header)

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

# Factor Effects Analysis
with open(f'fullfactorial_analysis_data/factor_impact_ranks_load{loadn}.txt', 'w') as f: # generates text file with factors ranked by impact for each criteria
  if loadn == 1:
    criteria = ['Max Mises Stress (Pa)', 'Max Displacement (cm)', 'Max Strain', 'Node 1 Displacement (cm)', 'Node 2 Displacement (cm)', 'SAV (1/cm)']
  elif loadn == 2:
    criteria = ['Max Mises Stress (MPa)', 'Max Displacement (cm)', 'Max Strain', 'Node 1 Displacement (cm)', 'Node 2 Displacement (cm)', 'SAV (1/cm)']
  f.write(f" , {', '.join(criteria)}\n")
  rankstrings = header[2:9]
  for c in criteria:
    if "(" in c:
      dispc = c[:c.index("(")-1] # removes units for display
    else:
      dispc = c
    ind = header.index(c) # index of column to analyze
    alphabet = ['a','b','c','d','e','f','g','h','i'] # used for treatment combinations
    factors = alphabet[:NUM_FACTORS]
    fig, ax = plt.subplots()
    averages = [] # list of average criterion values for the min and max values of each factor
    factordict = {} # dictionary of factor names and their impact measures
    for i in range(len(factors)): # for each factor letter
      factor = factors[i]
      name = header[i+2]
      mins = []
      maxs = []
      for d in data: # finding the data points where the factor is at its min or max
        if factor in d[9]: # if the factor's treatment letter is in the treatment combination
            maxs.append(d[ind])
        else:
            mins.append(d[ind])
      averages.append([mean(maxs), mean(mins)])
      # Calculating difference (impact measure)
      score = (averages[i][0] - averages[i][1])
      factordict[name] = abs(score)
      sortedfactors = sorted(factordict.items(), reverse=True, key=lambda x:x[1])
      rankedfactors = [x[0] for x in sortedfactors] # list of factor names in order of impact
    # Creating factor effects plots
    for i in range(len(factors)):
      name = header[i+2]
      rank = rankedfactors.index(name) # rank from 0 to NUM_FACTORS-1, with 0 being the most impactful
      rankstrings[i] += f", {rank+1}"
      x = np.array(['Min', 'Max'])
      y = np.array([averages[i][1], averages[i][0]])
      ax.plot(x,y, label=name, linewidth = 2.0, color = hexcolors()[i])
      ax.set_xlabel('Parameter')
      ax.set_ylabel(c)
      ax.set_title(f'Effect of parameters on {dispc}')
      ax.legend(loc='upper right', ncols=2, fontsize='small')
    plt.savefig(f'fullfactorial_analysis_data/FF1Load{loadn} Factor Effects {dispc}.png')
    plt.close()
    print(f"{dispc}")
  for row in rankstrings:
      f.write(f"{row}\n")