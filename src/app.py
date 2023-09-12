# import packages
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json
from copy import deepcopy
from pathlib import Path

# get rootpath
root = str(Path(__file__).parent.parent)

# load and cache data
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df 

# data on internet access
df_inet_raw = load_data(path = root + "/data/share-of-individuals-using-the-internet.csv")
df_inet = deepcopy(df_inet_raw)

# lets rename the columns
df_inet = df_inet.rename(columns={"Entity":"country", f"Individuals using the Internet (% of population)":"Percentage", "Year":"year"})

# clean based on country codes
df_inet.dropna(inplace=True)

# group by year
year_grp = df_inet.groupby(by=["year"])

# data on other quantities
df_gdppc = px.data.gapminder()

# geojson file
with open(root + "/data/countries.geojson", "r") as readfile:
    geojson_countries = json.load(readfile)


# title and header
st.title("Internet Across the World :earth_africa: :computer:")
st.write('<p style="font-family: Cambria"> \
         The map shows the percentage of the population of a country having internet access in a given year. \
          For some years additional information such as the GDP per capita is included and shown upon hovering over the country. \
          </p>', unsafe_allow_html=True)

# columns
left_column, right_column = st.columns([1, 1])

# choose a year for the dataset
years = sorted(pd.unique(df_inet['year']))

# selectbox
# year = left_column.selectbox("Year (takes some time to reload after changing)", years, index=20)

# slider
year = st.slider(label="Year (takes some time to reload after changing)", min_value=np.min(years), max_value=np.max(years), step=1, value=years[20])

# plot based on year
# the additional data only includes some years, so we will need to check if the year ends with a 2 or 7 and is less than or equal to 2007

# get internet data
data_year = year_grp.get_group(year)
# if there is data on the gdp we will take it and merge based on the country code, else we simply produce the base plot
if (year % 10 == 2 or year % 10 == 7) and (year <= 2007):

    # get data for GDP population and life exp
    data_new = df_gdppc[df_gdppc.year == year][["lifeExp", "pop", "gdpPercap", "iso_alpha"]]

    # rename columns for nice names
    data_new = data_new.rename(columns={"lifeExp":"Life Expectancy", "pop":"Population Size", "gdpPercap":"GDP per Capita", "iso_alpha":"Code"})

    # merge data
    data_year = pd.merge(data_year, data_new, on="Code", how="left")
    
    # replace Nan values
    data_year = data_year.fillna("data unavailable")

    # plot
    
    # use featureidkey to set the country name for location mapping (default is id) - the country code is listed under properties: {"ISO_A3" in the geojson file
    # the colorscale will interpolate between the given colors
    # the hoverdata will select which columns to display for the hoverbox and format values
    # the opacity allows to see names of countries and cities provided by the open streetmap style

    fig = px.choropleth_mapbox(data_year, geojson=geojson_countries, featureidkey="properties.ISO_A3", locations=data_year.Code, color=data_year.Percentage,
                                color_continuous_scale=["black", "red", "yellow", "green"], range_color=(0, 100), 
                                hover_name=data_year.country, hover_data={"Code":False, "country":False, "Percentage":":.1f", "Population Size":True, "GDP per Capita":True, "Life Expectancy":True}, opacity=0.5)

    # # change colorbar orientation and size - orientation does not work on the colorbar
    # fig.update_traces(colorbar=dict(orientation='h'))

    # another attempt - this works!
    # also change some other details
    fig.update_coloraxes(colorbar={"y":-0.1, "yanchor":"bottom", "len":0.95, "thickness":15, "orientation":'h', "title":{"text":"Percentage", "font":{"family":"Cambria"}}})

    # the style open street map will color the water and provide names of countries and cities upon zooming
    fig.update_layout(mapbox_style='open-street-map', mapbox_zoom=1, mapbox_center = {"lat": 45, "lon": 0}, height=700) 

    # set margins and bounds, such that the map is not repeated upon zooming out
    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, mapbox_bounds={"west":-168, "east":192, "north":85, "south":-58})

    # set title
    fig.update_layout(title={"text":f"Percentage of Population with Internet Access in each Country", "font":{"family":"Cambria"}, "xanchor":"left", "x":0., "yanchor":"middle", "y":0.98})

    # update hover text style
    fig.update_layout(hoverlabel={"bgcolor":"white", "font_size":12, "font_family":"Cambria"})

else:
    # plot

    # use featureidkey to set the country name for location mapping (default is id) - the country code is listed under properties: {"ISO_A3" in the geojson file
    # the colorscale will interpolate between the given colors
    # the hoverdata will select which columns to display for the hoverbox and format values
    # the opacity allows to see names of countries and cities provided by the open streetmap style

    fig = px.choropleth_mapbox(data_year, geojson=geojson_countries, featureidkey="properties.ISO_A3", locations=data_year.Code, color=data_year.Percentage,
                                color_continuous_scale=["black", "red", "yellow", "green"], range_color=(0, 100), 
                                hover_name=data_year.country, hover_data={"Code":False, "country":False, "Percentage":":.1f"}, opacity=0.5)

    # # change colorbar orientation and size - orientation does not work on the colorbar
    # fig.update_traces(colorbar=dict(orientation='h'))

    # another attempt - this works!
    # also change some other details
    fig.update_coloraxes(colorbar={"y":-0.1, "yanchor":"bottom", "len":0.95, "thickness":15, "orientation":'h', "title":{"text":"Percentage", "font":{"family":"Cambria"}}})

    # the style open street map will color the water and provide names of countries and cities upon zooming
    fig.update_layout(mapbox_style='open-street-map', mapbox_zoom=1, mapbox_center = {"lat": 45, "lon": 0}, height=700) 

    # set margins and bounds, such that the map is not repeated upon zooming out
    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, mapbox_bounds={"west":-168, "east":192, "north":85, "south":-58})

    # set title
    fig.update_layout(title={"text":f"Percentage of Population with Internet Access in each Country", "font":{"family":"Cambria"}, "xanchor":"left", "x":0., "yanchor":"middle", "y":0.98})

    # update hover text style
    fig.update_layout(hoverlabel={"bgcolor":"white", "font_size":12, "font_family":"Cambria"})

st.plotly_chart(fig)

# sources
url_internet = "https://data.worldbank.org/indicator/IT.NET.USER.ZS"
url_gapminder = "https://github.com/plotly/datasets/blob/master/gapminder-unclean.csv"
st.write(f'<p style="font-family: Cambria">Sources: <a href="{url_internet}">Internet access data</a>, <a href="{url_gapminder}">Other data</a></p>', unsafe_allow_html=True)  
# st.write("Geojson data for the map:")



