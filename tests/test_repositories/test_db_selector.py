import yaml

import repositories.db_selector  as db_selector
from repositories.db_selector import MongoDB, Databases


def get_config():
    with open("../../conf/config.yml", 'r') as file:
        config = yaml.safe_load(file)
        return config


def test_mongo_check_connection():
    conf = get_config()
    obj = MongoDB(conf)
    db = obj.get_db()
    status = obj.check_connection()
    obj.db_close()
    assert status