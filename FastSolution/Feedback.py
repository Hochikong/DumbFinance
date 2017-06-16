# __author__ = 'Hochikong'
from keras.models import load_model
from neo4j.v1 import GraphDatabase, basic_auth
from configparser import ConfigParser
from bosonnlp import BosonNLP
from splinter import Browser
from jieba import posseg, add_word, enable_parallel, load_userdict
from ETL import translate
import numpy
import shelve
import pandas
import os

CONFIG = 'config.ini'
NLP = 'NLP'
SECTION = 'FEEDBACK'
PARALLEL = 4
WORD_SET = 'wordset.dat'  # file['word_set']
FEATURES_FILE = 'features.csv'

cfg = ConfigParser()
cfg.read(CONFIG)

addr = cfg.get(SECTION, 'address')
port = cfg.get(SECTION, 'port')
username = os.getenv('NEO4J_NAME')
passwd = os.getenv('NEO4J_PASSWD')
token = os.getenv('BOSON_TOKEN')
userdictpath = cfg.get(NLP, 'path')
userdicts = cfg.get(NLP, 'files')
addwords = cfg.get(NLP, 'addwords')
max_length = int(cfg.get(NLP, 'max_length'))

nlp = BosonNLP(token)
word_set = shelve.open('wordset.dat')
word_set = word_set['word_set']
features = pandas.Series.from_csv(FEATURES_FILE, header=None)

# jieba configuration
files = userdicts.split(',')
for file in files:
    load_userdict(userdictpath + file)
enable_parallel(PARALLEL)
addwords = addwords.split(',')
for w in addwords:
    add_word(w)


def sen_ner(data, sensitivity=None, segmented=False):
    sensitivity_list = [1, 2, 3, 4, 5]
    if segmented:
        if sensitivity in sensitivity_list:
            result = nlp.ner(data, sensitivity, True)
            return result
        else:
            return 'Invalid sensitivity content'
    else:
        if sensitivity in sensitivity_list:
            result = nlp.ner(data, sensitivity)
            return result
        else:
            return 'Invalid sensitivity content'


def sen_cut(sentence):  # No punctuation
    words = posseg.cut(sentence)
    result = [{'word': [], 'tag':[]}]
    for word, flag in words:
        result[0]['word'].append(word)
        result[0]['tag'].append(flag)
    for f in result[0]['tag']:
        if f == 'x':
            p = result[0]['tag'].index(f)
            result[0]['tag'].remove(f)
            del(result[0]['word'][p])
    return result


def launch_browser(addr, passwd, port='7474'):
    b = Browser()
    url = 'http://' + addr + ':' + port
    b.visit(url)
    passwd_place = b.find_by_tag('input')[-1]
    button = b.find_by_tag('button')[-1]
    passwd_place.fill(passwd)
    button.click()
    print('Please check the browser...')


def sen2num(result):
    for i in result:
        if numpy.isnan(i):
            result[result.index(i)] = 0
    return result


class Analysis(object):
    def __init__(self):
        self.__model = load_model('mymodel.h5')
        self.__driver = GraphDatabase.driver("bolt://{}:{}".format(addr,port),auth=basic_auth(username,passwd))
        self.__session = self.__driver.session()

    def analysis(self,sentence):
        # Step 1:Cut the word
        cut_result = sen_cut(sentence)

        # Step 2:NER
        ner_result = sen_ner(cut_result, 1, True)

        # Step3 :Translation
        result = translate(cut_result[0]['word'], max_length, word_set, features)
        result = sen2num(result)

        # Step3:Sentiment analysis
        result = result.reshape((1, result.shape[0]))
        self.__model.predict(result,verbose=0)






