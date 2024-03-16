import pandas as pd
import streamlit as st

from bson import ObjectId

from db import mongodb_engine as engine


@st.cache_resource
def get_database():
    return engine.get_database(st.secrets['DB']['NAME'])

db = get_database()


class Collection:
    def __init__(self):
        self.collection_name = str(self.__class__).split("'")[1].split('.')[-1].lower()

    def find(self, filter, as_dataframe=False):
        collection = db[self.collection_name]
        cursor = collection.find(filter)

        docs = []
        for doc in cursor:
            d = doc.copy()
            d['_id'] = str(d['_id'])
            docs.append(d)

        if as_dataframe:
            if len(docs) == 0:
                return pd.DataFrame(columns=self.fields)
            df = pd.DataFrame(docs)
            return df

        return docs

    def insert_one(self, obj):
        # Return False if fields are missing
        if not all( f in obj for f in self.fields ):
            return False

        # Filter extra fields
        obj = { k:v for k,v in obj.items() if k in self.fields }

        # Insert object
        result = db[self.collection_name].insert_one(obj)
        return result.acknowledged

    def delete_many(self, userid, ids):
        collection = db[self.collection_name]
        object_ids = [ ObjectId(_id) for _id in ids ]
        query = {
            'userid': userid,
            '_id': {'$in': object_ids}
        }
        result = collection.delete_many(query)
        return result.deleted_count

    def update_one(self, userid, _id, update):
        collection = db[self.collection_name]
        query = {
            'userid': userid,
            '_id': ObjectId(_id)
        }
        result = collection.update_one(query, {'$set': update})
        return result.modified_count
