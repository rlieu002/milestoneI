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

# SAVINGS $: personal saving (https://apps.bea.gov/iTable/iTable.cfm?reqid=19&step=2#reqid=19&step=2&isuri=1&1921=survey)
savings_dollars_data = pd.read_csv('./data/PSAV.csv')

# REV CREDIT: revolving consumer credit (https://fred.stlouisfed.org/series/REVOLSL)
credit_data = pd.read_csv('./data/REVOLSL.csv')

# FED FUND RATE: interest rate (https://fred.stlouisfed.org/series/DFEDTARU)
interest_data = pd.read_csv('./data/DFEDTARU.csv')

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
st.dataframe(df_CPI_PCE.head())

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

cpi_vs_pce_chart = (cpi_pce_line+cpi_pce_corr_text).configure_legend(
    orient='top-left'
).properties(
    width=450, 
    height=225,
    title={'text':'Consumer Price Index vs Personal Consumption Expenditure',
           'subtitle':'A 2-Year Metric Comparison'})
cpi_vs_pce_chart

st.markdown("""
### Inflation

Causes of Inflation: https://news.stanford.edu/2022/09/06/what-causes-inflation/
""")

# Inflation dataframe
df_INFL = cpi_data
df_INFL = df_INFL.rename(columns={'CPIAUCSL':'CPI'})
df_INFL['DATE'] = pd.to_datetime(df_INFL['DATE'])
df_INFL = df_INFL[df_INFL['DATE'] >= '2017-08-01']

# Calculate 12 month lag for later inflation % calculations
df_INFL['lag_12_diff'] = df_INFL['CPI'].diff(periods=12)
df_INFL['lag_12'] = df_INFL['CPI'] - df_INFL['lag_12_diff']

# Calculate inflation as % increase YoY
df_INFL['YoY_inflation_perc'] = (df_INFL['lag_12_diff'] / df_INFL['lag_12']) * 100
df_INFL = df_INFL[df_INFL['DATE'] >= '2018-08-01']
st.dataframe(df_INFL)

# Inflation graph
inflation_line = alt.Chart(df_INFL).mark_line().encode(
    x=alt.X('DATE:T', title=None),
    y=alt.Y('YoY_inflation_perc:Q', title=None, scale=alt.Scale(domain=[0, 10]))
)

# Inflation text
inflation_text = inflation_line.mark_text(align='center',fontSize=11,dy=-10).encode(
        text=alt.Text('YoY_inflation_perc:Q', format='.1f')) 

# Fed Fund Rate
df_INT = interest_data
df_INT['DATE'] = pd.to_datetime(df_INT['DATE'])
df_INT.reset_index(drop=True, inplace=True)
df_INT = df_INT[df_INT['DATE'] >= '2018-08-01']
df_INT = df_INT[df_INT['DATE'] <= '2022-08-01']
df_INT = df_INT.melt(id_vars=['DATE'],var_name='INDEX')

interest_line = alt.Chart(df_INT).mark_line(color='green').encode(
    x=alt.X('DATE:T', title=None),
    y=alt.Y('value:Q', title=None, scale=alt.Scale(domain=[0, 10]))
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

# Russia-Ukraine war
war_line_events = {'Russia Ukraine War':'2022-02-24'}
war_line_events_df = pd.DataFrame(war_line_events.items(), columns=['Event', 'Date'])
war_lines = alt.Chart(war_line_events_df).mark_rule(color='red', size=2).encode(
    x = 'Date:T')

# Event annotations for Inflation
event_annotations = [['2020-02-05', 9, '1.a COVID Emergency Declaration'],
               ['2020-03-02', 8.25, '1.b COVID Stimulus 1'],
               ['2020-04-05', 7.5, '1.b COVID Stimulus 2'],
               ['2020-12-05', 7.25, '1.b COVID Stimulus 3'],
               ['2021-03-05', 6.5, '2. Quantitative Easing'],
               ['2021-04-05', 0.75, 'Federal Fund Rate ~ 0%'],
               ['2022-03-01', 4.5, '3. Rus-Ukr War']]

event_annotations_df = pd.DataFrame(event_annotations, columns=['date','count','note'])

event_annotations_text = alt.Chart(event_annotations_df).mark_line().encode(
    x=alt.X('date:T'),
    y=alt.Y('count:Q')
)

event_annotations_mark = event_annotations_text.mark_text(
    align='left',
    baseline='middle',
    fontSize=13,
    fontWeight=500,
).encode(text=alt.Text('note')).properties(width=400,height=275)

# Inflation Legend
leg_int = alt.Chart(pd.DataFrame({'y': [9], 'x': ['2018-9-01'], 'x2': ['2018-10-01']})
                ).mark_rule(color='#4c8fe0', strokeWidth=2.5).encode(y='y', x='x:T', x2='x2:T')

leg_fed = alt.Chart(pd.DataFrame({'y': [8.5], 'x': ['2018-9-01'], 'x2': ['2018-10-01']})
                ).mark_rule(color='green', strokeWidth=2.5).encode(y='y', x='x:T', x2='x2:T')

leg_covid = alt.Chart(pd.DataFrame({'y': [8.0], 'x': ['2018-9-01'], 'x2': ['2018-10-01']})
                ).mark_rule(color='grey', strokeWidth=2.5).encode(y='y', x='x:T', x2='x2:T')

leg_war = alt.Chart(pd.DataFrame({'y': [7.5], 'x': ['2018-9-01'], 'x2': ['2018-10-01']})
                ).mark_rule(color='red', strokeWidth=2.5).encode(y='y', x='x:T', x2='x2:T')


leg_annotations = [['2018-10-05', 9, 'Inflation'],
               ['2018-10-05', 8.5, 'Fed Fund Rate'],
               ['2018-10-05', 8.0, 'COVID'],
               ['2018-10-05', 7.5, 'Russian Ukraine War']]

leg_annotations_df = pd.DataFrame(leg_annotations, columns=['date','count','note'])

leg_lines_text = alt.Chart(leg_annotations_df).mark_line().encode(
    x=alt.X('date:T'),
    y=alt.Y('count:Q')
)

leg_lines_mark = leg_lines_text.mark_text(align='left',
    baseline='middle',
    fontSize=11,
    fontWeight=500,
).encode(text=alt.Text('note')).properties(width=400,height=275)

# Inflation final graph
inflation_chart = (inflation_line+inflation_text+interest_line+covid_lines+war_lines+covid_area+event_annotations_mark+leg_int+leg_fed+leg_covid+leg_war+leg_lines_mark).properties(
    width=900, 
    height=250,
)

inflation_chart

st.markdown('### Personal Savings Rate')
# Personal Savings dataframe
df_SAV = savings_data
df_SAV = df_SAV.rename(columns={'PSAVERT':'Savings'})
df_SAV['DATE'] = pd.to_datetime(df_SAV['DATE'])
df_SAV = df_SAV[df_SAV['DATE'] >= '2018-08-01']

# Personal Savings & Income dollar dataframe
df_SAV_DOL = savings_dollars_data
df_SAV_DOL['DATE'] = pd.to_datetime(savings_dollars_data['DATE'])
df_SAV_DOL['PSAV'] = df_SAV_DOL['PSAV'].astype(float)
df_SAV_DOL['PINC'] = df_SAV_DOL['PINC'].astype(float)
df_SAV_DOL = df_SAV_DOL.rename(columns={'PINC':'Personal Income (Billions)'})
df_SAV_DOL = df_SAV_DOL[df_SAV_DOL['DATE'] >= '2018-08-01']

# Personal Savings line
savings_line = alt.Chart(df_SAV).mark_line(color='#7332a8').encode(
    x=alt.X('DATE:T', title=None),
    y=alt.Y('Savings:Q', title=None, axis=None, scale=alt.Scale(domain=[0, 50]))
)

# Personal Savings text
savings_text = savings_line.mark_text(
    align='center',
    fontSize=11,
    dy=-10,
).encode(text=alt.Text('Savings:Q', format='.1f')) 

# Inflation graph 2
inflation_line_2 = alt.Chart(df_INFL).mark_line(color='#4c8fe0').encode(
    x=alt.X('DATE:T', title=None, axis=alt.Axis(format="%b %Y")),
    y=alt.Y('YoY_inflation_perc:Q', title=None, scale=alt.Scale(domain=[0, 50]), axis=None)
)

# Inflation text 2
inflation_text_2 = inflation_line_2.mark_text(
    align='center',
    fontSize=11,
    dy=-10,
).encode(text=alt.Text('YoY_inflation_perc:Q', format='.1f')) 

## LINES COMBINED
sav_infl_lines = (savings_line+savings_text+inflation_line_2+inflation_text_2).resolve_scale(y='shared')

# Personal Income bar
pers_inc_bar = alt.Chart(df_SAV_DOL).mark_bar(color='#7332a8', opacity=0.19).encode(
    x=alt.X('DATE:T', title=None),
    y=alt.Y('Personal Income (Billions):Q') 
)

pers_inc_annotations = [['2022-07-28', 22200, '$21.9T']]
pers_inc_annotations_df = pd.DataFrame(pers_inc_annotations, columns=['date','count','note'])

pers_inc_annotations_text = alt.Chart(pers_inc_annotations_df).mark_line().encode(
    x=alt.X('date:T'),
    y=alt.Y('count:Q', axis=None, scale=alt.Scale(domain=[17500, 25000]))
)

pers_inc_annotations_mark = pers_inc_annotations_text.mark_text(
    align='center',
    baseline='middle',
    fontSize=11, 
    fontWeight=700,
).encode(text=alt.Text('note'))

# Event annotations for Personal Savings
event_annotations_2 = [['2020-02-05', 24500, '1.a COVID Emergency Declaration'],
    ['2020-03-02', 24000, '1.b COVID Stimulus 1'],
    ['2020-04-05', 23500, '1.b COVID Stimulus 2'],
    ['2020-12-05', 23000, '1.b COVID Stimulus 3'],
    ['2021-03-05', 22500, '2. Quantitative Easing']]

event_annotations_df_2 = pd.DataFrame(event_annotations_2, columns=['date','count','note'])

event_annotations_text_2 = alt.Chart(event_annotations_df_2).mark_line().encode(
    x=alt.X('date:T'),
    y=alt.Y('count:Q', axis=None, scale=alt.Scale(domain=[17500, 25000]))
)

event_annotations_mark_2 = event_annotations_text_2.mark_text(
    align='left',
    baseline='middle',
    fontSize=12,
    fontWeight=500,
).encode(text=alt.Text('note'))

# Personal Savings Legend
leg_int_2 = alt.Chart(pd.DataFrame({
    'y': [24500],
    'x': ['2018-9-01'],
    'x2': ['2018-10-01'],
})).mark_rule(color='#4c8fe0', strokeWidth=2.5).encode(y=alt.Y('y', axis=None), x='x:T', x2='x2:T')

leg_covid_2 = alt.Chart(pd.DataFrame({
    'y': [24000],
    'x': ['2018-9-01'],
    'x2': ['2018-10-01'],
})).mark_rule(color='grey', strokeWidth=2.5).encode(y=alt.Y('y', axis=None), x='x:T', x2='x2:T')

leg_per_sav_2 = alt.Chart(pd.DataFrame({
    'y': [23500],
    'x': ['2018-9-01'],
    'x2': ['2018-10-01'],
})).mark_rule(color='#7332a8', strokeWidth=2.5).encode(y=alt.Y('y', axis=None), x='x:T', x2='x2:T')

leg_per_inc_2 = alt.Chart(pd.DataFrame({
    'y': [23000],
    'x': ['2018-9-01'],
    'x2': ['2018-10-01'],
})).mark_rule(color='#ae8dc9', strokeWidth=2.5).encode(y=alt.Y('y', axis=None), x='x:T', x2='x2:T')


leg_annotations_2 = [['2018-10-05', 24500, 'Inflation'],
    ['2018-10-05', 24000, 'COVID'],
    ['2018-10-05', 23500, 'Personal Savings Rate'],
    ['2018-10-05', 23000, 'Personal Income ($ Billions)']]

leg_annotations_df_2 = pd.DataFrame(leg_annotations_2, columns=['date','count','note'])

leg_lines_text_2 = alt.Chart(leg_annotations_df_2).mark_line().encode(
    x=alt.X('date:T'),
    y=alt.Y('count:Q', axis=None)
)

leg_lines_mark_2 = leg_lines_text_2.mark_text(
    align='left',
    baseline='middle',
    fontSize=11,
    fontWeight=500,
).encode(text=alt.Text('note'))

# Personal Savings final graph
per_savings = (sav_infl_lines+pers_inc_bar).resolve_scale(y='independent')
per_savings_final = (event_annotations_mark_2+per_savings+covid_lines+pers_inc_annotations_mark
    +leg_int_2+leg_covid_2+leg_per_sav_2+leg_per_inc_2+leg_lines_mark_2
).properties(width=925, height=250)

per_savings_final

st.markdown('### Revolving Credit')
# Revolving Credit
df_REV = credit_data
df_REV = df_REV.rename(columns={'REVOLSL':'RevCredit'})
df_REV['DATE'] = pd.to_datetime(df_REV['DATE'])
df_REV = df_REV[df_REV['DATE'] >= '2018-08-01']

# Revolving Credit line
rev_credit_bar = alt.Chart(df_REV).mark_bar(color='red', opacity=0.4).encode(
    x=alt.X('DATE:T', title=None, axis=alt.Axis(format="%b %Y")),
    y=alt.Y('RevCredit:Q',title='Revolving Credit (Billions)')
)

# Rev credit text
rev_credit_text = rev_credit_bar.mark_text(
    align='center',
    fontSize=11,
    dy=-10,
).encode(text=alt.Text('RevCredit:Q')) 

# Inflation graph 3
inflation_line_3 = alt.Chart(df_INFL).mark_line(color='#4c8fe0').encode(
    x=alt.X('DATE:T', title=None, axis=alt.Axis(format="%b %Y")),
    y=alt.Y('YoY_inflation_perc:Q', title=None, axis=None, scale=alt.Scale(domain=[0, 11]))
)

# Inflation text 3
inflation_text_3 = inflation_line_3.mark_text(
    align='center',
    fontSize=11,
    dy=-10,
).encode(text=alt.Text('YoY_inflation_perc:Q', format='.1f')) 

inflation_3 = inflation_line_3+inflation_text_3

## PLOTS COMBINED
rev_credit_infl_bar = alt.layer(rev_credit_bar, inflation_3).resolve_scale(y='independent')

# Event annotations for Revolving Credit
event_annotations_3 = [['2020-02-05', 1370, '1.a COVID Emergency Declaration'],
    ['2020-03-02', 1340, '1.b COVID Stimulus 1'],
    ['2020-04-05', 1310, '1.b COVID Stimulus 2'],
    ['2020-12-05', 1270, '1.b COVID Stimulus 3'],
    ['2021-03-05', 1240, '2. Quantitative Easing']]

event_annotations_df_3 = pd.DataFrame(event_annotations_3, columns=['date','count','note'])

event_annotations_text_3 = alt.Chart(event_annotations_df_3).mark_line().encode(
    x=alt.X('date:T'),
    y=alt.Y('count:Q', axis=None, scale=alt.Scale(domain=[900, 1400])),
)

event_annotations_mark_3 = event_annotations_text_3.mark_text(
    align='left',
    baseline='middle',
    fontSize=12,
    fontWeight=500,
).encode(text=alt.Text('note'))

# Revolving Credit annotation
rev_credit_annotations = [['2022-07-28', 1170, '$1.15T'], ['2021-01-01', 1013, '$0.97T']]
rev_credit_annotations_df = pd.DataFrame(rev_credit_annotations, columns=['date','count','note'])

rev_credit_annotations_text = alt.Chart(rev_credit_annotations_df).mark_line().encode(
    x=alt.X('date:T'),
    y=alt.Y('count:Q', axis=None, scale=alt.Scale(domain=[900, 1400])),
)

rev_credit_annotations_mark = rev_credit_annotations_text.mark_text(
    align='center',
    baseline='middle',
    fontSize=11, 
    fontWeight=700,
).encode(text=alt.Text('note'))

# Revolving Credit Legend
leg_int_3 = alt.Chart(pd.DataFrame({
    'y': [1350],
    'x': ['2018-9-01'],
    'x2': ['2018-10-01'],
})).mark_rule(color='#4c8fe0', strokeWidth=2.5).encode(y=alt.Y('y', axis=None), x='x:T', x2='x2:T')

leg_covid_3 = alt.Chart(pd.DataFrame({
    'y': [1320],
    'x': ['2018-9-01'],
    'x2': ['2018-10-01'],
})).mark_rule(color='grey', strokeWidth=2.5).encode(y=alt.Y('y', axis=None), x='x:T', x2='x2:T')

leg_rev_cred_3 = alt.Chart(pd.DataFrame({
    'y': [1290],
    'x': ['2018-9-01'],
    'x2': ['2018-10-01'],
})).mark_rule(color='red', strokeWidth=2.5).encode(y=alt.Y('y', axis=None), x='x:T', x2='x2:T')

leg_annotations_3 = [['2018-10-05', 1350, 'Inflation'],
    ['2018-10-05', 1320, 'COVID'],
    ['2018-10-05', 1290, 'Revolving Credit ($ Billions)']]

leg_annotations_df_3 = pd.DataFrame(leg_annotations_3, columns=['date','count','note'])

leg_lines_text_3 = alt.Chart(leg_annotations_df_3).mark_line().encode(
    x=alt.X('date:T'),
    y=alt.Y('count:Q', axis=None)
)

leg_lines_mark_3 = leg_lines_text_3.mark_text(
    align='left',
    baseline='middle',
    fontSize=11,
    fontWeight=500,
).encode(text=alt.Text('note'))

# Revolving Credit final graph
rev_credit_final = (rev_credit_annotations_mark+covid_lines+event_annotations_mark_3+rev_credit_infl_bar+leg_int_3+leg_covid_3+leg_rev_cred_3+leg_lines_mark_3).properties(
    width=925,
    height=250,
)

rev_credit_final
