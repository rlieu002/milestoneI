# Import libraries
import streamlit as st
import pandas as pd
import altair as alt

st.markdown("# Analysis")

# Import datasets

# CPI: consumer price index (https://fred.stlouisfed.org/series/CPIAUCSL)
cpi_data = pd.read_csv('./data/CPIAUCSL.csv')

# PCE: personal consumption expenditures (https://fred.stlouisfed.org/series/PCE)
pce_data = pd.read_csv('./data/PCE.csv')

# SAVINGS: personal saving rate (https://fred.stlouisfed.org/series/PSAVERT)
savings_data = pd.read_csv('./data/PSAVERT.csv')

# REV CREDIT: revolving consumer credit (https://fred.stlouisfed.org/series/REVOLSL)
credit_data = pd.read_csv('./data/REVOLSL.csv')

# UNEMPL: unemployment rate (https://fred.stlouisfed.org/series/UNRATE)
unemployment_data = pd.read_csv('./data/UNRATE.csv')

# FED FUND RATE: interest rate (https://fred.stlouisfed.org/series/DFEDTARU)
interest_data = pd.read_csv('./data/DFEDTARU.csv')

st.dataframe(interest_data.head(2))

def normalize_col(df, col_name):
    mean = df.mean().loc[col_name]  
    std = df.std().loc[col_name]
    df[col_name] = df[col_name].apply(lambda x: (x - mean) / std)

    return df

def get_combined_df(df_list, months):
    combined_df = None
    
    for df in df_list:
        start = df['DATE'].size - months
        df_copy = df[start:].copy()
        print(df_copy.tail(2))
        
        combined_df = df_copy if combined_df is None else combined_df.merge(df_copy, on='DATE', how='outer')
        
    return combined_df

def get_combined_df_norm(df_list_norm, months):
    combined_df_norm = None
    
    for df in df_list_norm:
        start = df['DATE'].size - months
        df_copy = df[start:].copy()
        df_copy = normalize_col(df_copy, df_copy.columns[1])
        print(df_copy.tail(2))
        
        combined_df_norm = df_copy if combined_df_norm is None else combined_df_norm.merge(df_copy, on='DATE', how='outer')
        
    return combined_df_norm

st.markdown('### Consumer Price Index & Personal Consumption Expenditure')
df_CPI_PCE = get_combined_df_norm([cpi_data, pce_data], 48)
df_CPI_PCE = df_CPI_PCE.rename(columns={'CPIAUCSL':'CPI'})
df_CPI_PCE = df_CPI_PCE.melt(id_vars=['DATE'],var_name='INDEX')

df_CPI_PCE['DATE'] = pd.to_datetime(df_CPI_PCE['DATE'])
df_CPI_PCE = df_CPI_PCE[df_CPI_PCE['DATE'] >= '2020-08-01']

st.dataframe(df_CPI_PCE.head())
df_CPI_PCE.dtypes
# CPI vs PCE dataframe
df_CPI_PCE = get_combined_df_norm([cpi_data, pce_data], 48)
df_CPI_PCE = df_CPI_PCE.rename(columns={'CPIAUCSL':'CPI'})
df_CPI_PCE['DATE'] = pd.to_datetime(df_CPI_PCE['DATE'])
df_CPI_PCE = df_CPI_PCE[df_CPI_PCE['DATE'] >= '2020-08-01']

# CPI vs PCE Correlation
corr_matrix_CPI_PCE = df_CPI_PCE.corr()
corr_CPI_PCE = corr_matrix_CPI_PCE.iloc[0][1]

# CPI vs PCE dataframe melted
df_CPI_PCE = df_CPI_PCE.melt(id_vars=['DATE'],var_name='INDEX')
# CPI vs PCE Graph

cpi_pce_line = alt.Chart(df_CPI_PCE).mark_line().encode(
    x=alt.X('DATE:T', title=None),
    y=alt.Y('value:Q', title=None),
    color=alt.Color('INDEX', title='') #legend=alt.Legend(legendX=10,legendY=2, 
)

cpi_pce_corr_text = alt.Chart({'values':[{}]}).mark_text(
    align='left', baseline='bottom'
).encode(
    x=alt.value(35), 
    y=alt.value(60), 
    text=alt.value([f"r: {corr_CPI_PCE:.3f}"]))

(cpi_pce_line+cpi_pce_corr_text).configure_legend(
    orient='top-left'
).properties(
    width=450, 
    height=225,
    title={'text':'Consumer Price Index vs Personal Consumption Expenditure',
           'subtitle':'A 2-Year Metric Comparison'})

st.markdown("""
### Inflation')

Causes of Inflation: https://news.stanford.edu/2022/09/06/what-causes-inflation/
""")
# inflation dataframe
df_INFL = get_combined_df([cpi_data], 48)
df_INFL = df_INFL.rename(columns={'CPIAUCSL':'CPI'})
df_INFL['DATE'] = pd.to_datetime(df_INFL['DATE'])
df_INFL = df_INFL[df_INFL['DATE'] >= '2018-08-01']

# Calculate 1 month and 12 month lags, for later inflation % calculations
df_INFL['lag_1_diff'] = df_INFL['CPI'].diff()
df_INFL['lag_12_diff'] = df_INFL['CPI'].diff(periods=12)
df_INFL['lag_1'] = df_INFL['CPI'] - df_INFL['lag_1_diff']
df_INFL['lag_12'] = df_INFL['CPI'] - df_INFL['lag_12_diff']

# Calculate inflation as % increase MoM and YoY
df_INFL['MoM_inflation_perc'] = (df_INFL['lag_1_diff'] / df_INFL['lag_1']) * 100
df_INFL['YoY_inflation_perc'] = (df_INFL['lag_12_diff'] / df_INFL['lag_12']) * 100
df_INFL = df_INFL[df_INFL['DATE'] >= '2019-08-01']
df_INFL[df_INFL['DATE']>='2021-08-01']
# Inflation graph
inflation_line = alt.Chart(df_INFL).mark_line().encode(
    x=alt.X('DATE:T', title=None),
    y=alt.Y('YoY_inflation_perc:Q', title=None, scale=alt.Scale(domain=[0, 10]))
)

# Inflation text
inflation_text = inflation_line.mark_text(align='center',fontSize=11,dy=-10).encode(
        text=alt.Text('YoY_inflation_perc:Q', format='.1f')) 

# Combine
(inflation_line+inflation_text).properties(
    width=900, 
    height=250,
    title={'text':'Inflation Causal Relationship Analysis',
           'fontSize':18}
)
# Inflation Inducing Events

# COVID

line_events = {'US COVID Emergency Declaration':'2020-02-03',
                   'Stimulus Round 1':'2020-04-01',
                   'Stimulus Round 2':'2020-12-01',
                   'Stimulus Round 3':'2021-03-01',
                   'US Quantitative Easing 4':'2020-03-01'
                  }

line_events_df = pd.DataFrame(line_events.items(), columns=['Event', 'Date'])

covid_lines = alt.Chart(line_events_df).mark_rule(color='gray', size=2).encode(
    x = 'Date:T')
line_events_df.sort_values('Date')
line_events_df['y1'] = 0
line_events_df['y2'] = 10
line_events_df['x2'] = ['2020-03-01','2020-04-01','2020-12-01','2021-03-01','2022-08-01']

covid_area = alt.Chart(line_events_df).mark_rect(fill='lightgray',opacity=0.3).encode(
    x='Date:T',
    x2='x2',
    y='y1',
    y2='y2',
)

st.markdown('### Personal Savings Rate & Revolving Credit')
# Savings dataframe
df_SAV = get_combined_df([savings_data], 48)
df_SAV = df_SAV.rename(columns={'PSAVERT':'Savings'})
df_SAV['DATE'] = pd.to_datetime(df_SAV['DATE'])
df_SAV['Savings_12M'] = df_SAV.rolling(window=12).mean()

df_SAV['Savings'] = df_SAV['Savings']/100
df_SAV['Savings_12M'] = df_SAV['Savings_12M']/100

df_SAV = df_SAV[df_SAV['DATE'] >= '2018-08-01']

savings_bar = alt.Chart(df_SAV).mark_bar().encode(
    x=alt.X('DATE:T', title=None, axis=alt.Axis(format="%b %Y")),
    y=alt.Y('Savings:Q', title=None, axis=alt.Axis(format='%'), scale=alt.Scale(domain=[0, .4]))
)

savings_12_line = alt.Chart(df_SAV).mark_line(color='#73e3eb').encode(
    x=alt.X('DATE:T', title=None),
    y=alt.Y('Savings_12M:Q', title=None)
)

savings_text = savings_bar.mark_text(
    align='left',
    baseline='middle',
    dy=-10,  # Nudges text to right so it doesn't appear on top of the bar
).encode(text=alt.Text('Savings:Q', format='0.0%'))

line_events_df.sort_values('Date')
line_events_df['y1'] = 0
line_events_df['y2'] = .4
line_events_df['x2'] = ['2020-03-01','2020-04-01','2020-12-01','2021-03-01','2022-08-01']

covid_area = alt.Chart(line_events_df).mark_rect(fill='lightgray',opacity=0.3).encode(
    x='Date:T',
    x2='x2',
    y='y1',
    y2='y2',
)

(savings_bar+savings_text+savings_12_line+covid_lines+covid_area).properties(
    width=800, 
    height=225,
    title={'text':'U.S. Personal Savings Rate & 12-Month Average', 'fontSize':14})
interest_data.head()
# Fed Fund Rate
df_INT = interest_data
df_INT['DATE'] = pd.to_datetime(df_INT['DATE'])
df_INT.reset_index(drop=True, inplace=True)
df_INT = df_INT[df_INT['DATE'] >= '2019-08-01']
df_INT = df_INT[df_INT['DATE'] <= '2022-08-01']

# Dataframe melted
df_INT = df_INT.melt(id_vars=['DATE'],var_name='INDEX')
df_INT.head()
interest_line = alt.Chart(df_INT).mark_line(color='green').encode(
    x=alt.X('DATE:T', title=None),
    y=alt.Y('value:Q', title=None, scale=alt.Scale(domain=[0, 10]))
)

interest_line
(inflation_line+inflation_text+interest_line).properties(
    width=900, 
    height=250,
    title={'text':'Inflation Causal Relationship Analysis',
           'fontSize':18}
)
# Russia-Ukraine war
war_line_events = {'Russia Ukraine War':'2022-02-24'}
war_line_events_df = pd.DataFrame(war_line_events.items(), columns=['Event', 'Date'])
war_lines = alt.Chart(war_line_events_df).mark_rule(color='red', size=2).encode(
    x = 'Date:T')
(inflation_line+inflation_text+interest_line+covid_lines+covid_area+war_lines).properties(
    width=900, 
    height=250,
    title={'text':'Inflation Causal Relationship Analysis',
           'fontSize':18}
)
