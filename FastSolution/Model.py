# __author__ = 'Hochikong'
from __future__ import absolute_import
from __future__ import print_function
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout, Embedding, LSTM
from keras.utils import plot_model
from configparser import ConfigParser
import matplotlib.pyplot as plt
# import os
# import sys
# PROJECT_PATH = os.path.abspath('.')
# sys.path.append(PROJECT_PATH)
from ETL import get_db, get_collection
import numpy
import pandas

CONFIG = 'config.ini'
SECTION = 'MODEL'
NLP = 'NLP'
DB = 'ETL'
FEATURES_FILE = 'features.csv'

cfg = ConfigParser()
cfg.read(CONFIG)

max_length = int(cfg.get(NLP, 'max_length'))
features = pandas.read_csv(FEATURES_FILE, header=None)

OUTPUT_DIM = cfg.get(SECTION, 'output_dim')
LSTM_UNITS = cfg.get(SECTION, 'lstm_units')
DROPOUT = cfg.get(SECTION, 'dropout')
DENSE = cfg.get(SECTION, 'dense')
ACTIVATION = cfg.get(SECTION, 'activation')
LOSS = cfg.get(SECTION, 'loss')
OPTIMIZER = cfg.get(SECTION, 'optimizer')
METRICS = cfg.get(SECTION, 'metrics')
BATCH_SIZE = cfg.get(SECTION, 'batch_size')
TRAIN_PERCENT = cfg.get(SECTION, 'train_percent')
EPOCH = cfg.get(SECTION, 'epoch')
VALIDATION_SPLIT = cfg.get(SECTION, 'validation_split')

addr = cfg.get(DB, 'address')
port = int(cfg.get(DB, 'port'))
database = cfg.get(DB, 'database')
collection = cfg.get(DB, 'collection')

model = Sequential()
model.add(Embedding(len(features), int(OUTPUT_DIM), input_length=max_length))
model.add(LSTM(int(LSTM_UNITS)))
model.add(Dropout(float(DROPOUT)))
model.add(Dense(int(DENSE)))
model.add(Activation(ACTIVATION))
model.compile(loss=LOSS, optimizer=OPTIMIZER, metrics=[METRICS])


if __name__ == "__main__":
    print('Connecting to MongoDB')
    db = get_db(addr, port, database)
    col = get_collection(db, collection)
    query_result = [l for l in col.find()]  # Add lines into query_result

    indx = list(set([l['label'] for l in query_result]))  # Labels set

    data = [[] for i in indx]
    for l in query_result:
        if l['label'] in indx:
            p = indx.index(l['label'])
            data[p].append(l['sentence'])  # Store,accord to indx
    # labels = numpy.array([l['label'] for l in query_result])
    tmpl = [l['label'] for l in query_result]  # A list only contains labels

    train_percent = float(TRAIN_PERCENT)
    percent = list(map(lambda x: x * train_percent,
                       [tmpl.count(i) for i in indx]))
    # Choose how many lines in data you used as train data
    percent = list(map(lambda x: int(x), percent))
    unit = zip(indx, percent)
    train_X = []
    train_Y = []
    test_X = []
    test_Y = []
    for i, v in unit:
        p = indx.index(i)
        train_X.extend(data[p][:v])
        test_X.extend(data[p][v:])
        train_Y.extend(len(data[p][:v]) * [i])
        test_Y.extend(len(data[p][v:]) * [i])
    train_Y = numpy.array(train_Y, dtype=int)
    test_Y = numpy.array(test_Y, dtype=int)

    train_X = numpy.array(train_X)
    train_Y = train_Y.reshape((-1, 1))
    test_X = numpy.array(test_X)
    test_Y = test_Y.reshape((-1, 1))

    batch_size = int(BATCH_SIZE)
    epoch = int(EPOCH)
    print("Fitting model...")
    log = model.fit(train_X, train_Y, batch_size=batch_size, nb_epoch=epoch, validation_split=float(VALIDATION_SPLIT))
    print("Evaluating model...")
    model.evaluate(test_X, test_Y, batch_size=batch_size)

    plt.figure(facecolor='white')

    plt.subplot(2, 1, 1)
    plt.plot(log.history['acc'], 'b-', label='Training Accuracy')
    plt.plot(log.history['val_acc'], 'r-', label='Validation Accuracy')
    plt.legend(loc='best')
    plt.xlabel('Epochs')
    plt.axis([0, epoch, 0.9, 1])

    plt.subplot(2, 1, 2)
    plt.plot(log.history['loss'], 'b-', label='Training Loss')
    plt.plot(log.history['val_loss'], 'r-', label='Validation Loss')
    plt.legend(loc='best')
    plt.xlabel('Epochs')
    plt.axis([0, epoch, 0, 1])

    # plt.show()
    print("Saving photo to statistics.png ")
    plt.savefig('statistics.png')
    print("Saving model to mymodel.h5")
    model.save('mymodel.h5')
    print("Saving graph to mymodel.png")
    plot_model(model, to_file='mymodel.png')
