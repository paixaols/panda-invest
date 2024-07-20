import streamlit as st

import controllers as ctr
from app import login_required, menu

login_required()
menu()


def btn_new_onclick():
    st.switch_page('pages/transaction_new.py')


def btn_update_onclick():
    ids = st.session_state['selected_rows'].loc[:, '_id'].to_list()
    if len(ids) > 0:
        st.session_state['update'] = ids[0]
        st.switch_page('pages/transaction_update.py')


def btn_delete_onclick():
    ids = st.session_state['selected_rows'].loc[:, '_id'].to_list()
    if len(ids) > 0:
        ctr.transaction.delete_transactions(ids)


# Filter
event = st.selectbox(
    'Eventos:',
    ['Amortização', 'Compra', 'Desdobramento', 'Grupamento', 'Venda'],
    index=None,
    placeholder='Selecione um tipo de evento',
)
if event == 'Compra' or event == 'Venda':
    column_order = ['date', 'event', 'asset', 'quantity', 'value', 'tax', 'account']
elif event in ['Desdobramento', 'Grupamento']:
    column_order = ['date', 'event', 'asset', 'pre_split', 'post_split', 'account']
else:
    column_order = ['date', 'event', 'asset', 'account']

# Action buttons
col1, col2, col3, _ = st.columns(4)
with col1:
    if st.button('Novo'):
        btn_new_onclick()
with col2:
    if st.button('Editar'):
        btn_update_onclick()
with col3:
    if st.button('Apagar'):
        btn_delete_onclick()

# Data
df, accounts, assets = ctr.transaction.get_transactions()
if event is not None:
    df = df[df['event'] == event]
    df.reset_index(drop=True, inplace=True)
df['selected'] = False
df.sort_values('date', inplace=True)
df.reset_index(inplace=True, drop=True)

# Table
config = {
    '_id': None,
    'userid': None,
    'account_id': None,
    'asset_id': None,
    'date': st.column_config.DateColumn('Data', format='DD/MM/YYYY'),
    'event': st.column_config.TextColumn('Evento'),
    'asset': st.column_config.TextColumn('Ativo'),
    'pre_split': st.column_config.NumberColumn(
        'Fator pré',
        help='Fator pré grupamento ou desdobramento de ações'
    ),
    'post_split': st.column_config.NumberColumn(
        'Fator pós',
        help='Fator pós grupamento ou desdobramento de ações'
    ),
    'account': st.column_config.TextColumn('Conta'),
    'selected': st.column_config.CheckboxColumn(
        'Selecionar',
        help='Selecione para editar ou apagar',
        default=False,
        required=True
    ),
}

st.data_editor(
    df,
    hide_index=True,
    column_config=config,
    column_order=column_order+['selected'],
    disabled=column_order,
    key='transaction_crud',
)
edited_rows = st.session_state['transaction_crud']['edited_rows']
idx_selected_rows = [ k for k, v in edited_rows.items() if v['selected'] ]
st.session_state['selected_rows'] = df.loc[idx_selected_rows]
