import pandas as pd
import streamlit as st
import numpy as np
from pymongo import ASCENDING, DESCENDING
from functions import balance_sheet_collection, income_collection, cash_collection, company_profile, terms_interested, company_statements, read_statement, generate_key_metrics, create_financial_page, make_pretty

#####################################################

# Define dropdowns and set page config

#####################################################


tickers = list(set([i['symbol'] for i in balance_sheet_collection.find()]))

ticker_list_box = st.sidebar.selectbox(
    "Select a ticker symbol:", sorted(tickers), key="ticker_list")

companyA_info = read_statement(company_profile, ticker_list_box)[0]

same_sector = sorted([i for i in tickers if read_statement(company_profile, i)[0]['sector'] == companyA_info['sector']])

ticker_compare = st.sidebar.selectbox("Select a ticker symbol to compare:", same_sector, key="ticker_compare")

companyB_info = read_statement(company_profile, ticker_compare)[0]

compare_companies = st.sidebar.checkbox('Compare', key='compare_companies')

#####################################################

# FInancial Statements Page

#####################################################

if compare_companies:
    l0, l1 = st.columns([1,1])
    t0, t1 = st.columns([1,1])
    p1, p2, p3, p4, p5, p6 = st.columns([1, 1, 1, 1, 1, 1])
    c1, c2 = st.columns([1,1])

    create_financial_page(ticker_list_box, companyA_info, l0, t0, c1, [p1,p2,p3])
    create_financial_page(ticker_compare, companyB_info, l1, t1, c2, [p4,p5,p6])

else:
    st.markdown(f"""

    ![Logo]({companyA_info['image']} "Company Logo")

    # {ticker_list_box} 
    ---
    ### Company Profile

    {companyA_info['description']}

    *<span style="font-size:1em;">Visit [{companyA_info['website']}]({companyA_info['website']}) to learn more.</span>*

    """, unsafe_allow_html=True)

    profile = st.container()
    p1, p2, p3, p4, p5, p6 = profile.columns([1, 1, 1, 1, 1, 1])

    p1.markdown(
    f"""<span style='font-size:1.5em;'>CEO</span>  
    :green[{companyA_info['ceo']}]

    """, unsafe_allow_html=True)

    p2.markdown(
    f"""<span style='font-size:1.5em;'>Exchange</span>  
    :green[{companyA_info['exchangeShortName']}]

    """, unsafe_allow_html=True)

    p3.markdown(
    f"""<span style='font-size:1.5em;'>Industry</span>  
    :green[{companyA_info['industry']}]

    """, unsafe_allow_html=True)

    p4.markdown(
    f"""<span style='font-size:1.5em;'>Sector</span>  
    :green[{companyA_info['sector']}]

    """, unsafe_allow_html=True)

    p5.markdown(
    f"""<span style='font-size:1.5em;'>Country</span>  
    :green[{companyA_info['country']}]

    """, unsafe_allow_html=True)

    p6.markdown(
    f"""<span style='font-size:1.5em;'>Number of Employees</span>  
    :green[{int(companyA_info['fullTimeEmployees']):,}]

    """, unsafe_allow_html=True)


    income_tab, cash_tab, balance_tab, key_metrics_tab = st.tabs(
        ["Income Statement", "Cash Flow", "Balance Sheet", "Key Metrics"], )

    for i, x in enumerate([income_tab, cash_tab, balance_tab]):
        with x:
            tab_statement = [j for j in company_statements[i].find({'symbol':ticker_list_box}).sort('date', DESCENDING)]

            year_range = st.slider('Select year range (past n years):',
                                    min_value=1,
                                    max_value=int(
                                        tab_statement[0]['calendarYear'])-int(tab_statement[-1]['calendarYear'])+1,
                                    key=f'{ticker_list_box}_{x}_{i}')

            year_list = list(range(year_range))

            st.checkbox("Use container width",
                        value=False,
                        key=f'use_container_width_{x}_{i}')

            df_financial_statements = pd.DataFrame.from_records(
                tab_statement[year_list[0]:year_list[-1]+1],
                index=[tab_statement[i]['calendarYear'] for i in year_list]).iloc[::-1,1:]
            df_financial_statements = df_financial_statements.style.pipe(make_pretty, use_on='statements')
                                                                        

            st.dataframe(df_financial_statements,
                            use_container_width=bool(f'st.session_state.use_container_width_income_tab'))

    with key_metrics_tab:
        master_table = pd.concat([generate_key_metrics(read_statement(x,ticker_list_box), terms_interested.values()) for x in company_statements],axis=0).drop_duplicates()
        master_table = master_table.loc[~master_table.index.duplicated(keep='first'),:]
        mt_growth = master_table.T.pct_change(periods=1).style.pipe(make_pretty, use_on='metric')

        st.dataframe(mt_growth)

        # st.metric(label=f'{mt_growth.columns[0]}', value=mt_growth.iloc[:,0].mean(skipna=True)/len(mt_growth.index), delta=mt_growth.iloc[-1,0])

        # To create the master key metrics table compiled from statements
        st.dataframe(master_table)


st.markdown("***Data provided by Financial Modeling Prep***")
