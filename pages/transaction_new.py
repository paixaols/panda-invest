import datetime as dt
import streamlit as st

import controllers as ctr
from app import login_required, menu

login_required()
menu()

def buy_sell_form():
    with st.form('transaction_form'):
        quantity = st.number_input(
            'Quantidade',
            step=1.,
            min_value=0.
        )
        value = st.number_input(
            'Valor',
            step=0.01,
            min_value=0.
        )
        fee = st.number_input(
            'Taxas',
            step=0.01,
            min_value=0.
        )
        submit = st.form_submit_button('Salvar')
    data = {
        'quantity': quantity,
        'value': value,
        'fee': fee,
    }
    return submit, data


def split_form():
    with st.form('transaction_form'):
        st.write('Quantidade')
        col1, col2 = st.columns(2)
        with col1:
            pre = st.number_input(
                'Pré-desdobramento',
                step=1.,
                min_value=1.
            )
        with col2:
            post = st.number_input(
                'Pós-desdobramento',
                step=1.,
                min_value=1.
            )
        submit = st.form_submit_button('Salvar')
    data = {
        'pre_split': pre,
        'post_split': post,
    }
    return submit, data


def reverse_split_form():
    with st.form('transaction_form'):
        st.write('Quantidade')
        col1, col2 = st.columns(2)
        with col1:
            pre = st.number_input(
                'Pré-grupamento',
                step=1.,
                min_value=1.
            )
        with col2:
            post = st.number_input(
                'Pós-grupamento',
                step=1.,
                min_value=1.
            )
        submit = st.form_submit_button('Salvar')
    data = {
        'pre_split': pre,
        'post_split': post,
    }
    return submit, data


response = ctr.accounts.get_bank_accounts()
account_options = list(response['data'][['_id', 'bank']].to_records(index=False))

response = ctr.manage_assets.get_assets()
asset_options = list(response['data'][['_id', 'code']].to_records(index=False))

# General info
with st.container(border=True):
    event = st.selectbox(
        'Transação',
        ['Amortização', 'Bonificação', 'Compra', 'Desdobramento', 'Grupamento', 'Venda'],
        index=2,
        placeholder='Selecione um tipo de evento',
    )
    date = st.date_input(
        'Data',
        value=None,
        max_value=dt.date.today()
    )
    asset = st.selectbox(
        'Ativo',
        [ f'{x[1]} (id: {x[0]})' for x in asset_options ],
        index=None,
        placeholder='Selecione uma opção'
    )
    account = st.selectbox(
        'Conta',
        [ f'{x[1]} (id: {x[0]})' for x in account_options ],
        index=None,
        placeholder='Selecione uma opção'
    )

# Event specific data
if event == 'Compra' or event == 'Venda':
    submit, data = buy_sell_form()
elif event == 'Desdobramento':
    submit, data = split_form()
elif event == 'Grupamento':
    submit, data = reverse_split_form()
else:
    submit, data = False, {}

if submit:
    data['event'] = event
    data['date'] = date
    data['asset'] = asset
    data['account'] = account

    response = ctr.transaction.submit_new_transaction(data)
    if response['success']:
        # st.success(response['message'], icon='✔️')
        st.switch_page('pages/transaction.py')
    else:
        st.warning(response['message'], icon='⚠️')
