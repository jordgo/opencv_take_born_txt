import pytest
import yaml

from repositories.db_selector import MongoDB


@pytest.fixture()
def config():
    with open("../../conf/config.yml", 'r') as file:
        config = yaml.safe_load(file)
        return config


@pytest.fixture()
def db_session(config):
    obj = MongoDB(config)
    db = obj.get_db()
    yield db
    obj.db_close()