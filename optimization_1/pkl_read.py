import chardet
import pickle

attempt = 2.4 # attempt number
pickle_file_name = f'optimization/attempt_{attempt}/optimized_sav.pkl'

with open(pickle_file_name, 'rb') as fileObj:
    #results = pickle.load(fileObj)
    results = pickle.load(fileObj, encoding="latin1") # <----- use this line if you get an error with ascii encoding

print(results)