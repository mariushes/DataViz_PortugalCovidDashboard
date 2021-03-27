# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import datetime
from datetime import date

from dash.dependencies import Input, Output


import json

import pandas as pd
import plotly.graph_objs as go

import numpy as np


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df_concelhos = pd.read_csv("Data/new_infections_concelhos.csv")
dates = df_concelhos.iloc[:,0].tolist()
df_concelhos = df_concelhos.set_index("data")


app.layout = html.Div([
    dcc.Graph(id='graph-with-slider'),
    dcc.DatePickerSingle(
        id='date-picker-single',
        min_date_allowed=date.fromisoformat(dates[0]),
        max_date_allowed=date.fromisoformat(dates[-1]),
        initial_visible_month=date.fromisoformat(dates[-1]),
        date=date.fromisoformat(dates[-1])
    )
])

@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('date-picker-single', 'date'))
def create_choropleth(selected_date):
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
            if date.fromisoformat(selected_date) <= date.fromisoformat(x):
                selected_date = x
                break


    # update all the continente data with the values from df_concelhos
    for i in continente_data.index.tolist():
        concelho = continente_data.iloc[i,1]
        continente_data.iloc[i,2] = df_concelhos.loc[selected_date,concelho.lower()]




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
    fig.add_choropleth(geojson=continente, locations=continente_data.id,
                       z=continente_data.value,
                       colorscale="teal",
                       zmin=0,
                       zmax=100,
                       hovertext=continente_data.concelho,
                       hoverinfo="text",
                       colorbar=dict(title={'text': '',
                                            'font': {  # 'size':24,
                                                'family': 'Arial',
                                                'color': palette['text']},
                                            'side': 'right'},
                                     tickfont={  # 'size' : 20,
                                         'color': palette['bartext']},
                                     # ticks='outside',
                                     # len=0.1,
                                     # x=0.1
                                     ),
                       marker=dict(line=dict(width=1))
                       )
    fig.update_geos(fitbounds="locations", bgcolor='rgba(0,0,0,0)', visible=False)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)