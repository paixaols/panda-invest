import datetime as dt
import streamlit as st

import controllers as ctr


def save_changes(df):
    # Insert
    addition = st.session_state['dividend_crud']['added_rows']
    if len(addition) > 0:
        inserted = ctr.dividend.insert_dividend(addition[0])

    # Delete
    deletion = st.session_state['dividend_crud']['deleted_rows']
    if len(deletion) > 0:
        ids = df.iloc[deletion].loc[:, '_id'].tolist()
        ctr.dividend.delete_dividends(ids)

    # Update
    edition = st.session_state['dividend_crud']['edited_rows']
    if len(edition) > 0:
        for k, v in edition.items():
            _id = df['_id'].iloc[k]
            ctr.dividend.update_dividend(_id, v)


def create_page():
    if not st.session_state['authenticated']:
        st.stop()

    df, accounts, assets = ctr.dividend.get_dividends()

    # Section history
    st.subheader('Histórico de pagamentos')

    if df.shape[0] == 0:
        st.warning('Nada encontrado. Insira seus dividendos na seção *Detalhes*.', icon='⚠️')
    else:
        col1, col2, col3 = st.columns([1, 3, 1])
        time_span = col1.radio('Período', ['1A', '6M'])
        currency = col3.radio('Moeda', sorted(df['currency'].unique()))

        if time_span == '6M':
            days = 182
        elif time_span == '1A':
            days = 365
        cutoff = dt.datetime.now()-dt.timedelta(days=days)
        filtered_df = df.loc[
            (df['date'] > cutoff) & (df['currency'] == currency)
        ]
        grouped_filtered_df = filtered_df[['month', 'value']].groupby('month').sum()
        col2.bar_chart(grouped_filtered_df, color='#cd332e')

    # Section details
    st.subheader('Detalhes')

    # Filters
    col1, col2 = st.columns(2)
    month = col1.selectbox('Mês', sorted(df['month'].unique(), reverse=True))

    filtered_df = df.loc[df['month'] == month]

    currency_options = sorted(filtered_df['currency'].unique())
    currencies = col2.multiselect(
        'Moeda',
        currency_options,
        default=currency_options,
        placeholder='Selecione uma opção'
    )

    # Filtered data
    filtered_df = filtered_df.loc[
        df['currency'].isin(currencies)
    ]

    # CRUD
    config = {
        '_id': None,
        'userid': None,
        'month': None,
        'currency': None,
        'account_id': None,
        'asset_id': None,
        'date': st.column_config.DateColumn('Data', max_value=dt.date.today(), required=True),
        'asset': st.column_config.SelectboxColumn('Ativo', options=assets, required=True),
        'value': st.column_config.NumberColumn('Valor', min_value=0, step=0.01, required=True),
        'tax': st.column_config.NumberColumn('Imposto', min_value=0, step=0.01, required=True),
        'account': st.column_config.SelectboxColumn('Conta', options=accounts, required=True)
    }

    filtered_df.sort_values('date', inplace=True)
    st.data_editor(
        filtered_df,
        column_config=config,
        column_order=['date', 'asset', 'value', 'tax', 'account'],
        hide_index=True,
        disabled=['_index'],
        key='dividend_crud',
        num_rows='dynamic',
        on_change=save_changes,
        args=[filtered_df]
    )
