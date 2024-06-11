from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()

class Database:
    def __init__(self, database, table):
        self.database = database
        self.table = table
        self.user_table = "Users"
        self.client = self._connect_to_server()
        self.collection = self._connect_to_database()

    def _connect_to_server(self):
        MONGODB_PWD = os.getenv('MONGODB_PWD')
        MONGODB_USER = os.getenv('MONGODB_USER')
        uri = f"mongodb+srv://{MONGODB_USER}:{MONGODB_PWD}@cluster0.jcrcool.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        return MongoClient(uri, server_api=ServerApi('1'))
    
    def _connect_to_database(self):
        db = self.client[self.user_table]
        return db[self.table]

    def submit_user(self, user):
        try:
            existing_user = self.collection.find_one({"user_id": user["user_id"]})
            if existing_user is None:
                self.collection.insert_one(user)
                return True
            else:
                return False
        except Exception as e:
            print(f"Error submitting user: {e}")
            return False

    def update_user(self, user):
        try:
            result = self.collection.update_one({"user_id": user["user_id"]}, {"$set": user})
            if result.modified_count > 0:
                return True
            else:
                return False
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
        
    def get_user_data_by_user_id(self, user_id):
        user = _db.collection.find_one({"user_id": user_id})
        return user
    
    def create_collection(self, table):
        db = self.client[self.database]
        return db[table]
    
    def get_collection(self, table):
        db = self.client[self.database]
        return db[table]
    
    def create_database(self, database):
        return self.client[database]
    
    def get_database(self, database):
        return self.client[database]
    
    def create_database_and_collection(self, database, table):
        db = self.client[database]
        return db[table]
    
    def get_all_users(self):
        return self.collection.find({})
    
    def update_casting_call_notification_list(self, database, table, notification_list):
        # make sure to check it exists first and if not, create it, then update
        db = self.client[database]
        collection = db[table]
        existing_notification_list = collection.find_one({"notification_list": {"$exists": True}})
        try:
            if existing_notification_list is None:
                collection.insert_one({"notification_list": notification_list})
            else:
                collection.update_one({"notification_list": {"$exists": True}}, {"$set": {"notification_list": notification_list}})
            return True
        except Exception as e:
            print(f"Error updating casting call notification list: {e}")
            return False
            

_db = Database("Atlanta", "Backstage Notifications")

if __name__ == '__main__':
    try:
        _db.client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        print(_db.get_all_users())
    except Exception as e:
        print(e)
        pass