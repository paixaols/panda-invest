import datetime as dt
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

    def find(self, filter={}, as_dataframe=False):
        collection = db[self.collection_name]
        cursor = collection.find(filter)

        docs = []
        for doc in cursor:
            d = doc.copy()
            d['_id'] = str(d['_id'])
            docs.append(d)

        if as_dataframe:
            if len(docs) == 0:
                return pd.DataFrame(columns=['_id']+self.fields)
            df = pd.DataFrame(docs)
            return df

        return docs

    def insert_one(self, obj, datetime_fields={}):
        # Convert datetime fields from string
        for field in datetime_fields:
            format = datetime_fields[field]
            obj[field] = dt.datetime.strptime(obj[field], format)

        # Return False if fields are missing
        if not all( f in obj for f in self.fields ):
            return False

        # Filter extra fields
        obj = { k:v for k,v in obj.items() if k in self.fields }

        # Insert object
        result = db[self.collection_name].insert_one(obj)
        return result.acknowledged

    def delete_many(self, ids):
        collection = db[self.collection_name]
        object_ids = [ ObjectId(_id) for _id in ids ]
        result = collection.delete_many(
            {'_id': {'$in': object_ids}}
        )
        return result.deleted_count

    def update_one(self, _id, update, datetime_fields={}):
        for field in datetime_fields:
            if field in update:
                format = datetime_fields[field]
                update[field] = dt.datetime.strptime(update[field], format)

        # Filter extra fields
        update = { k:v for k,v in update.items() if k in self.fields }

        collection = db[self.collection_name]
        result = collection.update_one(
            {'_id': ObjectId(_id)},
            {'$set': update}
        )
        return result.modified_count
