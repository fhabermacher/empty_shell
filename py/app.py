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


# Set path to pylib model module containing python api:
sys.path.append(fs(os.environ['SAPO_TEST_DIR'],'/py/pylib/'))
from pylib import User, Api
fd('Eventually change folder here & copy pylib.so into env SAPO_TEST_DIR')
from threading import Thread
from easygui import passwordbox # As getpass fails to avoid echoing PW in prompt
from passlib.hash import sha256_crypt
import math
from flask import request, send_from_directory # request: So can get URL with
# "request.base_url"
import logging
import base64
import io
from urllib.parse import quote as urlquote
import pickle
# Dash-Auth, for BasicAuth, nice login: Note, requires to store raw username & password pairs.
# I am really keen to simply change source (https://github.com/plotly/dash-auth) slightly
# (I tihnk simply https://github.com/plotly/dash-auth/blob/master/dash_auth/basic_auth.py)
# such as to check simply whether the hash of the pw fits instead of giving the app the entire
# list of all original passwords!!
#   Okay, so let's get my version!:

sys.path.append(fs(os.environ['SAPO_TEST_DIR'],'/py/dash-auth_fh/'))
import dash_auth

# Cleanest way to return from callback w/o update:
#   Use dash.exception PreventUpdate, with
#       "raise dash.exceptions.PreventUpdate()"
#   or after "from dash.exceptions import PreventUpdate" thus
#       "raise PreventUpdate()"
#   Yields 'silent' exception; alternative would be to pass pre-existing object as additional state
#   to callback and then return this pre-existing state, but that would mean sending forth and back
#   the entire object across network! Hence the silent exception is 'the' solution!
#   Cf. https://community.plot.ly/t/exiting-a-callback/7256/7
#   and https://community.plot.ly/t/improving-handling-of-aborted-callbacks/7536
from dash.exceptions import PreventUpdate


# Key options:
# -General
allow_web = False # Allow dash to request online resources. Set to False to
# avoid errors if not connected
suppress_logging = False # Avoid regular line updates from e.g. interval event
progressnce_silent = 1 # Avoid each zns from printing lots on comand line, instead only make a '.' to indicate next zoom'n'shuffle
# -Graph
linemode = 'lines' # Graph line mode: 'lines+markers' or 'lines', or ...?
maxbar_allow = 60 # For bar plot: Max number of bars allowed to be plotted; else force reversion to line
# -File system
freespaceminGB = 1 # How many spare Gigabytes of space requested before
# allowing people to upload files. E.g. 20

#   Note, improvement would be: is there a way to suppress logging all while preserving display of router link? Or can I get router link separately?
if suppress_logging:
    fd('Typical links to app can be http://127.0.0.1:5000/ or http://127.0.0.1:8050/ . To see actual link, set suppress_logging=False')
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

datestamp = flib.timestamp(True)
timestamp = flib.timestamp()
oxee_copyright = """
Copyright: Oxford Energy Economics, {0}. All rights reserved.
Use, copying, and spreading of any code, data, pictures,
ideas or algorithms without explicit permission by Oxford
Energy Economics is strictly prohibited.""".format(datestamp)

version = 'Test'

x = {}
sha256salt = User.sha256salt
# x = Api("myApi")
# sha256salt = x.sha256salt

usercredlistV2str = User.getusercredlist()
# usercredlistV2str = x.getusercredlist()
global customcurr
up_sub = ["sub1","sub2"] # All possible ones; we'll
# idle them and activate only those that relevant for current user type
customcurr = {sub: False for sub in up_sub} # Preliminary assignment
VALID_USERNAME_PWHASH_PAIRS = [[s for s in pair] for pair in usercredlistV2str]
global user
created = False
app = dash.Dash(__name__)
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PWHASH_PAIRS,
    sha256salt = sha256salt,
    loginmsg = 'Login to SaPo {}'.format(version)
)
# Accoridng to https://dash.plot.ly/urls :
# Since we're adding callbacks to elements that don't exist in the app.layout,
# Dash will raise an exception to warn us that we might be
# doing something wrong.
# In this case, we're adding the elements through a callback, so we can ignore
# the exception.
app.config.suppress_callback_exceptions = True

server = app.server

def verify_username(name): # Make sure is simple (A-Za-z0-9) username,
# esp. to avoid any (to me unknown) risk of folder-haking or so when
# user folder to be created/accessed
# Set-based solution thanks to https://stackoverflow.com/a/1323374/3673329
    name_ok = len(name) and\
              (set(name) <= set(string.ascii_uppercase +
                                string.ascii_lowercase + string.digits))
    if not name_ok:
        ferr("Invalid username: ",name,'\n  Must have non-empty string of '
                                       'simple characters & digits')

def usermainfolder(name):
    return fs(os.environ['SAPO_TEST_DIR']+'/guestbook/')
def userfolder(name,subfolder):
    return fs(usermainfolder(name),subfolder,"/")

global upload_dir
def createuserfoldersmaybe(name):
    verify_username(name)
    global upload_dir
    upload_dir = {sub: userfolder(name,sub)
                  for sub in up_sub} # The
    [flib.mkdirIfNotExist(dir) for dir in upload_dir.values()]

fileoptions = {sub: [] for sub in up_sub}


# For being able to serve downloadable files also from directory
@server.route(os.environ['SAPO_TEST_DIR']+'/guestbook/<path:path>')
def download(path): # path being what comes after
    """Serve a file from the upload directory."""
    return send_from_directory(os.environ['SAPO_TEST_DIR']+'/guestbook/', path,
                               as_attachment=True)

def file_download_link_href(sub,filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    location = upload_dir[sub]+"{}".format(urlquote(filename))
    return location
def file_download_link(sub,filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    location = upload_dir[sub]+"{}".format(urlquote(filename))
    return html.A(filename, href=location)

if allow_web:
    fdc(flib.fdcolor.Red,"Currently avoiding external codeopen.io/chriddyp's css which creates inconvenient formatting")
    app.css.append_css({
        'external_url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'})

else:
    # Ensure offline-executable, cf. https://github.com/plotly/dash/issues/46#issuecomment-311065463
    app.css.config.serve_locally = True
    app.scripts.config.serve_locally = True

def maybelogo(allow):
    if allow:
        return html.Img(src='http://habermacher.net/wp-content/uploads/2018/09/OXEE_Orange_on_Black.png', width=246, height=135)
    else:
        return html.Div('',id='no-logo',style={'display': 'none'})

def maybeaction(allow):
    if allow:
        return html.Img(id='actiongifortxt',src='https://78.media.tumblr.com/ece4d7611a52431ba31f150dad98ebad/tumblr_mw2efvjVGb1rhz43wo1_500.gif',width=250, height=131, style={'visibility': 'hidden'})
    else:
        return html.Div('RUNNING',id='actiongifortxt',style={'visibility': 'hidden'})

threads = []

progressd_str = 'SOLVED'
conv_share_str_base = 'Solved ca. '


next_init_dropdown_value = {sub: False for sub in up_sub}

num_thread = 3 # Second interval duration
duration_sec = 10

# Messagebox
msg_for_box = ''


app.title='SaPo @ Oxford Energy Economics'


usermodelfiles = {sub: None for sub in up_sub}

global cookiedir

def load_cookie():
    global usermodelfiles
    filename = cookiedir+'modelfiles.p'
    try:
        # First reload and make sure if new session has additional
        usermodelfiles_restore = pickle.load(open(filename, 'rb'))
        for sub in usermodelfiles:
            if sub in usermodelfiles_restore:
                usermodelfiles[sub] = usermodelfiles_restore[sub]
        for sub,val in usermodelfiles.items():
            if sub in usermodelfiles_restore:
                usermodelfiles[sub] = usermodelfiles_restore[sub]
            if (val is None) or (not os.path.isfile(userfolder(user,sub)+val)):
                fd("Cookie entry ignored: file ",val," @ ",sub," not found")
                usermodelfiles[sub] = None
        fd('User model file choice loaded from server cookie')
    except FileNotFoundError:
        fd("No cookie for modelfiles found for user ")
    except Exception as e:
        fdc(flib.fdcolor.Red, "Modelfiles cookie not loaded due to "
                              "error:\n",str(e))

def save_cookie():
    global usermodelfiles
    flib.mkdirIfNotExist(cookiedir)
    fd("Saving: {}/{}".format(usermodelfiles, cookiedir))
    pickle.dump(usermodelfiles, open(cookiedir + 'modelfiles.p', 'wb'))

def up_div(name):
    dropdownanddragselect = \
        html.Div(id='filesub'+name, children=[
                html.Div(children=dcc.Dropdown(
                        id='file-dropdown'+name,
                        options=fileoptions[name],
                        multi=False,
                        placeholder="Select "+name+" file ...",
                        value=usermodelfiles[name],
                    ),
                    style={'width': '40%','display': 'inline-block',}
                ),
                html.A(id='userfile-download'+name,n_clicks=0,
                       children=[html.I(className='fa fa-cloud-download')],
                       title='Download current file',  # title = Hovertext!
                       style={'width': '5%',
                              'display': 'inline-block',
                              'text-align': 'center',
                              },

               ),
                html.Div(id='filedd-container'+name,style={'display':'none'}),
                dcc.Upload(
                    id='upload-data'+name,
                    children=html.Div([
                        "Drag or ",
                        html.A('Browse File(s)')
                    ]),
                    style={
                        'width': '35%',
                        'height': '30px',
                        'lineHeight': '30px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px',
                        'display': 'inline-block'
                    },
                    multiple=True
                ),
                html.A(id='wipe-button'+name,n_clicks=0,
                       children=[html.I(className='fa fa-eraser')],
                       title='Wipe uploads', # title = Hovertext!
                       style={'display': 'inline-block'},
                       href='#'),
                html.Div(id='wipe-container'+name, style={'display': 'none'}),
            ],
            style={'display': 'none'}
        )
    return dropdownanddragselect



###############################################################################
############################### Page layout ###################################
###############################################################################
app.layout = html.Div(children=[
    dcc.Location(id='url', refresh=False),
    html.Div(session_id, id='session-id'),
    # html.Div(session_id, id='session-id', style={'display': 'none'}),
    html.Div('',id='onload-only',style={'display': 'none'}),
    html.H2(children='SaPo Energy Model '+version),
    maybelogo(allow_web),
    html.Div(children=oxee_copyright,id='copyright-div'),
    html.Div(id='upload-section',
        children=[ *[up_div(sub) for sub in up_sub] ],
        style={"max-width": "700px"},
    ),

    html.Button('Activate', id='activate-button'),
    html.Div(id='activate-container',style={'display': 'none'}),
    html.Div(id='run-controls',children=[
        html.Button('Launch', id='launch-button',title='Run the model'),
        html.Div(id='create-container', style={'display': 'none'}),
        html.Div(id='launch-container',  style={'display': 'none'}),
        html.Div(id='msg-box',  style={'color': 'red', 'display': 'none'}),
    ]),
    maybeaction(allow_web),
    html.Div(id='prog-container',children=''),
    html.Div([
        html.Div([
            dcc.Input(id='thread-input', type='number', inputmode='numeric', min=1, step=1, value=num_thread, maxlength=4),
            html.Span(children=' Number of threads '),
            html.Span(children='',id='thread-container',style={'display':
                                                                   'none'}),

            dcc.Input(id='duration-input', type='number', inputmode='numeric', min=1, step=1, value=duration_sec, maxlength=4),
            html.Span(children=' Duration (sec) '),
            html.Span(children='',id='duration-container',style={'display':
                                                                     'none'}),
        ]),
    ]),
    dcc.Interval(id='interval-update', interval=1 * 1000,), # in milliseconds
])

###############################################################################
############################ Callback/Reactions ###############################
###############################################################################

def xsidif(sid,alt='',abort=False,preventupdate=False):
    if sid in x:
        return x[sid]
    elif abort:
        flib.ferr(__name__,": x has no ",sid,"\n x = ",x)
    elif preventupdate:
        raise PreventUpdate
    else:
        return alt

# Upload files. Cf. also
#   https://docs.sherlockml.com/user-guide/apps/examples/dash_file_upload_download.html
#   https://dash.plot.ly/dash-core-components/upload
def save_file(name, content, sub):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1] # Create bytes object
    server_fn = os.path.join(upload_dir[sub], name)
    with open(server_fn, "wb") as fp:
        fp.write(base64.decodebytes(data))

def stored_files(sub,inclpath=False):
    """List the files in the upload directory.
    If raw then entire names incl. path, else raw filenames w/o path
    """
    files = []
    for filename in os.listdir(upload_dir[sub]):
        path = os.path.join(upload_dir[sub], filename)
        if os.path.isfile(path):
            files.append(path if inclpath else filename )
    return files


# Auxiliary to help auto-updating file dropdown selection to last INDIVIDUAL
#  uploaded file. None = no particular value to update to
up_dd_update = {sub: None for sub in up_sub}
# Auxiliary for... ah let me not talk about the dash limitations, but it's
# to allow me to essentially create (combine) multiple callbacks for one
# Output which Dash does not readily allow
wipe_n_clicks_save= {sub: 0 for sub in up_sub}

@app.callback(
    Output('session-id','children'),
    [Input('onload-only','children')]
)
def onload_session_id(aux):
    session_id = str(uuid.uuid4())
    print('Onload: New layout, attributing session ID ', session_id)
    global x
    x[session_id] = ' '
    return session_id


for sub in up_sub:
    @app.callback(
        Output('file-dropdown'+sub, 'options'),
        [Input('activate-container', 'children'),
         Input('upload-data'+sub, 'filename'),
         Input('upload-data'+sub, 'contents'),
         Input('file-dropdown'+sub, 'id'),
         Input('wipe-button' + sub, 'n_clicks'),
         ],
    )
    def update_file_dd_or_wipe(dummy_txt,uploaded_filenames, uploaded_file_contents, id,
                               wipe_n_clicks):
        """Combined file dropdown options update callback:
        Needed to combine because each property allowed only ONE OUTPUT CALLBACK
        -File initialization at activation (pre-existing files on disk)
        -File upload
        -File erasing
        """
        sub_extracted = id[len("file-dropdown"):] # Need this cumbersome way
        #  as only through callback-arguments can sneak in dynamic behavior
        # of function itself!
        """Save upload files, and store name."""
        if uploaded_filenames is not None and uploaded_file_contents is not None:
            if len(uploaded_filenames) is 1:
                up_dd_update[sub_extracted] = uploaded_filenames[0]
            for name, data in zip(uploaded_filenames, uploaded_file_contents):
                save_file(name, data,sub_extracted)
        if (wipe_n_clicks==wipe_n_clicks_save[sub_extracted]): # For this
            """Simply show all existing/uploaded files."""
            # to not be dangerous despite onload auto-clicks messing up
            # wipe_n_clicks_save vs. wipe_n_clicks, important to above
            # always update wipe_n_clicks_save before raising the PreventUpdate
            #  in the pre-active period!
            # Now simpler & more robust: always simply show all files in folder
            opt = [{'label': os.path.basename(file),
                    'value': os.path.basename(file)} for file in
                   stored_files(sub_extracted)]
        else:
            if (not active()):
                wipe_n_clicks_save[sub_extracted] = wipe_n_clicks
                raise PreventUpdate
            """Wipe uploaded files."""
            files_inclpath = stored_files(sub_extracted,True)
            fd("Files to erase are\n",files_inclpath)
            [os.remove(file) for file in files_inclpath]
            opt = []
            wipe_n_clicks_save[sub_extracted] = wipe_n_clicks
        return opt

    @app.callback(
        Output('file-dropdown'+sub, 'value'),
        [Input('activate-container','children'), # Should change only once
         # at activation
         Input('file-dropdown' + sub, 'options'),
         Input('file-dropdown'+sub, 'id')])
    def dropdownoptions(dummy_txt, dummy_opt, id):
        sub_extracted = id[len("file-dropdown"):] # Need this cumbersome way
        global next_init_dropdown_value
        if next_init_dropdown_value[sub_extracted]:
            """Update dropdown options with cookie-file right after activation."""
            next_init_dropdown_value[sub_extracted]=False
            value = usermodelfiles[sub_extracted]
        elif (up_dd_update[sub_extracted] is not None):
            if not active(): raise PreventUpdate
            """Update dropdown options with single newly-added file."""
            value = up_dd_update[sub_extracted]
            up_dd_update[sub_extracted]=None
        else: raise PreventUpdate
        return value

    @app.callback(
        Output('filesub'+sub, 'style'),
        [Input('activate-container','children'), # Should change only once
         # at activation
         Input('filesub'+sub, 'id')],
        state=[State('filesub'+sub, 'style')])
    def enable_customfile_current(dummy_txt, id,origstyle):
        sub_extracted = id[len("filesub"):] # Need this cumbersome way
        global customcurr
        style=origstyle
        style['display'] = 'inline' if customcurr[sub_extracted] else 'none'
        return style

    @app.callback(
        Output('filedd-container'+sub, 'children'),
        [Input('file-dropdown'+sub, 'value'),
         Input('file-dropdown' + sub, 'id'),],
    )
    def update_file_choice_for_model(value,id):
        sub_extracted = id[len("file-dropdown"):] # Need this cumbersome way
        global usermodelfiles
        usermodelfiles[sub_extracted] = value
        save_cookie()
        return None


    @app.callback(
        Output('userfile-download'+sub, "href"),
        [Input('file-dropdown' + sub, 'value'),
        Input('file-dropdown' + sub, 'id'),],
    )
    def provide_download(fn,id):
        if not fn:
            return "."
        sub_extracted = id[len("file-dropdown"):] # Need this cumbersome way
        return file_download_link_href(sub_extracted,fn)


@app.callback(
    Output('msg-box','style'),
    [Input('msg-box','children')],
    state=[State('msg-box','style')]
)
def updatemsgboxdisabled(text,origstyle):
    style = origstyle
    style['display'] = 'block' if text else 'none'
    return style

@app.callback(
    Output('msg-box','children'),
    state=[State('msg-box','children')],
    events=[Event('interval-update', 'interval')]
)
def updatemsgboxtxt(currtext):
    if (msg_for_box is currtext):
        raise PreventUpdate
    return msg_for_box



# Progress indication
@app.callback(
    Output('prog-container','children'),
    state=[State('prog-container','children'),
           State('sid', 'children')],
    events=[Event('interval-update', 'interval')])
def progress_text(origtext,sid):
    return xsidif(sid,"No init yet").run_status()
    # return x[sid].run_status()

# Set threads
@app.callback(
    Output('thread-container','children'),
    [Input('thread-input','value')])
def auto_interval_set(value):
    global num_thread
    num_thread = value
    return ''
# Set duration
@app.callback(
    Output('duration-container','children'),
    [Input('duration-input','value')])
def auto_interval_set(value):
    global duration_sec
    duration_sec = value
    return ''



# BACKGROUND ON IMPORTANT 'Activate/Active' CONCEPT, implemented by means of the next 2-3 functions:
#   Py Dash insists on auto-calling all callbacks upon page (re-)load!
#   For our purposes this is not warranted: E.g., we do not want model to be launched upon page load,
#   but instead only allow user to launch it manually
#   'Activate'/'active()' helps us overcome this issue of unwarranted auto-execution:
#       We ensure 'active()' is false for at least hte first 2 seconds, and ensure crucial functions
#       like the model launcher 'Launch' are not fully executed unless 'active()', meaning Py Dash
#       calls the 'Launch' callback, but our function written in that callback exits without really launching
#       unless active() is true, which only happens after >=2 sec from page load or 'Activation' button click.

# Indicator fct. telling whether app is 'active':
#   Helper to manually avoid all callbacks from being fully executed on pageload
idle_until = np.inf
def active():
    global idle_until
    return time.time()>idle_until

# 'Activate' app with delay of 2 sec to 'survive' page-load period where dash app may sadly auto-call all callback functions automatically:
#   Also creates system: x.createsys, for authenticated user
#  Enabling esp. also 'Launch' button after this delay.
#       Update: only allow launch if user selected all files!
#   Note, may gets executed automatically upon page load, else user simply to push the corresponding Activate button manually
@app.callback(
    Output('activate-container','children'),
    [Input('activate-button', 'n_clicks')],
    [State('sid', 'children')],)
def activation(n_clicks,sid):
    x[sid] = Api("myapi")
    x[sid].authenticate(auth._username, auth._pwhash)
    global user, customcurr, fileoptions, cookiedir, next_init_dropdown_value
    user = auth._username
    customcurr = {sub: True for idx,sub in enumerate(
        up_sub)}
    createuserfoldersmaybe(user)
    fileoptions = {sub: [{'label': file, 'value': file} for file in
                         flib.filesinpath(dir)] for sub, dir in
                   upload_dir.items()}
    cookiedir = userfolder(user, 'cookie')
    load_cookie()
    next_init_dropdown_value = {sub: True for sub in up_sub}
    global idle_until
    idle_until = time.time() + 2
    return "Activated"

@app.callback(
    Output('create-container','children'),
    [Input('launch-button', 'n_clicks')],
    [State('sid', 'children')], )
def create(n_clicks,sid):
    if not active(): raise PreventUpdate()
    # Create system:
    result = xsidif(sid,'',False,True).createsys()
    # result = x[sid].createsys()
    global msg_for_box
    msg_for_box = result
    if result:
        fd(result)
        raise PreventUpdate
    global created
    created = True
    return 'Launched (Created) {} times'.format(n_clicks)

@app.callback(
    # Mind, Output here will not really be updated, as the t=Thread(...) launching
    # seems to block rest of function incl. the return/Output update!
    Output('launch-container','children'),
    [Input('create-container', 'children')],
    [State('sid', 'children')],)
def launch(n_clicks,sid):
    if not (active() and sid in x):
        raise PreventUpdate()
    # Run it
    global threads, progressnce_silent
    t = Thread(target=x[sid].run(duration_sec,num_thread,progressnce_silent))
    # Hm, seems that the 't=Thread(..)' line already exits/stops fct. (?)
    # and rest below not really executed anymore
    threads.append(t)
    t.start()
    print("Running now  .")
    return 'Launched {} times'.format(n_clicks)

def currfilesokay():
    for sub in up_sub:
        if customcurr[sub]:
            # 'not x' is true if x is None or if it is empty string '', great:
            if not usermodelfiles[sub]: return False
    return True

# Enable/Disable launch button depending on whether app 'active' & model running
@app.callback(
    Output('launch-button','disabled'),
    state=[State('sid', 'children')],
    events=[Event('interval-update', 'interval')])
def update_launch_button(sid):
    enable = active() and (sid in x) and (not x[sid].running(False))
    # if enable: # Pbly must first check this separately, to avoid calling
    #     # currfilesokay() before model is active at all
    #     if not currfilesokay():
    #         enable=False
    return not enable

@app.callback(
    Output('actiongifortxt','style'),
    state=[State('sid', 'children')],
    events=[Event('interval-update', 'interval')])
def update_halt_button(sid):
    if active() and (sid in x) and x[sid].running(False):
        visibility = 'visible'
    else:
        visibility = 'hidden'
    return {'visibility': visibility}

if __name__ == '__main__':
    # Use threaded=True OR processes=4 e.g. could give threading? https://community.plot.ly/t/dash-callbacks-are-not-async-handling-multiple-requests-and-callbacks-in-parallel/5848
    #   Mind: AH: Spanning new process = creating full copy of all! So cannot use that at all in my way...
    app.run_server(debug=True, threaded=True, use_reloader = False)
    # app.run_server(debug=True, threaded=False)
    # app.run_server(debug=True, threaded=False, processes = 4)
