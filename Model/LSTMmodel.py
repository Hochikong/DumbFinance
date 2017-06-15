# __author__ = 'Hochikong'
from keras.models import Sequential,load_model
from keras.layers import Dense, Activation, Dropout, Embedding, LSTM
from configparser import ConfigParser
import shelve
import numpy
import pandas

CONF_PATH = 'config.ini'
SECTION = 'Train'
OUTPUT_DIM = 'output_dim'
LSTM_UNITS = 'lstm_units'
DROPOUT = 'dropout'
DENSE = 'dense'
ACTIVATION = 'activation'
LOSS = 'loss'
OPTIMIZER = 'optimizer'
METRICS = 'metrics'
BATCH_SIZE = 'batch_size'
TRAIN_RANGE = 'train_range'
EPOCH = 'epoch'


def train_prepare(data, labels):
    """
    Use numpy modify data and labels'type and shape
    :param data: A list contains numbers' list
    :param labels: A list contains labels
    :return: A tuple
    """
    data = numpy.array(data)
    labels = numpy.array(labels).reshape((-1, 1))
    return data, labels


def translate(raw_words_line, word_features, word_features_set, max_features):
    """
    Use word_features_set to translate words to numbers
    :param raw_words_line: A list contains all sentences after cut,like:
    [在, 和平时期, ，, 一个, 科学家, 是, 属于, 全世界, 的]

    :param word_features: A pandas instance contains words with number like this:
    的    1
    是    2
    了    3
    dtype: int64

    :param word_features_set: A list contains words,eg.:['，', '的', '是', '了', '在', '']

    :param max_features: The train data's length
    :return: raw_words modify in place
    """
    raw_words_line = [
        word for word in raw_words_line if word in word_features_set]
    raw_words_line = raw_words_line[:max_features] + \
        [''] * max(0, max_features - len(raw_words_line))
    return list(word_features[raw_words_line])


class Base(object):
    def __init__(self):
        self.__cfg = ConfigParser()
        self.__cfg.read(CONF_PATH)
        self.__max_features = self.__cfg.get(SECTION, 'max_features')
        self.__min_frequency = self.__cfg.get(SECTION, 'min_frequency')


class Model(Base):
    def __init__(self):
        super(Model, self).__init__()
        self.__output_dim = self.__cfg.get(SECTION, OUTPUT_DIM)
        self.__lstm = self.__cfg.get(SECTION, LSTM_UNITS)
        self.__dropout = self.__cfg.get(SECTION, DROPOUT)
        self.__dense = self.__cfg.get(SECTION, DENSE)
        self.__activation = self.__cfg.get(SECTION, ACTIVATION)
        self.__loss = self.__cfg.get(SECTION, LOSS)
        self.__optimizer = self.__cfg.get(SECTION, OPTIMIZER)
        self.__metrice = self.__cfg.get(SECTION, METRICS)
        self.model = None
        self.read_model = None
        self.read_word_features = None
        self.read_word_features_set = None


    def building(self, word_features):
        # Add layers
        self.model = Sequential()
        self.model.add(
            Embedding(
                len(word_features),
                self.__output_dim,
                input_length=self.__max_features))
        self.model.add(LSTM(self.__lstm))
        self.model.add(Dropout(self.__dropout))
        self.model.add(Dense(self.__dense))
        self.model.add(Activation(self.__activation))
        self.model.compile(
            loss=self.__loss,
            optimizer=self.__optimizer,
            metrics=[
                self.__metrice])

    def fit(self, x, y, batch_size, epoch):
        """
        Fit model
        :param x: Data,a numpy instance from train_prepare
        :param y: Labels,a numpy instance from train_prepare
        :param batch_size: Batch_size
        :param epoch: Epoch
        :return:
        """
        self.model.fit(x, y, batch_size=batch_size, nb_epoch=epoch)

    def evaluate(self, x, y, batch_size):
        """
        Evaluate the model
        :param x: Data,a numpy instance from train_prepare
        :param y: Labels,a numpy instance from train_prepare
        :param batch_size:
        :return:
        """
        self.model.evaluate(x, y, batch_size=batch_size)


    def word_to_num(self, words, raw_words):
        """
        When all data from TrainRawData load by server, you should
        extend them to a big list which only contains words(without punctuation),then use this method
        :param words: A list contains all words from raw_words,eg.:[在, 和平时期, ，, 一个, 科学家, 是, 属于, 全世界, 的]word
        :param raw_words: A list contains all sentences after cut,
        eg.:[[在, 和平时期, ，, 一个, ]
             [科学家, 是, 属于, 全世界, 的]]
        :return: A list
        """
        word_features = pandas.Series(words).value_counts()
        word_features = word_features[word_features >=
                                      self.__min_frequency]  # If a word's frequency
        # less than min_frequency will be filter out
        word_features[:] = range(
            1, len(word_features) + 1)  # Sorted by frequency
        word_features[''] = 0
        word_features_set = set(word_features.index)
        result = []
        for lines in raw_words:
            result.append(
                translate(
                    lines,
                    word_features,
                    word_features_set,
                    self.__max_features))
        return {'result': result, 'word_features': word_features,'word_features_set':word_features_set}  # No labels

    def save(self, file, word_features,word_features_set):
        """
        Save the model
        :param file: Filename
        :param word_features: Word features,pandas instance
        :param word_features_set: Word features set,list
        :return:
        """
        print('Saving model and word_features')  # By default use features.dat as filename
        self.model.save(file)
        features = shelve.open('features.dat')
        tmp = {}
        tmp['word_features'] = word_features
        tmp['word_features_set'] = word_features_set
        features['data'] = tmp
        features.close()

    def load(self,model, features):
        data = shelve.open(features)
        self.read_model = load_model(model)
        self.read_word_features = data['data']['word_features']
        self.read_word_features_set = data['data']['word_features_set']

    def predict(self,sentence):
        """
        You should cut the word first
        :param sentence: A list
        :return:
        """
        tmp = translate(sentence,self.read_word_features,self.read_word_features_set,self.__max_features)
        return self.read_model.predict_classes(tmp,verbose=0)[0][0]