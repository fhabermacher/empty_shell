import numpy as np # just to be able to plot nicely, easily
# import flib.flib as flib

# def f(a,*arg): assert (a),"Error: "+flib.fs(arg); return True
def f(a,msg=""): assert (a),"Error: "+(msg); return True
def notnone(a,msg=""): assert (a) is not None, "None where shouldn't: "+(msg); return True
def eq(a,b,msg=""): assert (a)==(b), str(a)+"!="+str(b)+": "+(msg); return True
def eqtol(a,b,tol,msg=""): assert abs((a)-(b))<=(tol), str(a)+" != "+str(b)+"+/-"+str(tol)+" "+(msg); return True
# def eq0(a,*arg): assert (a)==0, str(a)+" != 0: "+flib.fs(arg); return True
def eq0(a,msg=""): assert (a)==0, str(a)+" != 0: "+(msg); return True
def eq0tol(a,tol,msg=""): assert abs(a)<(tol), str(a)+" != 0+-"+str(tol)+": "+(msg); return True
def g0(a,msg=""): assert (a)>0, str(a)+"<=0: "+(msg); return True
def ge0(a,msg=""): assert (a)>=0, str(a)+"<0: "+(msg); return True
def ge(a,b,msg=""): assert (a)>=(b), str(a)+"<"+str(b)+": "+(msg); return True
def g(a,b,msg=""): assert (a)>(b), str(a)+"<="+str(b)+": "+(msg); return True
def l(a,b,msg=""): assert (a)<(b), str(a)+">="+str(b)+": "+(msg); return True
def rng(a,mi,ma,msg=""): assert (a)>=(mi) and (a)<=(ma), str(a)+"not in range ["+str(b)+".."+str(b)+"]: "+(msg); return True
def le(a,b,msg=""): assert (a)<=(b), str(a)+">"+str(b)+": "+(msg); return True
def ltol(a,b,tol,msg=""): assert (a)<=(b)+(tol), str(a)+">"+str(b)+" by more than tol "+str(tol)+" ("+str(b)+str(tol)+"): "+(msg); return True
def finite(a,msg=""): assert not np.isnan(a), str(a)+" not finite: "+(msg); return True
def isin(a,list,msg=""): assert (a) in (list), str(a)+" not in list: "+(msg)+": "+str(list); return True
