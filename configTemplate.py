import pymongo
from pymongo import MongoClient

cluster = MongoClient("")
db = cluster[""]
collection = db[""]

apiToken = ""