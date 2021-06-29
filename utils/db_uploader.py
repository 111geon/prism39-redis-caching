import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import pickle
# import pandas

import database 


with open("example_data/test_data1.pkl", "rb") as f:
    data_1 = pickle.load(f)
with open("example_data/test_data2.pkl", "rb") as f:
    data_2 = pickle.load(f)

data_1.to_sql('test_data_1', database.engine, if_exists='replace')
data_2.to_sql('test_data_2', database.engine, if_exists='replace')
