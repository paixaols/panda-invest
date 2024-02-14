from pymongo import MongoClient

from .settings import MONGODB_URI


def get_client():
    client = MongoClient(MONGODB_URI)
    return client


def get_database(db_name):
    db = get_client()[db_name]
    return db


def get_collection(db_name, collection_name):
    collection = get_database(db_name=db_name)[collection_name]
    return collection