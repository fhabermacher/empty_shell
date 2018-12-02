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
import uuid

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
x={}
def serve_layout():
    # Original place where plotly suggested to init session_id.
    # But for me when I did here, at least on local machine, when having multiple
    # browser sessions SIMULTANEOUSLY, they all got the same id.
    # Hence I changed this, cf. onload_session_id
    session_id = 'temp_should_be_overriden'
    # session_id = str(uuid.uuid4())
    # print('New layout, for session ID ',session_id)
    # x[session_id]= ' '
    return html.Div(children=[
        # html.Div(session_id, id='session-id'),
        html.Div(session_id, id='session-id', style={'display': 'none'}),
        dcc.Input(id='a',
            placeholder='Enter a value...',
            type='text',
            value=''
        ),
        html.Button(children='Submit', id='b'),
        html.Button(children='Submit2',id='c'),
        html.Div(id='dummy-div'),
    ])


app.layout = serve_layout()


###############################################################################
############################ Callback/Reactions ###############################
###############################################################################

@app.callback(
    Output('session-id','children'),
    [Input('dummy-div','children')]
)
def onload_session_id(aux):
    session_id = str(uuid.uuid4())
    print('Onload: New layout, attributing session ID ', session_id)
    global x
    x[session_id] = ' '
    return session_id

@app.callback(
    Output('b','children'),
    [Input('a','value')],
    [State('session-id','children')]
)
def doB(value,session_id):
    global x
    x[session_id]=value
    print("Session ID = ",session_id)
    return value

@app.callback(
    Output('c','children'),
    [Input('c','n_clicks')],
    [State('a','value'),
    State('session-id', 'children')]
)
def doC(n,value,session_id):
    return x[session_id]

if __name__ == '__main__':
    # Use threaded=True OR processes=4 e.g. could give threading? https://community.plot.ly/t/dash-callbacks-are-not-async-handling-multiple-requests-and-callbacks-in-parallel/5848
    #   Mind: AH: Spanning new process = creating full copy of all! So cannot use that at all in my way...
    app.run_server(debug=True, threaded=False, processes = 4, use_reloader = False)
    # app.run_server(debug=True, threaded=True, use_reloader = False)
    # app.run_server(debug=True, threaded=False)
    # app.run_server(debug=True, threaded=False, processes = 4)
