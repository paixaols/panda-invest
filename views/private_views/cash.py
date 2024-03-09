import streamlit as st

import controllers as ctr


def create_page():
    data = ctr.mock.cash()
    if data.shape[0] == 0:
        st.warning('Nada encontrado.', icon='⚠️')
    else:
        df = data[['Moeda', 'Saldo']].groupby('Moeda').sum()

        st.subheader('Geral')
        st.write(df)

        st.subheader('Detalhes')
        st.write(data)
