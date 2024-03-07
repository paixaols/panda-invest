import datetime as dt
import streamlit as st

import controllers as ctr


def create_page():
    data = ctr.mock.dividends()

    tab1, tab2, tab3 = st.tabs(['Histórico', 'Mês', 'Novo'])

    # Tab history
    with tab1:
        st.subheader('Histórico de pagamentos')

        if data.shape[0] == 0:
            st.warning('Nada encontrado. Insira seus dividendos na aba *Novo*.', icon='⚠️')
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

    # Tab month
    with tab2:
        st.subheader('Pagamentos do mês')

        options = sorted(data['mês'].unique(), reverse=True)
        option = st.selectbox('Mês', options)
        filtered_data = data.loc[
            data['mês'] == option,
            ['data', 'ativo', 'valor', 'local']
        ]
        st.write(filtered_data)

    # Tab new
    with tab3:
        assets = ['BBAS3', 'SLG', 'XPLG11']
        with st.form(key='new_dividend'):
            st.subheader('Adicionar dividendo')
            st.selectbox(
                'Ativo',
                assets,
                index=None,
                placeholder='Selecione uma opção'
            )
            st.date_input('Data do pagamento', format='DD/MM/YYYY')
            st.text_input('Banco')
            st.number_input('Valor')
            st.form_submit_button('Enviar')
