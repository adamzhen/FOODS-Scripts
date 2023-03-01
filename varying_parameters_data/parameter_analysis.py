# Analyzing parameters using SA:V data

# read in data
with open('varying_parameters_data/VaryingParametersCSV2.txt', 'r') as f:
    data = [row.split(', ') for row in f.read().split('\n')]
    header = data.pop(0)
    data.pop() # removes last empty row
    for i in range(len(data)): # converting strings to floats
        for j in range(1, len(data[i])):
            data[i][j] = float(data[i][j])

method = 1 # 1 for max-min, 2 for deviation from mean

# Max-Min Analysis
if method == 1:
    paramdict = {}
    for i in range(0, len(data), 2):
        p1 = data[i]
        p2 = data[i+1]
        score = (p2[-1]-p1[-1]) / (p2[1]-p1[1])
        paramdict[p1[0]] = score
        #print(f"{p1[0]}: {score:.4f}")
    paramdict = dict(sorted(paramdict.items(), key=lambda x:x[1]))
    for k, v in paramdict.items():
        print(f"{k}: {v:.2f}")

# Deviation from Mean Analysis

if method == 2:
    with open('varying_parameters_data/MeanDeviationAnalysis.txt', 'w') as f:
        for i in range(0, len(data), 3):
            p1 = data[i]
            p2 = data[i+1]
            p3 = data[i+2]
            upperdev = (p3[-1]-p2[-1]) / p2[-1] * 100
            lowerdev = (p1[-1]-p2[-1]) / p2[-1] * 100
            f.write(f"{p1[0]}, {lowerdev:.3f}%, {upperdev:.3f}%\n")