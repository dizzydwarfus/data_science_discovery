import pandas as pd
import streamlit as st
import json
import string
# import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


# """
# plotly colors:
#     aliceblue, antiquewhite, aqua, aquamarine, azure,
#     beige, bisque, black, blanchedalmond, blue,
#     blueviolet, brown, burlywood, cadetblue,
#     chartreuse, chocolate, coral, cornflowerblue,
#     cornsilk, crimson, cyan, darkblue, darkcyan,
#     darkgoldenrod, darkgray, darkgrey, darkgreen,
#     darkkhaki, darkmagenta, darkolivegreen, darkorange,
#     darkorchid, darkred, darksalmon, darkseagreen,
#     darkslateblue, darkslategray, darkslategrey,
#     darkturquoise, darkviolet, deeppink, deepskyblue,
#     dimgray, dimgrey, dodgerblue, firebrick,
#     floralwhite, forestgreen, fuchsia, gainsboro,
#     ghostwhite, gold, goldenrod, gray, grey, green,
#     greenyellow, honeydew, hotpink, indianred, indigo,
#     ivory, khaki, lavender, lavenderblush, lawngreen,
#     lemonchiffon, lightblue, lightcoral, lightcyan,
#     lightgoldenrodyellow, lightgray, lightgrey,
#     lightgreen, lightpink, lightsalmon, lightseagreen,
#     lightskyblue, lightslategray, lightslategrey,
#     lightsteelblue, lightyellow, lime, limegreen,
#     linen, magenta, maroon, mediumaquamarine,
#     mediumblue, mediumorchid, mediumpurple,
#     mediumseagreen, mediumslateblue, mediumspringgreen,
#     mediumturquoise, mediumvioletred, midnightblue,
#     mintcream, mistyrose, moccasin, navajowhite, navy,
#     oldlace, olive, olivedrab, orange, orangered,
#     orchid, palegoldenrod, palegreen, paleturquoise,
#     palevioletred, papayawhip, peachpuff, peru, pink,
#     plum, powderblue, purple, red, rosybrown,
#     royalblue, saddlebrown, salmon, sandybrown,
#     seagreen, seashell, sienna, silver, skyblue,
#     slateblue, slategray, slategrey, snow, springgreen,
#     steelblue, tan, teal, thistle, tomato, turquoise,
#     violet, wheat, white, whitesmoke, yellow,
#     yellowgreen
# """

#####################################################

# Define dropdowns and set page config

#####################################################

with open(r'D:\\lianz\Desktop\\Python\data_science_discovery\\personal_finance\\tickers.json', 'r') as f:
    tickers = json.load(f)

page_placeholder = st.sidebar.selectbox('What do you want to see?', [
                                        'Financial Statements', 'DCF Calculator', 'Charts'])

ticker_list_box = st.sidebar.selectbox(
    "Select a ticker symbol:", sorted(list(set(tickers))), key="ticker_list")

company_statements = ['income-statement',
                      'cash-flow-statement', 'balance-sheet-statement']

if tickers != None:   
    with open(f'D:\lianz\Desktop\Python\data_science_discovery\personal_finance\{company_statements[0]}\{ticker_list_box}.json', 'r') as f:
        income_statement = json.load(f)

    with open(f'D:\lianz\Desktop\Python\data_science_discovery\personal_finance\{company_statements[1]}\{ticker_list_box}.json', 'r') as f:
        cash_flow_statement = json.load(f)

    with open(f'D:\lianz\Desktop\Python\data_science_discovery\personal_finance\{company_statements[2]}\{ticker_list_box}.json', 'r') as f:
        balance_sheet = json.load(f)


#####################################################

# Define functions to create dictionaries for
# historical data

#####################################################

terms_interested = {'Revenue': 'revenue',
                    'Gross margin%': 'grossProfitRatio',
                    'Operating Income': 'operatingIncome',
                    'Operating Margin %': 'operatingIncomeRatio',
                    'Net Income': 'netIncome',
                    'Net Income Margin': 'netIncomeRatio',
                    'Earnings per Share': 'epsdiluted',
                    'Shares Oustanding (diluted)': 'weightedAverageShsOutDil',
                    'Dividends': 'dividendsPaid',
                    'Operating Cash Flow': 'operatingCashFlow',
                    'Cap Spending': 'capitalExpenditure',
                    'Free Cash Flow': 'freeCashFlow',
                    'Free Cash Flow per Share': 'freeCashFlow',
                    'Working Capital': 'totalCurrentAssets - totalCurrentLiabilities',
                    'Net Debt': 'netDebt'
                    }

def read_statement(filepath, mode: list(['r','w','r+','w+'])):
    with open(filepath, f'{mode}') as f:
        statement = json.load(f)

        return statement

def generate_key_metrics(financial_statement, list_of_metrics):
    l = []
    dict_holder = {}
    columns = financial_statement[0].keys()

    for n in list_of_metrics:

        if n in columns:
            for i, x in enumerate(financial_statement[::-1]):
                dict_holder[x['calendarYear']] = x[f'{n}']

            l.append(dict_holder)
            dict_holder = {}

        else:
            pass

    df = pd.DataFrame.from_records(
        l, index=[items for items in list_of_metrics if items in columns])

    # df.style.format({f"{df}": "{:,}"})

    return df


def generate_plots(dataframe, arrangement: tuple):

    # create columns to place charts based on arrangement specified (columns in each row)
    cols = st.columns(arrangement)
    dataframe = dataframe.T
    m = 0

    for i, n in enumerate(terms_interested.values()):
        if n in dataframe.columns:
            if m >= len(cols):
                m = 0
            else:

                # Define growth rates Y-o-Y
                growth = dataframe[f'{n}'].pct_change(
                    periods=1).fillna(0)
                fig = make_subplots(specs=[[{"secondary_y": True}]])

                # Add traces (graphs)
                fig.add_trace(
                    go.Scatter(
                        x=dataframe.index, y=dataframe[f'{n}'], mode="lines+markers", name=f"{n.capitalize()}"),
                    secondary_y=False,
                )

                fig.add_trace(
                    go.Bar(
                        x=dataframe.index, y=growth, text=[i for i in growth], marker=dict({'color': 'darkorange'}), texttemplate="%{value:.1%}", textposition="inside", name="Growth Y-o-Y"),
                    secondary_y=True,
                )

                # Update figure title, legend, axes
                fig.update_layout(showlegend=False,
                                  xaxis_title='Year', yaxis_title=f'{n}')
                fig.update_yaxes(
                    title_text=f"<b>{n.capitalize()}</b>", secondary_y=False)
                fig.update_yaxes(
                    title_text="Growth Y-o-Y", secondary_y=True)

                # # Add horizontal lines to show max and min values
                fig.add_hline(y=dataframe[f'{n}'].max(
                ), line_color='green', line_dash='dash')
                fig.add_hline(y=dataframe[f'{n}'].min(
                ), line_color='red', line_dash='dash')

                # Plot the chart in its respective column based on loop
                cols[m].plotly_chart(
                    fig, use_container_width=True,)

                # Add 1 to column so next graph will be plotted on next column
                m += 1

#####################################################

# FInancial Statements Page

#####################################################


if page_placeholder == 'Financial Statements':

    st.write(f"""

    # {ticker_list_box}

    """)

    income_tab, cash_tab, balance_tab, key_metrics_tab = st.tabs(
        ["Income Statement", "Cash Flow", "Balance Sheet", "Key Metrics"], )

    for i, x in enumerate([income_tab, cash_tab, balance_tab]):
        with x:
            with open(f'D:\lianz\Desktop\Python\data_science_discovery\personal_finance\{company_statements[i]}\{ticker_list_box}.json', 'r') as f:
                tab_statement = json.load(f)

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
                index=[tab_statement[i]['calendarYear'] for i in year_list]).T

            st.dataframe(df_financial_statements,
                         use_container_width=bool(f'st.session_state.use_container_width_income_tab'))

    with key_metrics_tab:
        master_table = pd.concat([generate_key_metrics(read_statement(f'D:\lianz\Desktop\Python\data_science_discovery\personal_finance\{x}\{ticker_list_box}.json','r'), terms_interested.values()) for x in company_statements],axis=0).drop_duplicates()
        mt_growth = master_table.T.pct_change(periods=1)
        # mt_growth.apply(lambda x: "{:.0%}".format(x))

        st.dataframe(mt_growth)

        # Container to show some key metrics from table
        metric_container = st.container()
        metric_columns = st.columns([1,1,1,1,1])

        st.metric(label=f'{mt_growth.columns[0]}', value=mt_growth.iloc[:,0].mean(skipna=True)/len(mt_growth.index), delta=mt_growth.iloc[-1,0])

        # To create the master key metrics table compiled from statements
        st.dataframe(master_table.drop_duplicates())

        
# TODO: create function to combine all three statements so generate_key_metrics can be used on a single object instead of multiple filepaths

#####################################################

# DCF Calculator
 ############################################

if page_placeholder == 'DCF Calculator':
    st.title("DCF Calculator")

    st.write("""

    - show current growth rates (considering past 5 years)
    - show current stock price
    - use input fields for discount rate, growth rate, and terminal multiple
    - discount rate: use WACC, or expected return rate, or 10Y treasury yield
    - choose either growth on dividend (for slow growth), eps, or free cash flow
    - terminal multiple: what is the projected PE ratio 10 years from now?

    """)
    c1, c2, c3 = st.columns([1, 1, 1])

    # c2.metric(label=f'EPS Growth (1Y)',
    #           value=f'{sum(df(income_statement))}',
    #           delta='0.5%')

#####################################################

# Charts Page

#####################################################

if page_placeholder == 'Charts':

    # statement_selection = st.selectbox(
    #     "Select:", company_statements, format_func=lambda a: string.capwords(a.replace("-", " ")))

    with open(f'D:\lianz\Desktop\Python\data_science_discovery\personal_finance\{company_statements[0]}\{ticker_list_box}.json', 'r') as f:
        income = json.load(f)


    st.title(f"""

    {ticker_list_box}

    """)

    st.write(f"""

        # Financials Growth (last {len(income)} years)

        """)

    key_metrics_table = generate_key_metrics(
        income, terms_interested.values())

    generate_plots(key_metrics_table, [1,1,1,1,1,1])
    key_metrics_table

    """
    Show eps by industry/sector: create lists containing ticker
                                symbols belonging to an industry
                                use the selectbox to select the lists.
    """

    st.write("""

         Metrics to be shown (margin of safety):
         ---

         From Income-Statement:
         1. revenue - 'revenue'
         2. gross margin% - 'grossProfitRatio'
         3. operating income - 'operatingIncome'
         4. operating margin% - 'operatingIncomeRatio'
         5. net income - 'netincome'
         17. net income margin - 'netincomeRatio'
         6. earnings per share - 'epsdiluted'
         9. shares oustanding - 'weightedAverageShsOutDil'

         From Cash-Flow-Statement:
         7. dividends - 'dividendsPaid' (it is in negative so make it positive)
         11. operating cash flow - 'operatingCashFlow'
         12. cap spending - 'capitalExpenditure'
         13. free cash flow - 'freeCashFlow'
         14. free cash flow per share - 'freeCashFlow'

         From Balance-Sheet:
         15. working capital - 'totalCurrentAssets' - 'totalCurrentLiabilities'
         16. Net debt - 'netDebt' (total debt minus any existing cash balances)

         Unknown:
         8. payout ratio% - ''
         10. book value per share

         Keypoint
         : range of value: not exactly, value is adequate, approximate measure of intrinsic value may be sufficient(e.g. elon's twitter acquisition, "order of magnitude more valuable than current even if he is overpaying now").

         """)
    todos = [
        'net present value',
        'private market value - conservative historical value',
        'personal value - how much you would pay personally based on assets for the business',
        'liquidation value - best for unprofitable businesses trading below book value',
        'Stock market value - compare similar businesses (potential spin-off)',
        'Reflexivity - how rising stock prices influence underlying values (raising capital when stock prices are high)'
    ]

    for items in todos:
        st.checkbox(f"{items}")

    """
    Session state and how to utilize it
    -> if "photo" not in st.session_state:
        st.session_state['photo'] = 'not done'

    def change_photo_state():
        st.session_state['photo'] = 'done'

    a streamlit function (on_change=change_photo_state)
    """
st.markdown("***Data provided by Financial Modeling Prep***")
