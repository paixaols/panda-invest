import datetime as dt
import streamlit as st

import controllers as ctr


def data_edited(data):
    # Insert
    addition = st.session_state['dividend_crud']['added_rows']
    if len(addition) > 0:
        ctr.dividend.insert_dividend({
            'data': addition[0]['data'],
            'ativo': addition[0]['ativo'],
            'valor': addition[0]['valor'],
            'conta': addition[0]['conta']
        })

    # Delete
    deletion = st.session_state['dividend_crud']['deleted_rows']
    if len(deletion) > 0:
        ids = data.iloc[deletion].loc[:, '_id'].tolist()
        ctr.dividend.delete_dividends(ids)

    # Update
    edition = st.session_state['dividend_crud']['edited_rows']
    if len(edition) > 0:
        for k, v in edition.items():
            _id = data['_id'].iloc[k]
            ctr.dividend.update_one(_id, v)


def create_page():
    data = ctr.dividend.get_dividends()

    # Section history
    st.subheader('Histórico de pagamentos')

    if data.shape[0] == 0:
        st.warning('Nada encontrado. Insira seus dividendos na seção *Detalhes*.', icon='⚠️')
    else:
        col1, col2, col3 = st.columns([1, 3, 1])
        time_span = col1.radio('Período', ['1A', '6M'])
        country = col3.radio('Local', sorted(data['local'].unique()))

        if time_span == '6M':
            days = 182
        elif time_span == '1A':
            days = 365
        cutoff = dt.date.today()-dt.timedelta(days=days)
        filtered_data = data.loc[
            (data['data'] > cutoff) & (data['local'] == country)
        ]
        grouped_filtered_data = filtered_data[['mês', 'valor']].groupby('mês').sum()
        col2.bar_chart(grouped_filtered_data, color='#cd332e')

    # Section details
    st.subheader('Detalhes')

    # Filters
    col1, col2 = st.columns(2)
    month = col1.selectbox('Mês', sorted(data['mês'].unique(), reverse=True))

    filtered_data = data.loc[data['mês'] == month]

    country_options = sorted(filtered_data['local'].unique())
    countries = col2.multiselect(
        'Local',
        country_options,
        default=country_options,
        placeholder='Selecione uma opção'
    )

    # Filtered data & table
    filtered_data = filtered_data.loc[
        data['local'].isin(countries)
    ]

    assets = ['BBAS3', 'SLG', 'XPLG11']
    config = {
        '_id': None,
        'userid': None,
        'mês': None,
        'local': None,
        'data': st.column_config.DateColumn('Data', max_value=dt.date.today(), required=True),
        'ativo': st.column_config.SelectboxColumn('Ativo', options=assets, required=True),
        'valor': st.column_config.NumberColumn('Valor', min_value=0, required=True),
        'conta': st.column_config.TextColumn('Conta', required=True)
    }

    # CRUD
    st.data_editor(
        filtered_data,
        column_config=config,
        hide_index=True,
        disabled=['_index'],
        key='dividend_crud',
        num_rows='dynamic',
        on_change=data_edited,
        args=[filtered_data]
    )
