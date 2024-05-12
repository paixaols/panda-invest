import streamlit as st

# st.set_page_config(
#     page_title='Panda Invest',
#     page_icon=':panda_face:',
#     layout='wide'
# )

import controllers as ctr
from app import login_required, menu

login_required()
menu()


def save_changes(df):
    # Insert
    addition = st.session_state['account_crud']['added_rows']
    if len(addition) > 0:
        ctr.accounts.create_bank_account(addition[0])

    # Delete
    deletion = st.session_state['account_crud']['deleted_rows']
    if len(deletion) > 0:
        ids = df.iloc[deletion].loc[:, '_id'].tolist()
        ctr.accounts.delete_bank_accounts(ids)

    # Update
    edition = st.session_state['account_crud']['edited_rows']
    if len(edition) > 0:
        for k, v in edition.items():
            _id = df['_id'].iloc[k]
            ctr.accounts.update_bank_account(_id, v)


response = ctr.accounts.get_bank_accounts()
df = response['data']

currencies = ['BRL', 'EUR', 'USD']
config = {
    '_id': None,
    'userid': None,
    'bank': st.column_config.TextColumn('Banco', required=True),
    'currency': st.column_config.SelectboxColumn('Moeda', options=currencies, required=True),
    'balance': st.column_config.NumberColumn('Saldo', min_value=0, step=0.01, required=True),
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
