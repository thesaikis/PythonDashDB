from pymongo import MongoClient


class MongoDB:
    def __init__(self, database="academicworld", host="localhost", port=27017):
        self.database = database
        self.host = host
        self.port = port
        self.client = None
        self.db = None

        # Use to store last accessed collection
        self.collection = "faculty"

    def connect(self):
        self.client = MongoClient(host=self.host, port=self.port)
        self.db = self.client[self.database]

    def execute_query(self, collection_name, query):
        collection = self.db[collection_name]
        self.collection = collection
        return collection.find(query)

    def close(self):
        self.client.close()
