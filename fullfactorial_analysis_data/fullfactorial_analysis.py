# Analyzing parameters using SA:V data

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
criteria = []
ind = -1 # index of column to analyze
alphabet = ['a','b','c','d','e','f','g','h','i'] # used for treatment combinations
factors = alphabet[:NUM_FACTORS]
for i in range(len(factors)):
  factor = factors[i]
  mins = []
  maxs = []
  for d in data:
    if factor in d[9]:
        maxs.append(d[ind])
    else:
        mins.append(d[ind])
  print(f"{header[i+2]}: {mean(maxs):.2f} ± {stdev(maxs):.2f}, {mean(mins):.2f} ± {stdev(mins):.2f}")

