# __author__ = 'Hochikong'
from neo4j.v1 import GraphDatabase, basic_auth
from configparser import ConfigParser


def create_con():
    """
    Use address and port number connect to Neo4j,everytime you use it,it create a new instance with session
    :return:A session object
    """
    cfg = ConfigParser()
    cfg.read('config.ini')
    db_section = 'Neo4j'
    auth_section = 'Auth'
    try:
        # Fetch db info
        db = cfg.options(db_section)
        address = cfg.get(db_section, db[0])
        port = cfg.get(db_section, db[1])

        # Fetch auth info
        auth = cfg.options(auth_section)
        user = cfg.get(auth_section, auth[0])
        passwd = cfg.get(auth_section, auth[1])

        # Connect
        driver = GraphDatabase.driver(
            "bolt://%s:%s" % (address, port), auth=basic_auth(user, passwd))
        session = driver.session()
        return session
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
    result = session.run(model, data)
    return result
