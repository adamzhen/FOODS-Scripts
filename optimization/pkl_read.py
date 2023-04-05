import chardet
import pickle

pickle_file_name = 'optimization/optimized_sav.pkl'

with open(pickle_file_name, 'rb') as fileObj:
    #results = pickle.load(fileObj)
    results = pickle.load(fileObj, encoding="latin1") # <----- use this line if you get an error with ascii encoding

print(results)