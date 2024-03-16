import streamlit as st

import controllers as ctr


def save_changes(df):
    # Insert
    addition = st.session_state['account_crud']['added_rows']
    if len(addition) > 0:
        inserted = ctr.account.create_account(addition[0])

    # Delete
    deletion = st.session_state['account_crud']['deleted_rows']
    if len(deletion) > 0:
        ids = df.iloc[deletion].loc[:, '_id'].tolist()
        ctr.account.delete_accounts(ids)

    # Update
    edition = st.session_state['account_crud']['edited_rows']
    if len(edition) > 0:
        for k, v in edition.items():
            _id = df['_id'].iloc[k]
            ctr.account.update_account(_id, v)


def create_page():
    if not st.session_state['authenticated']:
        st.stop()

    df = ctr.account.get_accounts()

    currencies = ['BRL', 'EUR', 'UDS']
    config = {
        '_id': None,
        'userid': None,
        'bank': st.column_config.TextColumn('Banco', required=True),
        'currency': st.column_config.SelectboxColumn('Moeda', options=currencies, required=True),
    }

    # CRUD
    st.data_editor(
        df,
        column_config=config,
        key='account_crud',
        num_rows='dynamic',
        on_change=save_changes,
        args=[df]
    )
