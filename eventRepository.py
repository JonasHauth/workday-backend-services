from pymongo import MongoClient
from bson import json_util, ObjectId
import json


class eventRepository:

    def __init__(self):
        self.client = MongoClient('127.0.0.1', 27017) # mongodb
        self.db = self.client.workday_db
        self.events = self.db.event_collection

    """
    get event by id
    """
    def get_id(self, event_id):
        event = self.events.find_one({"_id": ObjectId(event_id)})
        event = json.loads(json_util.dumps(event))
        event["_id"] = event["_id"]["$oid"]
        return event

    """
    get all events per user
    """
    def get_all(self):
        cursor = self.events.find({})
        events = list(cursor)
        events = json.loads(json_util.dumps(events))
        for item in events:
            item["_id"] = item["_id"]["$oid"]
        return events

    """
    save event
    """
    def save(self, event):
        persisted_event = self.events.insert_one(event)
        new_id = json.loads(json_util.dumps(persisted_event.inserted_id))
        return list(new_id.values())[0]


    """
    update event
    """
    def update(self, event):
        event_id = event["_id"]
        del event["_id"]
        result = self.events.update_one(filter={"_id": ObjectId(event_id)}, update={"$set": event})
        return result.modified_count

    """
    delete event
    """
    def delete(self, event):
        result = self.events.delete_one({"_id": ObjectId(event)})
        return result.deleted_count

    """"
    delete many events
    """
    def delete_many(self, query):
        result = self.events.delete_many(query)
        return result.deleted_count