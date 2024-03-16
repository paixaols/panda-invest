import streamlit as st
from db import mongodb_engine as engine


@st.cache_resource
def get_database():
    return engine.get_database(st.secrets['DB']['NAME'])

db = get_database()


class Collection:
    def __init__(self):
        self.collection_name = str(self.__class__).split("'")[1].split('.')[-1].lower()

    def find(self, **kwargs):
        cursor = db[self.collection_name].find(kwargs)

        docs = []
        for doc in cursor:
            d = doc.copy()
            d['_id'] = str(d['_id'])
            docs.append(d)

        return docs
