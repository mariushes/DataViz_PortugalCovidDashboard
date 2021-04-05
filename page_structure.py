# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


##### Imports
import dash
import dash_core_components as dcc
import dash_html_components as html

import json
import pandas as pd
import plotly.graph_objs as go

####

palette = {
    'background' : 'rgba(20, 20, 50, 1)',
    'block' : 'rgba(50, 50, 50, 1)',
    'borders': 'rgba(0, 0, 0, 1)',
    'text': 'rgba(114, 114, 114, 1)',
    'legendtext': 'black',
    'bartext': 'black',
}

##### Dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

##### div blocks

### Components
# Slider-Timeline
slider_div = html.Div([html.H4('Slider div', style={"color":'white'})],
                      style={
                         "display": "grid",
                          "background-color": "#222222"

                           }
)

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

# counter of cases
counter_div = html.Div([html.H4('counter div', style={"color":'white'})],
                      style={
                         "display": "grid",
                         "background-color": "#222222"

                           }
)

# Radio Buttons
radios_div = \
    html.Div([html.H4('radios div', style={"color":'white'})],
             style={
                    "display": "grid",
                    "background-color": "#222222"

                    }
    )


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

left_block2 = html.Div([html.P('Left Block 2', style={"color":'white'})],
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

left_block3 = html.Div([html.P('Left Block 3', style={"color":'white'})],
                        style={
                          "display": "grid",
                          "background-color": palette["block"],
                          "height" : "100%",
                          #"padding": "0% 1% 1% 1%",
                          #"box-sizing": "border-box",
                          #"margin-bottom": "50px",
                          "margin-top": "3.2%"
                           }
)

left_block4 = html.Div([html.P('Left Block 4', style={"color":'white'})],
                        style={
                          "display": "grid",
                          "background-color": palette["block"],
                          "height" : "100%",
                          #"padding": "0% 1% 1% 1%",
                          #"box-sizing": "border-box",
                          #"margin-bottom": "50px",
                          "margin-top": "4.7%"
                           }
)

right_block1 = html.Div([html.P('Rigth Block 1', style={"color":'white'})],
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

right_block2 = html.Div([html.P('Rigth Block 2', style={"color":'white'})],
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
left_bottom_region = html.Div([html.P('Left Bottom Region', style={"color":'white'})],
                        style={
                          "display": "grid",
                          "background-color": palette["block"],
                          "height" : "100%",
                          #"padding": "0% 0% 0% 0%",
                          #"box-sizing": "border-box",
                          "margin-top": "0.7%",
                          #"position" : "relative"
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
                          "grid-template-rows": "77% 22%",
                          #"margin-bottom": "50px",
                          #"margin-top": "2%"
                           }
)

# Right Global Region
right_region = html.Div(html.P('Right Region', style={"color":'white'}),
                      style={
                         "display": "grid",
                          "background-color": palette["block"],
                          "height": "100%",
                          "margin-left": "1.5%",
                          "padding": "0% 1% 1% 1%", # t r b l
                          "box-sizing": "border-box",
                           #"position" : "relative"
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

##### MAIN
if __name__ == '__main__':
    app.run_server(debug=True)