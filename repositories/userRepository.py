from pymongo import MongoClient
from bson import json_util, ObjectId
import json


class userRepository:

    def __init__(self):
        self.client = MongoClient('127.0.0.1', 27017) # mongodb
        self.db = self.client.workday_db
        self.users = self.db.user_collection

    """
    get user by id
    """
    def get_id(self, user_id):
        user = self.users.find_one({"user_id": user_id})
        user = json.loads(json_util.dumps(user))
        #user["_id"] = user["_id"]["$oid"]
        return user

    """
    save user
    """
    def save(self, user):
        persisted_user = self.users.insert_one(user)
        new_id = json.loads(json_util.dumps(persisted_user.inserted_id))
        return user


    """
    delete user
    """
    def delete(self, user_id):
        result = self.users.delete_one({"user_id": user_id})
        return result.deleted_count