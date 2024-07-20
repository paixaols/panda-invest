import datetime as dt
import pandas as pd
import streamlit as st

from bson import ObjectId

from db import mongodb_engine as engine

INSERT_COOLDOWN = 1# cooldown time in seconds


@st.cache_resource
def get_database():
    return engine.get_database(st.secrets['DB']['NAME'])

db = get_database()


class Collection:
    def __init__(self):
        self.collection_name = str(self.__class__).split("'")[1].split('.')[-1].lower()

    def find(self, filter={}, as_dataframe=False):
        if '_id' in filter:
            filter['_id'] = ObjectId(filter['_id'])
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

    def insert_one(self, obj, datetime_fields={}, missing_fields='abort'):
        last_insert = st.session_state.get('last_insert')
        if last_insert is not None:
            if dt.datetime.now().timestamp()-last_insert < INSERT_COOLDOWN:
                return False

        # Convert datetime fields from string
        for field in datetime_fields:
            format = datetime_fields[field]
            obj[field] = dt.datetime.strptime(obj[field], format)

        # If missing_fields is 'ignore' save just the existing fields, ignoring the missing ones
        if missing_fields != 'ignore':
            # Return False if fields are missing
            if not all( f in obj for f in self.fields ):
                return False

        # Filter extra fields
        obj = { k:v for k,v in obj.items() if k in self.fields }

        # Insert object
        result = db[self.collection_name].insert_one(obj)
        st.session_state['last_insert'] = dt.datetime.now().timestamp()

        return result.acknowledged

    def delete_many(self, ids):
        collection = db[self.collection_name]
        object_ids = [ ObjectId(_id) for _id in ids ]
        result = collection.delete_many(
            {'_id': {'$in': object_ids}}
        )
        return result.deleted_count

    def update_one(self, _id, implement, datetime_fields={}):
        for field in datetime_fields:
            if field in implement['$set']:
                format = datetime_fields[field]
                implement['$set'][field] = dt.datetime.strptime(
                    implement['$set'][field], format
                )

        # Filter extra fields
        if '$set' in implement:
            implement['$set'] = { k:v for k,v in implement['$set'].items() if k in self.fields }
        if '$inc' in implement:
            implement['$inc'] = { k:v for k,v in implement['$inc'].items() if k in self.fields }

        collection = db[self.collection_name]
        result = collection.update_one(
            {'_id': ObjectId(_id)},
            implement
        )
        return result.modified_count
