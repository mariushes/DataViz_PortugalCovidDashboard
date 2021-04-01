# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import datetime
import time
from dash.dependencies import Input, Output
import json
import pandas as pd
import plotly.graph_objs as go
import numpy as np

import statistics

from helper_functions import color_interval, date_range

def unixToDatetime(unix):
    ''' Convert unix timestamp to datetime. '''
    return pd.to_datetime(unix,unit='s')

def getMarks(start, end, Nth=1):
    ''' Returns the marks for labeling. 
        Every Nth value will be used.
    '''
    daterange = pd.date_range(start,end)
    result = {}
    for i, date in enumerate(daterange):
        if(i%Nth == 1):
            # Append value to dict
            result[unixTimeMillis(date)] = str(date.strftime('%Y-%m-%d'))

    return result

#style
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#Data load
df_new_concelhos = pd.read_csv("Data/new_infections_concelhos.csv")
dates = df_new_concelhos.iloc[:,0].tolist()
dates_timestamp = [datetime.datetime.strptime(date,'%Y-%m-%d').timestamp() for date in dates]
df_new_concelhos = df_new_concelhos.set_index("data")

df_new_per100k_concelhos = pd.read_csv("Data/new_infections_per100k_concelhos.csv")
df_new_per100k_concelhos = df_new_per100k_concelhos.set_index("data")

df_cumulative_per100k_concelhos = pd.read_csv("Data/cumulative_per100k_concelhos.csv")
df_cumulative_per100k_concelhos = df_cumulative_per100k_concelhos.set_index("data")

df_cumulative_concelhos = pd.read_csv("Data/cumulative_concelhos.csv")
df_cumulative_concelhos = df_cumulative_concelhos.set_index("data")


portugal_new_infections_7average_data= pd.read_csv("./Data/time_series_covid19_confirmed_new_infections_7average_portugal.csv")
portugal_new_infections_7average_data = portugal_new_infections_7average_data.drop(labels=["Province/State","Country/Region","Lat","Long"], axis=1)
portugal_new_infections_7average_data = portugal_new_infections_7average_data[date_range(dates[0],dates[-1])]

radios_div = html.Div([
            dcc.RadioItems(
                id='cumulative-radio',
                options=[{'label': i, 'value': i} for i in ['New Infections', 'Cumulative']],
                value='New Infections',
                labelStyle={'display': 'inline-block'}
            ),
            dcc.RadioItems(
                id='absolute-radio',
                options=[{'label': i, 'value': i} for i in ['Per 100k Inhabitants', 'Absolute']],
                value='Per 100k Inhabitants',
                labelStyle={'display': 'inline-block'}
            )
        ])

date_picker = dcc.DatePickerSingle(
        id='date-picker-single',
        min_date_allowed=datetime.date.fromisoformat(dates[0]),
        max_date_allowed=datetime.date.fromisoformat(dates[-1]),
        initial_visible_month=datetime.date.fromisoformat(dates[-1]),
        date=datetime.date.fromisoformat(dates[-1])
    ) 
slider_div = html.Div([
dcc.Graph(id='slider-timeline'),
dcc.Slider(
        id='year_slider',
        min = min(dates_timestamp),
        max = max(dates_timestamp),
        value = min(dates_timestamp),
        marks = getMarks(unixToDatetime(min(dates_timestamp)), unixToDatetime(max(dates_timestamp))),
    )


])
#container layout and elements
app.layout = html.Div([
    radios_div,
    dcc.Graph(id='graph-with-slider'),
    date_picker,
    slider_div,
    html.P(id='placeholder')
])

#Date Slider callback
@app.callback(
    Output('date-picker-single', 'date'),
    Input('year_slider', 'value'))
def slider_callback(selected_date):
    selected_date_str = str(unixToDatetime(selected_date).date())
    return datetime.date.fromisoformat(selected_date_str)


#callback after date picker interaction
@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('date-picker-single', 'date'),
    Input('absolute-radio', 'value'),
    Input('cumulative-radio', 'value')
)
def create_choropleth_callback(selected_date, absolute, cumulative):
    return create_choropleth(selected_date, absolute, cumulative)

@app.callback(
    Output('slider-timeline', 'figure'),
    Input('date-picker-single', 'date')
)
def create_slider_timeline_callback(slider_date):
    return create_slider_timeline(slider_date)

def create_choropleth(selected_date, absolute, cumulative):
    if absolute == "Absolute" and cumulative == 'New Infections':
        df = df_new_concelhos
        quantiles = []
        for column in df.columns:
            quantiles.append(df[column].quantile(0.95))
        max = np.max(quantiles)
    elif absolute == "Per 100k Inhabitants" and cumulative == 'New Infections':
        df = df_new_per100k_concelhos
        # compute max value for map choropleth
        quantiles = []
        for column in df.columns:
            quantiles.append(df[column].quantile(0.95))
        max = statistics.mean(quantiles)
    elif absolute == "Per 100k Inhabitants" and cumulative == 'Cumulative':
        df = df_cumulative_per100k_concelhos
        max = df.to_numpy().max()
    elif absolute == "Absolute" and cumulative == 'Cumulative':
        df = df_cumulative_concelhos
        max = df.to_numpy().max()

    with open('geojson/continente.geojson', encoding='utf-8') as file:
        continente = json.loads(file.read())

    with open('geojson/madeira.geojson', encoding='utf-8') as file:
        madeira = json.loads(file.read())

    with open('geojson/azores.geojson', encoding='utf-8') as file:
        azores = json.loads(file.read())

    # add IDs to regions (features)
    for feature in continente["features"]:
        feature['id'] = feature['properties']['CCA_2']
    for feature in madeira["features"]:
        feature['id'] = feature['properties']['CCA_2']
    for feature in azores["features"]:
        feature['id'] = feature['properties']['CCA_2']


    # generate data
    data_list = []

    for region in (continente, madeira, azores):
        np.random.seed(len(region['features']))
        ids = [i['properties']['CCA_2'] for i in region['features']]
        names = [i['properties']['concelho'] for i in region['features']]
        values = [int(100 * np.random.random()) for i in range(len(region['features']))]
        data = pd.DataFrame([ids, names, values]).T.rename(columns={0: 'id', 1: 'concelho', 2: 'value'})
        data['value'] = data['value'].astype(int)
        data_list.append(data)

    continente_data, madeira_data, azores_data = data_list

    # if the selected date is not in the available dates choose the next higher date.
    if selected_date not in dates:
        for x in dates:
            if datetime.date.fromisoformat(selected_date) <= datetime.date.fromisoformat(x):
                selected_date = x
                break


    # update all the continente data with the values from df_concelhos
    for i in continente_data.index.tolist():
        concelho = continente_data.iloc[i,1]
        continente_data.iloc[i,2] = df.loc[selected_date,concelho.lower()]




    palette = {'cutoff': 'rgba(227, 78, 38, 1)',
               'wave1': 'rgba(247, 141, 31, 0.7)',
               'wave2': 'rgba(227, 78, 38, 1)',
               'scale0': 'rgba(172, 185, 54, 0)',
               'scale1': 'rgba(0, 120, 128, 1)',
               'scale2': 'rgba(0, 102, 102, 1)',
               'scale3': 'rgba(0, 70, 70, 1)',
               'borders': 'rgba(0, 0, 0, 1)',
               'text': 'rgba(114, 114, 114, 1)',
               'legendtext': 'black',
               'bartext': 'black',
               'bartitletext': 'black',
               'bubbletext': 'black'
               }

    # %%
    fig = go.Figure()

    ## Choropleth map ######
    fig.add_choropleth(
        geojson=continente, 
        locations=continente_data.id,
        z=continente_data.value,
        colorscale="teal",
        zmin=0,
        zmax=max,
        hovertext=continente_data.concelho,
        hoverinfo="text",
        colorbar=dict(
            title={
                'text': '',
                'font': {  
                    'family': 'Arial',
                    'color': palette['text']
                },
                'side': 'right'
            },
            tickfont={  
                'color': palette['bartext']
            }
        ),
        marker=dict(line=dict(width=1))
    )
    fig.update_geos(fitbounds="locations", bgcolor='rgba(0,0,0,0)', visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=700)
    return fig

def create_slider_timeline(slider_date):
    portugal_new_infections_7average_data_color = portugal_new_infections_7average_data.copy()
    portugal_new_infections_7average_data_color["color"] = ["green"]
    color_interval(portugal_new_infections_7average_data_color, "2020-10-27", "2020-11-27", "yellow")
    color_interval(portugal_new_infections_7average_data_color, "2021-01-15", "2021-02-28", "red")

    color_text = {
        "yellow":"Regional Lockdown",
        "green": "No Lockdown",
        "red": "Full Lockdown"
    }

    data = []
    for i in range(len(portugal_new_infections_7average_data_color.values.tolist())):
        row = portugal_new_infections_7average_data_color.values.tolist()[i]
        name = ""
        color = row.pop(len(row) - 1)
        data.append(dict(type='scatter',
                         y=row,
                         x=portugal_new_infections_7average_data.columns,
                         name="",
                         text = color_text[color],
                         hoverinfo="text",
                         fill='tozeroy',
                         line=dict(color=color)
                         ))

    layout = dict(title=dict(text=''),
                  xaxis={
                      'showgrid': False,  # thin lines in the background
                      'zeroline': False,  # thick line at x=0
                      'visible': False,  # numbers below
                  },
                  yaxis= {
                        'showgrid': False, # thin lines in the background
                        'zeroline': False, # thick line at x=0
                        'visible': False,  # numbers below
                        },
                  width=1400,
                  height=200,
                  showlegend=False,
                  margin=dict(l=30, r=0, t=20, b=0),
                  paper_bgcolor='rgba(0,0,0,0)',
                  plot_bgcolor='rgba(0,0,0,0)'
                  )
    figure = go.Figure(data=data,
                       layout=layout)
    figure.add_vline(x=slider_date)
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)