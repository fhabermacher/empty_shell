# Lil trivialities that at times help write few less letters or so
import numpy as np
from flib.flib import fs as fs
from flib.flib import fsfw as fsfw
from flib.flib import fd as fd
from flib.flib import fdsl as fdsl
from flib.flib import fdc as fdc
from flib.flib import ferr as ferr

def rngincl(start,stopIncl,step=None): # vector INCL last value, i.e.  [] instead of [)
    return np.arange(start,stopIncl+(step if step else 1),step)

import time
tictoctime = 0.0
tictocdisp = False
def tic(tictocdisp_=None):
    global tictoctime
    tictoctime = time.time()
    if not (tictocdisp_ is None):
        global tictocdisp
        tictocdisp = tictocdisp_
def toc(s=""):
    global tictoctime
    t = time.time()-tictoctime
    if tictocdisp:
        fd(("" if s is "" else fs(s,": ")),round(t,4),"s")
    return t
def toti(s=""):
    t = toc(s)
    return t

def removeDot0(s): # Remove, in result, trailing ".0" if present at end of string s
    while (s[-1] in ["0","."]) and "." in s: s=s[:-1]
    return s

def smartround(val,relevantmagnitudes,strRmvDot0=False):
    """
    :param val: number
    :param relevantmagnitudes: int number
    :param strRmvDot0: whether convert into string and remove any trailing '.0..'
    :return: val rounded such as to preserve at least relevantmagnitudes relevant digits; if strRmvDot0 then string with possible '.0..' removed
        E.g. smartround(333.33,4)=333.3, smartround(333.3,2)=smartround(333.3,3)=333
    """
    if val>0:
        v = round(val, max(0, relevantmagnitudes - int(round(np.log10(val)))))
    elif val<0:
        v = -round(-val, max(0, relevantmagnitudes - int(round(np.log10(-val)))))
    elif val is 0:
        v = 0
    else:
        ferr("Unidentified value number type: \n",val,"\n",type(val))
    return removeDot0(str(v)) if strRmvDot0 else v

def smartroundRemoveDot0(val,relevantmagnitudes):
    s = removeDot0(str(smartround(val,relevantmagnitudes)))
