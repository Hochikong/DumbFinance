# __author__ = 'Hochikong'
from neo4j.v1 import GraphDatabase, basic_auth
from configparser import ConfigParser

CONFIG_PATH = 'config.ini'
DB_SECTION = 'Neo4j'


def create_con():
    """
    Use address and port number connect to Neo4j,everytime you use it,it create a new instance with session
    :return:A connection object
    """
    cfg = ConfigParser()
    cfg.read(CONFIG_PATH)
    try:
        # Fetch db info
        address = cfg.get(DB_SECTION, 'address')
        port = cfg.get(DB_SECTION, 'port')
        user = cfg.get(DB_SECTION, 'user')
        passwd = cfg.get(DB_SECTION, 'passwd')
        # Connect
        driver = GraphDatabase.driver(
            "bolt://%s:%s" % (address, port), auth=basic_auth(user, passwd))
        return driver
    except Exception as err:
        print(err)


def close_con(session):
    """
    Nothing to say
    :param session: A section object
    :return:
    """
    session.close()
    return 'Session closed'


def run_model(session, model, data=None):
    """
    Use specific model to CRUD on Neo4j
    :param session: A session object
    :param model: A string store in .py file
    :param data: The data you want to use in model,usually use dict as input
    :return: A result list
    """
    if data:
        result = session.run(model, data)
        return result
    else:
        result = session.run(model)
        return result
