import streamlit as st
import pandas as pd
import altair as alt

# consumer price index (https://fred.stlouisfed.org/series/CPIAUCSL)
cpi_data = pd.read_csv('./data/CPIAUCSL.csv')
# personal consumption expenditures (https://fred.stlouisfed.org/series/PCE)
pce_data = pd.read_csv('./data/PCE.csv')
# personal saving rate (https://fred.stlouisfed.org/series/PSAVERT)
savings_data = pd.read_csv('./data/PSAVERT.csv')
# revolving consumer credit (https://fred.stlouisfed.org/series/REVOLSL)
credit_data = pd.read_csv('./data/REVOLSL.csv')
# unemployment rate (https://fred.stlouisfed.org/series/UNRATE)
unemployment_data = pd.read_csv('./data/UNRATE.csv')
# interest rate (https://www.federalreserve.gov/monetarypolicy/openmarket.htm)
interest_data = pd.read_csv('./data/INTEREST.csv')

def normalize_col(df, col_name):
    mean = df.mean().loc[col_name]  
    std = df.std().loc[col_name]
    df[col_name] = df[col_name].apply(lambda x: (x - mean) / std)

    return df

def get_combined_df(df_list, months):
    combined_df = None
    
    for df in df_list:
        start = df['DATE'].size - months
        df = df[start:]
        df = normalize_col(df, df.columns[1])
        print(df.head())
        
        combined_df = df if combined_df is None else combined_df.merge(df, on='DATE', how='outer')
        
    return combined_df

df_combined = get_combined_df([cpi_data, pce_data, savings_data, credit_data, unemployment_data], 60)
df_combined = df_combined.rename(columns={'CPIAUCSL':'CPI', 'PSAVERT':'Savings', 'REVOLSL':'Revolving Credit', 'UNRATE':'Unemployment'})
df_combined = df_combined.melt(id_vars=['DATE'],var_name='INDEX')

def get_indicator_chart():
    line = alt.Chart(df_combined).mark_line().encode(
        x='DATE',
        y='value',
        color='INDEX',
    )

    line_interest = alt.Chart(interest_data[2:]).mark_line(color='#000000').encode(
        x='DATE',
        y=alt.Y('INTEREST', title='value'),
    )

    point = alt.Chart(interest_data[2:]).mark_point(size=50).encode(
        x='DATE',
        y=alt.Y('INTEREST', title='value'),
    )

    chart = (line + line_interest + point).properties(
        width=800,
        title='Economic Indicators (Normalized, Except Interest)'
    )
    return chart

get_indicator_chart()