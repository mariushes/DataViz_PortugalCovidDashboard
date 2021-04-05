# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate
#from flask_caching import Cache
#import os
#import datetime
#import time
from dash.dependencies import Input, Output, State
import json
import pandas as pd
import plotly.graph_objs as go
import numpy as np
#import statistics

from helper_functions import color_interval, date_range

# Style
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
palette = {'cutoff': 'rgba(227, 78, 38, 1)',
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

# Seting up application
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Data Generation and load #################################
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
date_list = ('date1', 'date2', 'date3')
region_list = []

for region in (continente, madeira, azores):
    np.random.seed(len(region['features']))
    ids = []
    names = []
    values = []
    dates = []
    latitudes = []
    longitudes = []
    risks = []

    for date in date_list:
        ids += [i['properties']['CCA_2'] for i in region['features']]
        names += [i['properties']['concelho'] for i in region['features']]
        values += [int(100 * np.random.random()) for i in range(len(region['features']))]
        dates += [date for i in range(len(region['features']))]
        latitudes += [i['properties']['lat'] for i in region['features']]
        longitudes += [i['properties']['lon'] for i in region['features']]
        risks += [np.random.choice([1, 2, 3]) for i in range(len(region['features']))]

    data = pd.DataFrame([ids, names, values, dates, latitudes, longitudes, risks]) \
        .T.rename(columns={0: 'id',
                           1: 'concelho',
                           2: 'value',
                           3: 'date',
                           4: 'lat',
                           5: 'lon',
                           6: 'risk'})
    data['value'] = data['value'].astype(int)
    region_list.append(data)

continente_data, madeira_data, azores_data = region_list


def create_map_fig(date,
                   region: "continente/madeira/azores" = 'continente',
                   ):
    # Selection of the map##
    if region == 'continente':
        data_all_dates = continente_data.copy()
        geo = continente
    elif region == 'madeira':
        data_all_dates = madeira_data.copy()
        geo = madeira
    elif region == 'azores':
        data_all_dates = azores_data.copy()
        geo = azores
    fig = go.Figure()
    # Filtering the date
    data = data_all_dates[data_all_dates.date == date]
    data_locked = data[data.risk == 3]
    ## Choropleth map ######
    fig.add_choropleth(
        geojson=geo, locations=data.id,
        z=data.value,
        colorscale="teal",
        zmin=0,
        zmax=100,
        hovertext=data.concelho,
        hoverinfo="text",
        colorbar=dict(title={'text': '',
                             'font': {  # 'size':24,
                                 'family': 'Arial',
                                 'color': palette['text']},
                             'side': 'right'},
                      tickfont={'size': 20,
                                'color': palette['bartext']},
                      # ticks='outside',
                      len=0.8,
                      # x=0.1
                      ),
        marker=dict(line=dict(width=1)),
        # visible=False
    )

    ## Risk borders ######
    fig.add_trace(
        go.Choropleth(
            geojson=geo, locations=data_locked.id,
            z=[0 for i in range(len(data_locked))],
            colorscale=[[0, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,0)']],  # transparent
            colorbar=dict(tickvals=[],
                          ticktext=[]),
            name='',
            marker=dict(line=dict(width=1.5,
                                  color='red')),
            hoverlabel={'bgcolor':'red'},
            hovertemplate='(closed)',
            hoverinfo="text"
            # visible=False
        )
    )

    ##### Risks markers #####
    fig.add_trace(
        go.Scattergeo(
            lat=data_locked.lat.values,
            lon=data_locked.lon.values,
            mode='markers',
            name='',
            marker=dict(size=0.1,
                        #color='rgba(0,0,0,0)',
                        color='red',
                        line={"width": 0},
                        # symbol='x',
                        ),
            hovertemplate=data_locked.concelho,
            hoverinfo="text",
            showlegend=False,
            # visible=False
        )
    )

    fig.update_geos(fitbounds="geojson", bgcolor='rgba(0,0,0,0)', visible=False, projection={})
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      # autosize=False,
                      # legend=dict(yanchor="bottom",
                      #            y=0.09,
                      #            xanchor="left",
                      #            x=0.2,
                      #            #orientation='h'
                      #            font = {'size' : 22,
                      #                    'color': palette['legendtext']}
                      #           ),
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)',
                      )
    # fig.update_layout(uirevision=False)
    return fig


# Make lists of figures (1 list for 1 div block)
figs_continente = [create_map_fig(date, region='continente') for date in date_list]
# figs_madeira = [create_map_fig(date, region='madeira') for date in date_list]
# figs_azores = [create_map_fig(date, region='azores') for date in date_list]

# Make lists of dccs (1 list for 1 div block)
slider = dcc.Slider(
        id='date_slider',
        min=0,
        max=len(date_list) - 1,
        value=0,
        marks=dict(zip(range(len(date_list)), date_list))
    )
#print(slider.value)
block_continente = html.Div(
     [html.Button('Reset', id='reset', n_clicks=0)] + \
     [dcc.Graph(id='graph_continente_{}'.format(i),
                figure=figs_continente[i],
                config={'displayModeBar': False}
               ) for i in range(len(figs_continente))] + \
     [slider]
)

# container layout and elements
app.layout = html.Div([
                      block_continente,
                      ],
    id="layout",
    style={'float': 'left',
            'width' : "100%"}
)

# Date Slider callback
@app.callback(
    [Output('graph_continente_{}'.format(i), 'style') for i in range(len(date_list))],
    Input('date_slider', 'value'))
def slider_callback(selected_step):
    outputs = [{'display': 'none'} for i in range(3)]
    outputs[selected_step] = {'display': 'grid'}
    return outputs

# Zoom synchronization callbacks
@app.callback([Output('graph_continente_{}'.format(i), 'figure') for i in range(len(date_list))],
              [Input('graph_continente_{}'.format(i), 'relayoutData') for i in range(len(date_list))]+ \
              [Input('date_slider', 'value')] + \
              [Input('reset', 'n_clicks')],
              [State('graph_continente_{}'.format(i), 'figure') for i in range(len(date_list))] +\
              [State('date_slider', 'value')]
              )

def zoom_event(*params):
    num_inputs = int(len(params) / 2) - 1
    relayout_data = params[:num_inputs]
    figures = params[num_inputs+2:-1]
    signature = params[-1]
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    #print("changed_id: ", changed_id)
    outputs = []
    for fig in figures:
        try:
            fig["layout"]["geo"]["projection"] = {'rotation.lon': relayout_data[signature]['geo.projection.rotation.lon'],
                                                  'scale': relayout_data[signature]['geo.projection.scale']}
            fig["layout"]["geo"]["center"] = {'lon': relayout_data[signature]['geo.center.lon'],
                                              'lat': relayout_data[signature]['geo.center.lat']}
            fig["layout"]["geo"]["fitbounds"] = False
            print('success on rezoom')
            print(relayout_data[signature]['geo.projection.rotation.lon'])
            print('scale', relayout_data[signature]['geo.projection.scale'])
        except (KeyError, TypeError, IndexError):
            #print('fail on rezoom')
            #raise PreventUpdate
            pass
        if changed_id=='reset.n_clicks':
            #print('success on reset')
            fig["layout"]["geo"]["fitbounds"] = 'geojson'
        outputs.append(fig)
    return outputs

if __name__ == '__main__':
    app.run_server(debug=True)

