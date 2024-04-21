import streamlit as st

import controllers as ctr


def save_changes(df):
    # Insert
    addition = st.session_state['asset_mngmt_crud']['added_rows']
    if len(addition) > 0:
        inserted = ctr.manage_assets.create_asset(addition[0])

    # Delete
    deletion = st.session_state['asset_mngmt_crud']['deleted_rows']
    if len(deletion) > 0:
        ids = df.iloc[deletion].loc[:, '_id'].tolist()
        ctr.manage_assets.delete_assets(ids)

    # Update
    edition = st.session_state['asset_mngmt_crud']['edited_rows']
    if len(edition) > 0:
        for k, v in edition.items():
            _id = df['_id'].iloc[k]
            ctr.manage_assets.update_asset(_id, v)


def create_page():
    if not st.session_state['authenticated']:
        st.stop()
    if st.session_state['user'].get('role') not in ['admin', 'super-admin']:
        st.warning('Você não tem permissão para acessar esta página', icon='⚠️')
        st.stop()

    df = ctr.manage_assets.get_assets()

    # CRUD
    asset_types = [
        'RF | CDB', 'RF | CRA', 'RF | CRI', 'RF | Debênture', 'RF | LCA', 'RF | LCI', 'RF | Tesouro IPCA', 'RF | Tesouro Prefixado', 'RF | Tesouro Selic',
        'RV | Ação', 'RV | BDR', 'RV | ETF', 'RV | FII', 'RV | REIT', 'RV | Stock'
    ]
    currencies = ['BRL', 'EUR', 'USD']
    config = {
        '_id': None,
        'name': st.column_config.TextColumn('Nome', required=True),
        'description': st.column_config.TextColumn('Descrição', required=True),
        'code': st.column_config.TextColumn('Código', required=True),
        'type': st.column_config.SelectboxColumn('Tipo', options=asset_types, required=True),
        'currency': st.column_config.SelectboxColumn('Moeda', options=currencies, required=True),
    }

    st.data_editor(
        df,
        column_config=config,
        key='asset_mngmt_crud',
        num_rows='dynamic',
        on_change=save_changes,
        args=[df]
    )
