# __author__ = 'Hochikong'
from pymongo import MongoClient
from jieba import posseg, add_word, enable_parallel, load_userdict
from configparser import ConfigParser
from functools import reduce
import shelve
import pandas
import numpy

CONFIG = 'config.ini'
SECTION = 'ETL'
NLP = 'NLP'
PARALLEL = 4


def load_xls(filename):
    return pandas.read_excel(filename, header=None)


def get_db(addr, port, db):
    cli = MongoClient(addr, port)
    database = cli[db]
    return database


def get_collection(db, collection):
    return db[collection]


def write(collection, document):
    collection.insert_many(document)  # documment is a list


def tag(pandas_instance, tag):  # Modify in place
    pandas_instance['label'] = tag


def combine(p1, p2):
    all_ = p1.append(p2, ignore_index=True)
    return all_


def cut(sentence):
    tmp = []
    words = posseg.cut(sentence)
    for w, f in words:
        if f != 'x':  # remove all punctuation
            tmp.append(w)
    return tmp


def frequency_filter(pandas_instance, min_frequency):
    content = []
    for i in pandas_instance['words']:
        content.extend(i)
    order_by_frequency = pandas.Series(
        content).value_counts()  # Order by frequency
    after_filter = order_by_frequency[order_by_frequency >= min_frequency]
    number_by_frequency = after_filter
    number_by_frequency[:] = range(
        1, len(number_by_frequency) + 1)  # number by frequency
    number_by_frequency[''] = 0
    word_set = set(number_by_frequency.index)  # number_by_f = abc
    return word_set, number_by_frequency


def translate(sentence_list, max_length, word_set, number_by_frequency):
    sentence_list = [w for w in sentence_list if w in word_set]
    sentence_list = sentence_list[:max_length] + \
        [''] * max(0, (max_length - len(sentence_list)))
    return list(number_by_frequency[sentence_list])


if __name__ == '__main__':
    cfg = ConfigParser()
    cfg.read(CONFIG)
    addr = cfg.get(SECTION, 'address')
    port = int(cfg.get(SECTION, 'port'))
    database = cfg.get(SECTION, 'database')
    collection = cfg.get(SECTION, 'collection')
    userdictpath = cfg.get(NLP, 'path')
    userdicts = cfg.get(NLP, 'files')
    max_length = int(cfg.get(NLP, 'max_length'))
    min_frequency = int(cfg.get(NLP, 'min_frequency'))
    addwords = cfg.get(NLP, 'addwords')

    # load files
    filenames = []
    labels = []
    while True:
        name = input(
            "Enter the xls file name with path,enter 'halt' to continue: ")
        if name == 'halt':
            break
        else:
            filenames.append(name)
    print("Set labels for these files: ", filenames)
    for name in filenames:
        label = int(input("Label for {} is: ".format(name)))
        labels.append(label)

    # ops by pandas
    pandas_instances = []
    for file in filenames:
        p = filenames.index(file)
        tmp = load_xls(file)
        tag(tmp, labels[p])
        pandas_instances.append(tmp)

    all_instance = reduce(combine, pandas_instances)

    # jieba configuration
    files = userdicts.split(',')
    for file in files:
        load_userdict(userdictpath + file)
    enable_parallel(PARALLEL)
    addwords = addwords.split(',')
    for w in addwords:
        add_word(w)

    # Cut
    all_instance['words'] = all_instance[0].apply(lambda s: list(cut(s)))

    # Filter by frequency
    word_set, number_by_frequency = frequency_filter(
        all_instance, min_frequency)

    # translate all word list to number list
    all_instance['numbers'] = all_instance['words'].apply(
        lambda s: translate(s, max_length, word_set, number_by_frequency))

    # shuffle the index
    idx = list(range(len(all_instance)))
    numpy.random.shuffle(idx)
    all_instance = all_instance.loc[idx]

    # X and Y
    X = numpy.array(list(all_instance['numbers']))
    tmp = []
    for line in X:
        tmp.append(line.tolist())   # change numpy.int64 into int
    X = tmp
    Y = numpy.array(list((all_instance['label']))).tolist()
    unit = zip(X, Y)

    # You should create a database and collection before using this program
    db = get_db(addr, port, database)
    col = get_collection(db, collection)
    document = []
    for w, z in unit:
        # only use int labels
        document.append({'sentence': w, 'label': int(z)})

    # Store in MongoDB
    write(col, document)
    print('Data had save in MongoDB ')
    # Store word_set and number_by_frequency(features)
    f1 = shelve.open('wordset.dat')
    print('Word Set save in wordset.dat')
    f1['word_set'] = word_set
    f1.close()
    # f2 = shelve.open('features.dat')
    print('Features save in features.csv')
    number_by_frequency.to_csv('features.csv')
    # f2['number_by_frequency'] = number_by_frequency
    # f2.close()

