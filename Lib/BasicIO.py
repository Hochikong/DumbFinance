# __author__ = 'Hochikong'
from pymongo import MongoClient
from configparser import ConfigParser
from pandas import read_excel

"""
Include the functions to create connection and close connection,collection level create,drop and query.
store_xls() used for loading xls file to database
About the basic CRUD function:
--------------------------------
doc_insert:insert_many()
doc_find:find_one() or find()
doc_update:only update_one()
doc_delete:only delete_one()

--------------------------------
connection and db level ops use ACTION_OBJ style func name

file,collection and document ops use OBJ_ACTION style func name
"""

CONFIG_PATH = '~/Project/DumbFinance/ETL/config.ini'
DEFAULT_SECTION = 'DB'


def xls_store(col, files, labels):
    """
    Read xls file by pandas and store in MongoDB
    :param col: Collection object
    :param files: File names,list ['file1.xls','file2.xls']
    :param labels: Labels,list ['label1','label2']
    :return:
    """
    for name in files:
        for label in labels:
            print("Insert file " + name)
            tmpfile = read_excel(name, header=None)
            tmp = []
            for line in tmpfile[0]:
                tmp.append({'label': label, 'sentence': line})
            doc_insert(col, tmp)
            print("Insert a whole file")


def create_con():
    """
    Use address and port number connect to MongoDB,every time you use it,it create a new instance
    :return: A connection object
    """
    cfg = ConfigParser()
    cfg.read(CONFIG_PATH)
    try:
        address = cfg.get(DEFAULT_SECTION, 'address')
        port = int(cfg.get(DEFAULT_SECTION, 'port'))
        cli = MongoClient(address, port)
        return cli
    except Exception as err:
        print(err)


def select_db(cli, dbname):
    """
    Select a database with name
    :param cli: Client instance
    :param dbname: Database name
    :return:A database object
    """
    db = cli[dbname]
    return db


def col_ops(db, colname, ops):
    """
    Create,Drop and Get a collection
    :param db: Database object
    :param colname: Collection name
    :param ops: 'C','D' or 'G'
    :return:
    """
    if ops == 'G':
        collection = db[colname]
        return collection
    elif ops == 'C':
        db.create_collection(colname)
        return 'Create successfully'
    elif ops == 'D':
        db.drop_collection(colname)
        return 'Delete successfully'
    else:
        return 'Wrong ops'


def doc_insert(col, doc):
    """
    Only use insert_many()
    :param col: Collection object
    :param doc: Document data,list style
    :return: id
    """
    result = col.insert_many(doc)
    return result.inserted_ids


def doc_find(col, cond=None, types='single'):
    """
    By default use find_one()
    :param col: Collection object
    :param cond: Condition
    :param types: 'single' or 'multi'
    :return:
    """
    if cond:
        if types != 'multi':
            result = col.find_one(cond)
            return result
        else:
            result = []
            for data in col.find(cond):
                result.append(data)
            return result
    else:
        if types != 'multi':
            result = col.find_one()
            return result
        else:
            result = []
            for data in col.find():
                result.append(data)
            return result


def doc_update(col, cond, doc):
    """
    Only use update_one()
    :param col: Collection object
    :param cond: Condition
    :param doc: Document
    :return:
    """
    result = col.update_one(cond, doc)
    return "Modified:", result.modified_count


def doc_delete(col, cond):
    """
    Only use delete_one()
    :param col: Collection object
    :param cond: Condition
    :return:
    """
    result = col.delete_one(cond)
    return "Deleted:", result.deleted_count


def close_con(cli):
    """
    Nothing to say
    :param cli:
    :return:
    """
    cli.close()
    return 'Connection closed'
