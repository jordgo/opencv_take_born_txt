import abc
import enum
from typing import Optional

import pymongo
from pymongo import errors as pymongo_errors
import pymongo.database as mongodb
import logging.config

from conf.logging_conf import LOGGING_CONFIG


# logging.config.dictConfig(LOGGING_CONFIG)
_logger = logging.getLogger("app")

class Databases(enum.Enum):
    MONGO = 1


class DbClients(abc.ABC):

    @abc.abstractmethod
    def get_db(self):
        return NotImplemented

    @abc.abstractmethod
    def check_connection(self) -> bool:
        return NotImplemented


class MongoDB(DbClients):

    def __init__(self, config):
        mongo_conf = config['mongo']
        self.host = mongo_conf['host']
        self.port = mongo_conf['port']
        self.user = mongo_conf['user']
        self.password = mongo_conf['password']
        self.db_name = mongo_conf['db_name']
        self.db: Optional[mongodb.Database] = None
        self.db_client: Optional[pymongo.MongoClient] = None

    def get_db(self):
        connection_str = f'mongodb://{self.user}:{self.password}@{self.host}:{self.port}/'
        self.db_client = pymongo.MongoClient(connection_str)
        self.db = self.db_client[self.db_name]
        return self.db

    def db_close(self):
        if self.db_client:
            _logger.info("DB closed")
            self.db_client.close()

    def check_connection(self) -> bool:
        try:
            self.db_client.server_info()
            _logger.info("MongoDB Connection established!")
            return True
        except AttributeError as err:
            _logger.error(f"MongoDB connection failed, err: {err}")
            return False
        except pymongo_errors.ServerSelectionTimeoutError as err:
            _logger.error("MongoDB connection failed")
            return False



def get_db(db: Databases, config):
    if db == Databases.MONGO:
        db_obj = MongoDB(config)
        return db_obj.get_db(), db_obj
    else:
        raise NotImplementedError(f"Database {db} Not Implemented")
