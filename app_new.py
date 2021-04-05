# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

##### Imports
import dash
import dash_core_components as dcc
import dash_html_components as html
import datetime
from time import time
import json
import pandas as pd
import plotly.graph_objs as go
import numpy as np
import statistics
from dash.dependencies import Input, Output
from helper_functions import color_interval, date_range
from enum import Enum

####

palette = {
    'background' : 'rgba(20, 20, 50, 1)',
    'block' : 'rgba(50, 50, 50, 1)',
    'borders': 'rgba(0, 0, 0, 1)',
    'text': 'rgba(114, 114, 114, 1)',
    'legendtext': 'black',
    'bartext': 'black',
}

##### Auxiliary functions
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
            result[time.unixTimeMillis(date)] = str(date.strftime('%Y-%m-%d'))

    return result

##### Dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

##### DATA LOAD

#df_new_concelhos
df_new_concelhos = pd.read_csv("Data/new_infections_concelhos.csv")
dates = df_new_concelhos.iloc[:,0].tolist()
dates_timestamp = [datetime.datetime.strptime(date,'%Y-%m-%d').timestamp() for date in dates]
df_new_concelhos = df_new_concelhos.set_index("data")

#df_new_per100k_concelhos
df_new_per100k_concelhos = pd.read_csv("Data/new_infections_per100k_concelhos.csv")
df_new_per100k_concelhos = df_new_per100k_concelhos.set_index("data")

#df_cumulative_per100k_concelhos
df_cumulative_per100k_concelhos = pd.read_csv("Data/cumulative_per100k_concelhos.csv")
df_cumulative_per100k_concelhos = df_cumulative_per100k_concelhos.set_index("data")

#df_cumulative_concelhos
df_cumulative_concelhos = pd.read_csv("Data/cumulative_concelhos.csv")
df_cumulative_concelhos = df_cumulative_concelhos.set_index("data")

#portugal_new_infections_7average_data
portugal_new_infections_7average_data= pd.read_csv("./Data/time_series_covid19_confirmed_new_infections_7average_portugal.csv")
portugal_new_infections_7average_data = portugal_new_infections_7average_data.drop(labels=["Province/State","Country/Region","Lat","Long"], axis=1)
portugal_new_infections_7average_data = portugal_new_infections_7average_data[date_range(dates[0],dates[-1])]



### Components
# Slider-Timeline
slider_div = html.Div([html.H4('Slider div', style={"color":'white'})],
                      style={
                         "display": "grid",
                          "background-color": "#222222"

                           }
)

##### COMPONENTS
# Title
title_div = html.Div([
                      html.H4('Progression of coronavirus in Portugal',
                              style={"color":'red',
                                     "font-size": 20,
                                     "font-weight" : 'bold'
                              }),
                      html.P('Filipe Coelho, m20200580', style={"color":'white'}),
                      html.P('Ivan Kisialiou, m20200998', style={"color":'white'}),
                      html.P('José Quintas, m20200673', style={"color":'white'}),
                      html.P('Marius Hessenthaler, e20201824', style={"color":'white'})
                     ],
                     style={
                          "font-size": 12,
                          "display": "grid",
                          "padding" : "1% 1% 1% 1%",
                          "box-sizing": "border-box",
                          #"height" : "20vh"
                           }
)

#Radio Buttons
radios_div = \
    html.Div([
        dcc.RadioItems(
            id='cumulative-radio',
            options=[{'label': i, 'value': i} for i in ['Cumulative', 'New Cases']],
            value='Cumulative',
            labelStyle={'display': 'block'},
            style={"color" : "white",
                   "background-color":palette["block"],
                   "font-size" : 16,
                   "padding-top":"13%"}
        ),
        dcc.RadioItems(
            id='absolute-radio',
            options=[{'label': i, 'value': i} for i in ['Absolute', 'Per 100k Inhabitants']],
            value='Absolute',
            labelStyle={'display': 'block'},
            style={"color" : "white",
                   "background-color":palette["block"],
                   "font-size" : 16,
                   "margin-left" : "2%",
                   "padding-top" : "10%"}
        )
    ],
        style={'display': 'grid',
               "grid-template-columns": "40% 60%",
               "box-sizing" : "border-box",
               'padding': "0% 0% 0% 0%"}
    )

# counter of cases
counter_div = html.Div([html.P('Total Cases: ', style={"color":'white'}),
                        html.P('0', id='total-cases-counter', style={"color":'white', "font-size": 30,
                              "text-align" :'center',})],
                      style={"padding": "5% 0% 0% 2%",
                             "display":"grid",
                             "grid-template-columns": "40% 60%",
                             "font-size": 20,
                         #"display": "grid",
                         #"background-color": "#222222"
                           }
)
def getTotalCases(selected_date):
    # if the selected date is not in the available dates choose the next higher date.
    if selected_date not in dates:
        for x in dates:
            if datetime.date.fromisoformat(selected_date) <= datetime.date.fromisoformat(x):
                selected_date = x
                break

    return '%d' % np.sum(df_cumulative_concelhos.loc[[selected_date]], axis=1)

# Date Picker
date_picker = dcc.DatePickerSingle(
        id='date-picker-single',
        min_date_allowed=datetime.date.fromisoformat(dates[0]),
        max_date_allowed=datetime.date.fromisoformat(dates[-1]),
        initial_visible_month=datetime.date.fromisoformat(dates[-1]),
        date=datetime.date.fromisoformat(dates[-1]),
        with_portal=True,
        style={"color":'white',
               "background-color" : palette["block"],
               "margin-top":"1%"}
    )

# Slider-Timeline

slider = html.Div(dcc.Slider(
                            id='date_slider',
                            min=min(dates_timestamp),
                            max=max(dates_timestamp),
                            value=min(dates_timestamp),
                            marks=getMarks(unixToDatetime(min(dates_timestamp)), unixToDatetime(max(dates_timestamp))),
                            included=False,
                            updatemode="drag"
                             ),
                   style={
                          #"width":"100%",
                           "margin-top":"1%",
                          "display":"grid",
                          "padding-left":0,
                          "background-color":palette["background"]}
)
timeline = html.Div(dcc.Graph(id='slider-timeline',
                              style={"display":"grid",
                                     "height":"100%", #"width":"93.8%",
                                     "padding-left":"3.9vh",
                                     "padding-right":"4vh"
                                     #"padding-top":0,
                                     #"padding-bottom":0,
                                     #"box-sizing": "border-box"
                                      },
                              config={"responsive":True, 'displayModeBar': False}),
                   style={"height":"100%",
                          "display":"grid",
                          "background-color":palette["block"],
                          "padding-bottom":"1%",
                          "box-sizing": "border-box"
                          }
                    )

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
                  showlegend=False,
                  paper_bgcolor='rgba(255,255,255,0)',
                  plot_bgcolor='rgba(255,255,255,0)',
                  )
    figure = go.Figure(data=data,
                       layout=layout)
    figure.update_layout(autosize=True,
                         margin={"autoexpand":False,
                                 "t":0, "b":0, "l":0, "r":0
                                }
    )
    figure.add_vline(x=slider_date, line_width=2, line_color="white")
    return figure

# Choropleth
class Region(Enum):
    CONTINENT = 1
    MADEIRA = 2
    AZORES = 3


def create_choropleth(selected_date, absolute, cumulative, output_region):
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

    if output_region == Region.CONTINENT:
        # update all the continente data with the values from df_concelhos
        for i in continente_data.index.tolist():
            concelho = continente_data.iloc[i, 1]
            try:
                continente_data.iloc[i, 2] = df.loc[selected_date, concelho.lower()]
            except Exception as e:
                print("Exception: ", e)

        return createFigure(continente, continente_data, max)

    elif output_region == Region.MADEIRA:
        # update all the madeira data with the values from df_concelhos
        for i in madeira_data.index.tolist():
            concelho = madeira_data.iloc[i, 1]
            try:
                madeira_data.iloc[i, 2] = df.loc[selected_date, concelho.lower()]
            except Exception as e:
                print("Exception: ", e)

        figure = createFigure(madeira, madeira_data, max)
        figure.data[0].update(showscale=False)
        return figure

    else:
        # update all the azores data with the values from df_concelhos
        for i in azores_data.index.tolist():
            concelho = azores_data.iloc[i, 1]
            try:
                azores_data.iloc[i, 2] = df.loc[selected_date, concelho.lower()]
            except Exception as e:
                print("Exception: ", e)

        figure = createFigure(azores, azores_data, max)
        figure.data[0].update(showscale=False)
        return figure

def createFigure(region, region_data, max_value):
    # %%
    fig = go.Figure()

    ## Choropleth map ######
    fig.add_choropleth(
        geojson=region,
        locations=region_data.id,
        z=region_data.value,
        colorscale="teal",
        zmin=0,
        zmax=max_value,
        hovertext=region_data[['concelho', 'value']],
        hoverinfo="text",
        showscale = False,
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
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        geo=dict(bgcolor= 'rgba(0,0,0,0)'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',)
    if region['features'][0]['properties']['CCA_2']=='0705':#for continente
        fig["layout"]["geo"]["center"] = {'lon': -12, 'lat': 39.4}
        fig["layout"]["geo"]["projection"] = {'scale': 30}
        fig["layout"]["geo"]["fitbounds"] = False
    #fig.update_layout()

    return fig



### PAGE STRUCTURE
# Minor Blocks
# Left Block 1
left_block1 = html.Div([title_div],
                        style={
                          "display": "grid",
                          "background-color": palette["block"],
                          "height" : "100%",
                          #"padding": "0% 1% 1% 1%",
                          #"box-sizing": "border-box",
                          #"margin-bottom": "50px",
                          #"margin-top": "2%"
                           }
)

left_block2 = html.Div([counter_div],
                        style={
                          "display": "grid",
                          "background-color": palette["block"],
                          "height" : "100%",
                          #"padding": "0% 1% 1% 1%",
                          #"box-sizing": "border-box",
                          #"margin-bottom": "50px",
                          "margin-top": "1.6%"
                           }
)

left_block3 = html.Div([radios_div],
                        style={
                          "display": "grid",
                          "font-color" : "white",
                          "background-color": palette["background"],
                          "height" : "100%",
                          #"padding": "0% 1% 1% 1%",
                          #"box-sizing": "border-box",
                          #"margin-bottom": "50px",
                          "margin-top": "3.2%"
                           }
)

left_block4 = html.Div([html.P('Date selected',
                               style={"display": "inline",
                                      "color":"white",
                                      "font-size":20,
                                      "margin-right":"10%", "margin-left":"3%"}),
                        date_picker],
                        style={
                          "display": "inline",
                          "background-color": palette["block"],
                          "height" : "100%",
                          #"padding": "0% 1% 1% 1%",
                          #"box-sizing": "border-box",
                          #"margin-bottom": "50px",
                          "margin-top": "4.7%"
                           }
)

right_block1 = html.Div(dcc.Graph(id='madeira',  style={"width": "100%"}),
                        style={
                          "display": "grid",
                          "background-color": palette["block"],
                          "height" : "100%",
                          #"padding": "0% 1% 1% 1%",
                          #"box-sizing": "border-box",
                          #"margin-bottom": "50px",
                          #"margin-top": "2%"
                           }
)

right_block2 = html.Div(dcc.Graph(id='azores',  style={"width": "100%"}),
                        style={
                          "display": "grid",
                          "background-color": palette["block"],
                          "height" : "100%",
                          #"padding": "0% 1% 1% 1%",
                          #"box-sizing": "border-box",
                          #"margin-bottom": "50px",
                          "margin-top": "1.2%"
                           }
)

# Sub-columns in Left Top Region
left_column = html.Div([left_block1, left_block2, left_block3, left_block4],
                        style={
                          "display": "grid",
                          "background-color": palette["background"],
                          "height" : "100%",
                          "grid-template-rows": "41.5% 23% 22% 10%",
                          #"padding": "0% 1% 1% 1%",
                          #"box-sizing": "border-box",
                          #"margin-bottom": "50px",
                          #"margin-top": "2%"
                           }
)

# Right sub-column in left region
right_column = html.Div([right_block1, right_block2],
                        style={
                          "display": "grid",
                          "background-color": palette["background"],
                          "height" : "100%",
                          "grid-template-rows": "50% 48.8%",
                          #"padding": "0% 1% 1% 1%",
                          #"box-sizing": "border-box",
                          #"margin-bottom": "50px",
                          "margin-left": "1.2%"
                        }
)

#left-top region
left_top_region = html.Div([left_column, right_column],
                        style={
                          "display": "grid",
                          "background-color": palette["background"],
                          "height" : "100%",
                          "grid-template-columns": "42% 58%",
                          #"padding": "0% 1% 1% 1%",
                          #"box-sizing": "border-box",
                          #"margin-bottom": "50px",
                          #"margin-top": "2%"
                        }
)

#left-bottom region
left_bottom_region = html.Div(
                        [slider, timeline],
                        style={
                          "display": "grid",
                          "background-color": palette["block"],
                          "height" : "100%",#"96.5%",
                          #"padding": "0% 0% 0% 0%",
                          #"box-sizing": "border-box",
                          "margin-top": "1vh",
                          #"position" : "relative",
                          "grid-template-rows": "2% 98%",
                           }
)


# Left Global Region
left_region = html.Div([left_top_region, left_bottom_region],
                        style={
                          "display": "grid",
                          "background-color": palette["background"],
                          "height" : "100%",
                          #"position" : "relative",
                          #"padding": "0% 0% 0% 0%", #t r b l
                          #"box-sizing": "border-box",
                          "grid-template-rows": "80% 18.7%",
                          #"margin-bottom": "50px",
                          #"margin-top": "2%"
                          "z-index":"1"
                           }
)

# Right Global Region
right_region = html.Div(
        html.Div(
            dcc.Graph(id='continente',  style={"width": "100%", "height": "100%"}),
            style={
                "position": "absolute",
                "width": "100%",
                "height": "95%",
                "right": 0
            }
        ),
        style={ "display": "grid",
                "background-color": palette["block"],
                "height" : "94.7vh",
                "padding": "0.5% 0.5% 0.5% 0.5%",
                "margin-left": "1%",
                "box-sizing": "border-box"
        }
    )

# container layout and elements
app.layout = html.Div([
                       left_region,
                       right_region
                      ],
                      style={"display": "grid",
                             "background-color": palette["background"],
                             "grid-template-columns": "62% 38%",
                             "height" : "97vh",
                             "padding": "0.5% 0.5% 0.5% 0.5%",
                             "box-sizing": "border-box",
                             #"position" : "relative"
                      }
)

##### CALLBACKS
#total-cases-counter
@app.callback(
    Output('total-cases-counter', 'children'),
    Input('date-picker-single', 'date')
)
def create_total_cases_counter_callback(slider_date):
    return getTotalCases(slider_date)

#Date-picker
@app.callback(
    Output('slider-timeline', 'figure'),
    Input('date-picker-single', 'date')
)
def create_slider_timeline_callback(slider_date):
    return create_slider_timeline(slider_date)

#Date Slider
@app.callback(
    Output('date-picker-single', 'date'),
    Input('date_slider', 'value'))
def slider_callback(selected_date):
    selected_date_str = str(unixToDatetime(selected_date).date())
    return datetime.date.fromisoformat(selected_date_str)

#Choropleth (continent)
@app.callback(
    Output('continente', 'figure'),
    Input('date-picker-single', 'date'),
    Input('absolute-radio', 'value'),
    Input('cumulative-radio', 'value')
)
def create_choropleth_callback(selected_date, absolute, cumulative):
    return create_choropleth(selected_date, absolute, cumulative, Region.CONTINENT)

#Choropleth (madeira)
@app.callback(
    Output('madeira', 'figure'),
    Input('date-picker-single', 'date'),
    Input('absolute-radio', 'value'),
    Input('cumulative-radio', 'value')
)
def create_choropleth_madeira_callback(selected_date, absolute, cumulative):
    return create_choropleth(selected_date, absolute, cumulative, Region.MADEIRA)


#Choropleth (azores)
@app.callback(
    Output('azores', 'figure'),
    Input('date-picker-single', 'date'),
    Input('absolute-radio', 'value'),
    Input('cumulative-radio', 'value')
)
def create_choropleth_azores_callback(selected_date, absolute, cumulative):
    return create_choropleth(selected_date, absolute, cumulative, Region.AZORES)

##### MAIN
if __name__ == '__main__':
    app.run_server(debug=True)