#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import string

import dash
from dash.dependencies import Input, Output, Event, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly
import sys
import copy
import pandas as pd
import urllib.parse

import os
sys.path.append(os.environ['SAPO_TEST_DIR']+'/py/flib_py/')
import flib.fassert as fassert
import flib.flib as flib
from flib.ftriv import *
from flib.flib import fs as fs
from flib.flib import fd as fd
from flib.flib import fdtmp as fdtmp
from flib.flib import fdsl as fdsl
from flib.flib import fdc as fdc

app = dash.Dash(__name__)

###############################################################################
############################### Page layout ###################################
###############################################################################
app.layout = html.Div(children=[
        dcc.Input(id='a',
            placeholder='Enter a value...',
            type='text',
            value=''
        ),
        html.Button(children='Submit', id='b'),
        html.Button(children='Submit2',id='c'),
        # dcc.Interval(id='interval-update', interval=1 * 1000,), # in milliseconds
])

###############################################################################
############################ Callback/Reactions ###############################
###############################################################################

x = ' '
@app.callback(
    Output('b','children'),
    [Input('a','value')]
)
def doB(value):
    global x
    x=value
    return value

@app.callback(
    Output('c','children'),
    [Input('c','n_clicks')],
    [State('a','value')]
)
def doC(n,value):
    return x

if __name__ == '__main__':
    # Use threaded=True OR processes=4 e.g. could give threading? https://community.plot.ly/t/dash-callbacks-are-not-async-handling-multiple-requests-and-callbacks-in-parallel/5848
    #   Mind: AH: Spanning new process = creating full copy of all! So cannot use that at all in my way...
    app.run_server(debug=True, threaded=False, processes = 4, use_reloader = False)
    # app.run_server(debug=True, threaded=True, use_reloader = False)
    # app.run_server(debug=True, threaded=False)
    # app.run_server(debug=True, threaded=False, processes = 4)
