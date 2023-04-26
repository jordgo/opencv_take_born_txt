import pymongo.database as database


class ImgTextsRepository:
    def __init__(self, db: database.Database, config):
        self.coll = db[config['mongo']['collection_name']]

    def insert_one(self, obj: dict):
        resp = self.coll.insert_one(obj)
        return resp.inserted_id

    def find_one_by_key(self, key):
        resp = self.coll.find_one(key)
        return resp

    def delete_one_by_key(self, key):
        resp = self.coll.delete_one(key)
        return resp
