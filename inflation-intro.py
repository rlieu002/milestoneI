import pandas as pd
import altair as alt
import streamlit as st
print("The pandas version we used is {v}".format(v = pd.__version__))
print("The altair version we used is {v}".format(v = alt.__version__))

st.markdown("""
### Inflation and Its Components
##### SIADS 593 - Fall 2022

This notebook presents a systematic analysis of the components of inflation in the United States during the trailing 5 years.

### Import Data & Setup Environment
We prepare the environment by installing the visualization library we'll be using, [Altair](https://altair-viz.github.io), then importing Altair and a data manipulation library called [Pandas](https://pandas.pydata.org).

## Loading Data
We'll use data sourced from the St. Louis Federal Reserve of the United States of America (aka "FRED"). FRED publishes a variety of datasets related to inflation. For our analysis we've chosen to utilize the Consumer Price Index (CPI), a commonly-used method for tracking inflation.

The [Consumer Price Index](https://fred.stlouisfed.org/release/tables?rid=10&eid=34483) is a price index of a basket of goods and services paid by urban consumers. Percent changes in the price index measure the inflation rate between any two time periods. This particular index includes roughly 88 percent of the total population. 

In addition to the "All Up" total CPI figures provided by FRED, there are sub-component breakdowns available as well. The first level categorization that FRED breaks down CPI into includes: Food & Beverage, Housing, Apparel, Transport, Medical, Recreation, Education, and Other.

Using these sub-categories of inflation we're able to further analyze what particular components of the economy are driving consumer inflation at particular points. That will likely provide meaningful insight that helps us understand consumer behavior.
""")



# CPI All-Up

cpi_all = pd.read_csv('./data/CPIAUCSL.csv')


# CPI By category

cpi_foodbev = pd.read_csv('./data/CPIFABSL.csv')
cpi_housing = pd.read_csv('./data/CPIHOSSL.csv')
cpi_apparel = pd.read_csv('./data/CPIAPPSL.csv')
cpi_transport = pd.read_csv('./data/CPITRNSL.csv')
cpi_medical = pd.read_csv('./data/CPIMEDSL.csv')
cpi_recreation = pd.read_csv('./data/CPIRECSL.csv')
cpi_education = pd.read_csv('./data/CPIEDUSL.csv')
cpi_other = pd.read_csv('./data/CPIOGSSL.csv')

"""
Dataset of relevant events in US and World History


"""
relevant_events = {'US COVID Emergency Declaration':'2020-02-03',
                  'Stimulus Round 1':'2020-04-01',
                   'Stimulus Round 2':'2020-12-01',
                   'Stimulus Round 3':'2021-03-01',
                   'US Quantitative Easing 4':'2020-03-01'
                  }
relevant_events_df = pd.DataFrame(relevant_events.items(), columns=['Event', 'Date'])
st.dataframe(relevant_events_df)



"""
Inspect a bit of each dataframe as a sanity check
"""
st.dataframe(cpi_all.head())
#cpi_foodbev.head()
#cpi_housing.head()
#cpi_apparel.head()
#cpi_transport.head()
#cpi_medical.head()
#cpi_recreation.head()
#cpi_education.head()
#cpi_other.head()

st.markdown("""
Immediately we can see that we have datasets with the key indicator and a monthly cadence. In order to make this data more usable and relevant, we need to perform some transformations on it. In particular, we're going to utilize a common approach in government and industry, which is to create Month-Over-Month (MoM) and Year-Over-Year (YoY) metrics. With MoM metrics, we gain the ability to perform relative comparisons of adjacent periods. With YoY metrics we can compare a month with the same month of the prior year. This can be especially useful in eliminating seasonality effects like gas prices spikes in summer months due to travel habits.

To accomplish this task we will do the following:
* For each dataframe from FRED
* Add a "lag" column with the prior month's value
* Add a "12 month lag" column with the 12 month prior value
* Calculate MoM and YoY on a row-basis
""")


"""
Generate the MoM and YoY % figures that are commonly-used by the government and industry
"""
dfs = [cpi_all, cpi_foodbev, cpi_housing, cpi_apparel, cpi_transport, cpi_medical, cpi_recreation, cpi_education, cpi_other]

for df in dfs:
    # Get Col Name
    col = df.columns[1]
    # Calculate 1 month and 12 month lags, for later inflation % calculations
    df['lag_1_diff'] = df[col].diff()
    df['lag_12_diff'] = df[col].diff(12)
    # Calculate inflation as % increase MoM and YoY
    df['MoM Inflation %_{col}'.format(col=col)] = (df['lag_1_diff'] /df[col]) * 100
    df['YoY Inflation %_{col}'.format(col=col)] = (df['lag_12_diff'] / df[col]) * 100



st.dataframe(cpi_all.head(15)) # Quick spot check looks correct

st.markdown("""
Spot checking our results we can see that the MoM and YoY figures are accurate and populated as expected (i.e. no MoM for the first observation, no YoY for the first 11 observations). We've successfully engineered our first features on these datasets! Now let's put them to use...

### Basics on Inflation
We start by visualizing the all-up inflation YoY rates for the prior 60 months. This gives us an initiatl sense of how total inflation has been trending in the United States. We'll layer on top of that a few key events that can begin to help us understand what has been happening.
""")


all_chart_yoy = alt.Chart(cpi_all.tail(60), title = 'All Up Inflation (CPI)').mark_line(color = 'blue'
).encode(
        x = alt.X('DATE:T', axis = alt.Axis(title = 'Date', format = ("%b %Y"))),
        y = 'YoY Inflation %_CPIAUCSL',
        tooltip=['DATE:T', 'YoY Inflation %_CPIAUCSL']
).properties(width = 800, height = 400).interactive()

relevant_events_lines = alt.Chart(relevant_events_df).mark_rule(color = 'red', size = 2).encode(
    x = 'Date:T', tooltip = ['Event','Date:T']).interactive()

all_chart_yoy + relevant_events_lines

st.markdown("""
Now we're able to see that inflation has really picked up right around January of 2021. From a January 2021 reading of 1.34% YoY inflation we jump to 5% in May 2021. By May 2022 that figure was above 8% YoY! That sort of increase is painful for consumers. 

As we can see from the interactive chart's vertical lines, we have a number of factors that likely contribute to inflation.

* COVID 19 - The US declared a health emergency for COVID-19 in early February 2020. This shut down businesses and threatened the economy. The government and central bank then took actions which are believed to be tied to inflation.
* Quantitative Easing - According to [Wikipedia](https://en.wikipedia.org/wiki/Quantitative_easing) "Quantitative easing (QE) is a monetary policy action whereby a central bank purchases government bonds or other financial assets in order to inject monetary reserves into the economy to stimulate economic activity". We know that the US central bank did just that at the beginning of March 2020, in order to combat the negative economic effects of COVID-19. It's commonly believed that the inflationary effects of QE often lag the QE itself by 12 to 18 months (source [Investopedia](https://www.investopedia.com/terms/q/quantitative-easing.asp)). That seems to be exactly what happened in this case.
* Economic Stimulus for Consumers - The federal government also authorized 3 separate payments to citizens to help aleviate the economic impact of COVID. Each of these payments increased the amount of money in circulation in the economy, putting upward pressure on inflation.

Now let's dig into the details on what components of inflation were increasing most rapidly to get a more complete picture of price changes for consumers.
""")


"""
Join the sub-component dataframes, and rename the YoY values accordingly
"""
dfs = [cpi_foodbev, cpi_housing, cpi_apparel, cpi_transport, cpi_medical, cpi_recreation, cpi_education, cpi_other]


working_df = cpi_foodbev.iloc[:,[0,5]].tail(60).merge(cpi_housing.iloc[:,[0,5]].tail(60), on = 'DATE')
working_df = working_df.merge(cpi_apparel.iloc[:,[0,5]].tail(60), on = 'DATE')
working_df = working_df.merge(cpi_transport.iloc[:,[0,5]].tail(60), on = 'DATE')
working_df = working_df.merge(cpi_medical.iloc[:,[0,5]].tail(60), on = 'DATE')
working_df = working_df.merge(cpi_recreation.iloc[:,[0,5]].tail(60), on = 'DATE')
working_df = working_df.merge(cpi_education.iloc[:,[0,5]].tail(60), on = 'DATE')
working_df = working_df.merge(cpi_other.iloc[:,[0,5]].tail(60), on = 'DATE')


working_df = working_df.rename(columns={working_df.columns[1]: "Food Bev",
                           working_df.columns[2]: "Housing",
                           working_df.columns[3]: "Apparel",
                           working_df.columns[4]: "Transport",
                           working_df.columns[5]: "Medical",
                           working_df.columns[6]: "Recreation",
                           working_df.columns[7]: "Education",
                           working_df.columns[8]: "Other"
                          })


sub_components_df = working_df.melt(id_vars=['DATE'],var_name='Component')


subcomponent_chart_yoy = alt.Chart(sub_components_df, title = 'CPI Components YoY Inflation %').mark_line(
    color = 'blue'
    ).encode(x = alt.X('DATE:T', axis = alt.Axis(title = 'Date', format = ("%b %Y"))),
        y = 'value',
        color = 'Component',
        tooltip = ['Date:T','value','Component']
).properties(width = 800, height = 400).interactive()

subcomponent_chart_yoy

st.markdown("""
Now we can begin to see various different trends that contribute to the overall inflation behavior. Picking the most notable components:

* During the initial period of the COVID 19 pandemic, we see that Transportation and Apparel experienced dis-inflation. That isn't highly surprising, since the world was in "lock down". People were not traveling, and they were not leaving the home for the most part. In those circumstances we'd expect that transportation costs (e.g. fuel) and apparel costs (e.g. professional clothing) might experience downward price pressure as inventories grew and demand shrank.
* Once lockdowns started loosening, quantitative easing began to take effect, and stimulus checks were received, we notice a dramatic spike in Transportation inflation. This is likely due to pent-up demand as well as energy cost fluctuations. We also notice that Food and Beverage inflation is steadily growing in the post-2020 period and remains the second highest overall YoY inflation component.
* Although the trends are more muted, Housing and Apparel, and Medical inflation are growing and contributing to the overall upward trend in Inflation.
""")
