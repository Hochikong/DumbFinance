from ETL.BasicIO import create_con, select_db, col_ops, doc_insert, doc_find, close_con, xls_store
from ETL.NLPlib import jieba_config, sen_cut, sen_ner
from configparser import ConfigParser
from Feedback import BasicGraph
from copy import deepcopy

CONFIG_PATH = 'config.ini'
ETL_SECTION = 'ETL'
SERVICE_SECTION = 'Service'


class Base(object):  # Base class
    def __init__(self):
        self.__cfg = ConfigParser()
        self.__cfg.read(CONFIG_PATH)


class WordIO(Base):
    def __init__(self):
        super(WordIO, self).__init__()
        self.__connection = create_con()  # Inital database connnection
        self.__database = False
        self.__collection = False
        self.__db_name = False
        self.__collection_name = False

    def read(self, from_db, from_collection, condition=False):
        """
        Get data from MongoDB
        :param from_db: Which database data come from,a string
        :param from_collection: Which collection data com from,a string
        :param condition: A query condition,usually a dict
        :return: A result list,because it usually return multiple data
        """
        self.__db_name = from_db
        self.__collection_name = from_collection
        self.__database = select_db(self.__connection, from_db)
        self.__collection = col_ops(self.__database, from_collection, 'G')
        if condition:
            result = doc_find(self.__collection, condition, 'multi')
        else:
            result = doc_find(self.__collection, types='multi')
        return result

    def write(self, to_db, to_collection, data):
        """
        Write data to MongoDB
        :param to_db: Which database you want to store data
        :param to_collection: Which collection you want to store data
        :param data: Documents,a list
        :return: A message
        """
        if to_db == self.__db_name:
            if to_collection == self.__collection_name:
                doc_insert(self.__collection, data)  # Use former collection
                return 'Write successfully'
            else:
                self.__collection = col_ops(
                    self.__database, to_collection, 'G')  # Change a collection
                doc_insert(self.__collection, data)
                return 'Write successfully'
        else:
            self.__database = select_db(
                self.__connection, to_db)  # Change a database
            self.__collection = col_ops(self.__database, to_collection, 'G')
            doc_insert(self.__collection, data)
            return 'Write successfully'

    def cut(self, sentence):
        """
        Use jieba cut the sentence
        :param sentence: A sentence from MongoDB
        :return: A list
        """
        result = sen_cut(sentence)
        return result


class CypherIO(Base):
    def __init__(self):
        super(CypherIO, self).__init__()
        self.__connection = BasicGraph.create_con()
        self.__session = self.__connection.session()

    def run(self, model, data=None):
        """
        Execute Cypher query and other operations
        :param model: A Cypher model
        :param data: Cypher data
        :return: A dict result
        """
        if data:
            result = BasicGraph.run_model(self.__session, model, data)
            return {'result': result, 'model': model, 'data': data}
        else:
            result = BasicGraph.run_model(self.__session, model)
            return result


def remove_punctuation(data):
    """
    Remove all punctuation in the result of sen_cut()

    As you see this result,I must remove the punctuation before use sen_ner()
    [ {'tag': ['v', 'x', 'x', 'b', 'x', 'x', 'x', 'x', 'x', 'r', 'n', 'd', 'c', 'n',
    'm', 'n', 'x'], 'word': ['例如', '，', '“', '副', '”', '（', 'f', 'ù', '）',
    '这个', '字', '就', '可以', '代表', '三个', '语素', '：']}]

    After this func:
    [{'tag': ['v', 'b', 'r', 'n', 'd', 'c', 'n', 'm', 'n'],
    'word': ['例如', '副', '这个', '字', '就', '可以', '代表', '三个', '语素']}]

    :param data: A list from sen_cut()
    :return: A new list without punctuation
    """
    COND = 'x'
    replica = deepcopy(data)
    while True:
        if COND in replica[0]['tag']:
            p = replica[0]['tag'].index(COND)
            replica[0]['tag'].remove(COND)
            # print(replica[0]['tag'])
            del(replica[0]['word'][p])
            # print(replica[0]['word'])
        else:
            break
    return replica

