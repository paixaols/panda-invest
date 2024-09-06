import datetime as dt
import streamlit as st

import controllers as ctr
from app import login_required, menu

login_required()
menu()

def buy_sell_form(data):
    with st.form('transaction_form'):
        quantity = st.number_input(
            'Quantidade',
            value=data['quantity'],
            step=1.,
            min_value=0.
        )
        value = st.number_input(
            'Valor',
            value=data['value'],
            step=0.01,
            min_value=0.
        )
        fee = st.number_input(
            'Taxas',
            value=data['fee'],
            step=0.01,
            min_value=0.
        )
        submit = st.form_submit_button('Salvar')
    form_data = {
        'quantity': quantity,
        'value': value,
        'fee': fee,
    }
    return submit, form_data


def split_form(data):
    with st.form('transaction_form'):
        st.write('Quantidade')
        col1, col2 = st.columns(2)
        with col1:
            pre = st.number_input(
                'Pré-desdobramento',
                value=data['pre_split'],
                step=1.,
                min_value=1.
            )
        with col2:
            post = st.number_input(
                'Pós-desdobramento',
                value=data['post_split'],
                step=1.,
                min_value=1.
            )
        submit = st.form_submit_button('Salvar')
    form_data = {
        'pre_split': pre,
        'post_split': post,
    }
    return submit, form_data


def reverse_split_form(data):
    with st.form('transaction_form'):
        st.write('Quantidade')
        col1, col2 = st.columns(2)
        with col1:
            pre = st.number_input(
                'Pré-grupamento',
                value=data['pre_split'],
                step=1.,
                min_value=1.
            )
        with col2:
            post = st.number_input(
                'Pós-grupamento',
                value=data['post_split'],
                step=1.,
                min_value=1.
            )
        submit = st.form_submit_button('Salvar')
    form_data = {
        'pre_split': pre,
        'post_split': post,
    }
    return submit, form_data


item_id = st.session_state['update']
response = ctr.transaction.get_transaction(item_id)
transaction_data = response['data']

response = ctr.accounts.get_bank_accounts()
account_options = list(response['data'][['_id', 'bank']].to_records(index=False))

response = ctr.manage_assets.get_assets()
asset_options = list(response['data'][['_id', 'name', 'code']].to_records(index=False))

# General info
with st.container(border=True):
    event = st.text_input(
        'Transação',
        value=transaction_data['event'],
        disabled=True
    )
    date = st.date_input(
        'Data',
        value=transaction_data['date'],
        max_value=dt.date.today()
    )
    options = [ f'{x[1]} (id: {x[0]})' for x in asset_options ]
    for i in range(len(options)):
        if options[i].endswith(transaction_data['asset_id']+')'):
            option_index = i
            break
    else:
        option_index = None
    asset = st.selectbox(
        'Ativo',
        [ f'{x[1]} - {x[2]} (id: {x[0]})' for x in asset_options ],
        index=option_index,
        placeholder='Selecione uma opção'
    )
    options = [ f'{x[1]} (id: {x[0]})' for x in account_options ]
    for i in range(len(options)):
        if options[i].endswith(transaction_data['account_id']+')'):
            option_index = i
            break
    else:
        option_index = None
    account = st.selectbox(
        'Conta',
        options,
        index=option_index,
        placeholder='Selecione uma opção'
    )

# Event specific data
if event == 'Compra' or event == 'Venda':
    submit, form_data = buy_sell_form(transaction_data)
elif event == 'Desdobramento':
    submit, form_data = split_form(transaction_data)
elif event == 'Grupamento':
    submit, form_data = reverse_split_form(transaction_data)
else:
    submit, form_data = False, {}

if submit:
    form_data['event'] = event
    form_data['date'] = date
    form_data['asset'] = asset
    form_data['account'] = account

    response = ctr.transaction.update_transaction(item_id, form_data)
    if response['success']:
        st.session_state['update'] = None# Uncomment ASAP
        # st.success(response['message'], icon='✔️')
        st.switch_page('pages/transaction.py')
    else:
        st.warning(response['message'], icon='⚠️')
