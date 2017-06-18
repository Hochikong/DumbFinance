from configparser import ConfigParser
from ETL import get_db, get_collection
from keras.models import load_model
import matplotlib.pyplot as plt
import numpy as np

CONFIG = 'config.ini'
DB = 'ETL'
SECTION = 'THRESHOLD'

cfg = ConfigParser()
cfg.read(CONFIG)

addr = cfg.get(DB, 'address')
port = int(cfg.get(DB, 'port'))
database = cfg.get(DB, 'database')
collection = cfg.get(DB, 'collection')

db = get_db(addr, port, database)
col = get_collection(db, collection)

query_result = [l for l in col.find()]
indx = list(set([l['label'] for l in query_result]))
data = [[] for i in indx]
for l in query_result:
    if l['label'] in indx:
        p = indx.index(l['label'])
        data[p].append(l['sentence'])
# tmpl = [l['label'] for l in query_result]

model = load_model('mymodel.h5')
x1 = range(len(data[0]))
y1 = []
x2 = range(len(data[1]))
y2 = []
for l in data[0]:
    t = np.array(l)
    t = t.reshape((1,t.shape[0]))
    rate = float(model.predict(t, verbose=0)[0][0])
    y1.append(rate)
for l in data[1]:
    t = np.array(l)
    t = t.reshape((1,t.shape[0]))
    rate = float(model.predict(t, verbose=0)[0][0])
    y2.append(rate)










