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
username = cfg.get(SECTION, 'name')
passwd = cfg.get(SECTION, 'passwd')
token = cfg.get(SECTION, 'token')
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
        self.__driver = GraphDatabase.driver(
            "bolt://{}:{}".format(addr, port), auth=basic_auth(username, passwd))
        self.__session = self.__driver.session()
        self.__div = float(cfg.get(SECTION, 'div'))
        self.bigger = cfg.get(SECTION, 'bigger')
        self.smaller = cfg.get(SECTION, 'smaller')

    def analysis(self, text, time, stock_number):
        CREATE_FACTOR = "MATCH (s:STOCK) WHERE s.StockNumber = {stock_number} " \
                        "CREATE (n:EVENT {FACTOR:{factor},TEXT:{text},KEYWORDS:{keywords}})-[f:%s]->(s)"

        CREATE_TIME = "MATCH (s:STOCK) WHERE s.StockNumber = {stock_number} " \
                      "CREATE (:TIME {TIME:{time}})-[t:时间]->(s)"   # '2017-06-15,01:41'

        QUERY_FOR_FACTORS = "MATCH (n)-[f]->(s:STOCK {StockNumber:'%s'})<-[t:时间]-(tn) RETURN n,f,s,t,tn"

        # QUERY_FOR_TYPE_STRUCTURE = "MATCH (n)-[r:%]->(s:STOCK {StockNumber:'xxx'}) RETURN n,r,s"

        QUERY_FOR_STRUCTURE = "MATCH (n)-[r]->(s:STOCK {StockNumber:'%s'})-[rx]->(nx) RETURN n,r,s,rx,nx"

        # Step 1:Cut the word
        cut_result = sen_cut(text)

        # Step 2:NER or Find keywords
        ner_result = sen_ner(cut_result, 1, True)
        entities = []
        if ner_result[0]['entity']:
            for i in ner_result[0]['entity'][0]:
                if type(i) == int:
                    entities.append(ner_result[0]['word'][i])
        else:
            keywords = nlp.extract_keywords(text, top_k=5)
            for weight, word in keywords:
                entities.append(word)

        # Step3 :Translation
        result = translate(
            cut_result[0]['word'],
            max_length,
            word_set,
            features)
        result = sen2num(result)
        result = numpy.array(result, dtype=int)

        # Step3:Sentiment analysis
        result = result.reshape((1, result.shape[0]))
        predict_result = self.__model.predict(result, verbose=0)[0][0]
        if predict_result > self.__div:
            factor = self.bigger
        else:
            factor = self.smaller

        self.__session.run(
            CREATE_TIME, {
                'stock_number': stock_number, 'time': time})
        self.__session.run(CREATE_FACTOR % factor,
                           {'stock_number': stock_number,
                            'factor': float(predict_result),
                            'text': text,
                            'keywords': entities})
        print('Result: ', predict_result)
        print('Use this cypher query check all factors by time: ' +
              QUERY_FOR_FACTORS % stock_number)
        print(
            'Use this cypher query check all relations: ' +
            QUERY_FOR_STRUCTURE %
            stock_number)

    def writeCore(self, company, stock_number, basic_info):
        CREATE_CORE_NODE = "CREATE (:STOCK {Company:{company},StockNumber:{stock_number},BasicInfo:{basic_info}})"
        self.__session.run(CREATE_CORE_NODE,
                           {'company': company,
                            'stock_number': stock_number,
                            'basic_info': basic_info})

    def cleanall(self):
        # MATCH (n) DETACH DELETE n
        self.__session.run('MATCH (n) DETACH DELETE n')

    def writeC2O(self, stock_number, relation, other_company):
        CREATE_BASIC_STRUCTURE_TO = "MATCH (s:STOCK) WHERE s.StockNumber = {stock_number} " \
                                    "CREATE (s)-[r:%s]->(n:Related {Company:{other_company}})"
        self.__session.run(CREATE_BASIC_STRUCTURE_TO % relation,
                           {'stock_number': stock_number,
                            'other_company': other_company})

    def writeO2C(self, stock_number, relation, other_company):
        CREATE_BASIC_STRUCTURE_FROM = "MATCH (s:STOCK) WHERE s.StockNumber = {stock_number} " \
                                      "CREATE (n:Related {Company:{other_company}})-[r:%s]->(s)"
        self.__session.run(CREATE_BASIC_STRUCTURE_FROM % relation,
                           {'stock_number': stock_number,
                            'other_company': other_company})

    def browser(self):
        launch_browser(addr, passwd, port='7474')
