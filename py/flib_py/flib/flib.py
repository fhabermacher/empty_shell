import datetime
import os
import errno
import numpy as np # just to be able to plot nicely, easily
import flib.fassert as fassert
import sys
import matplotlib.pyplot as plt
import math
from os.path import isfile

## FString
class fdcolor: # Inspired by: https://stackoverflow.com/a/287944/3673329, http://ozzmaker.com/add-colour-to-text-in-python/, https://en.wikipedia.org/wiki/ANSI_escape_code
    Black=30 # Overall color ANSI str for Black will be '\033[30m'
    Red=31
    Green=32
    Yellow=33
    Blue=34
    Magenta=35
    Cyan=36
    White=37
    BrightBlack=90
    BrightRed=91
    BrightGreen=92
    BrightYellow=93
    BrightBlue=94
    BrightMagenta=95
    BrightCyan=96
    BrightWhite=97
    Bold=1
    Reset=0
    @staticmethod
    def fromstr(colstr):
        if colstr is "Black": return fdcolor.Black
        elif colstr is "Red": return fdcolor.Red
        elif colstr is "Green": return fdcolor.Green
        elif colstr is "Yellow": return fdcolor.Yellow
        elif colstr is "Blue": return fdcolor.Blue
        elif colstr is "Magenta": return fdcolor.Magenta
        elif colstr is "Cyan": return fdcolor.Cyan
        elif colstr is "White": return fdcolor.White
        elif colstr is "BrightBlack": return fdcolor.BrightBlack
        elif colstr is "BrightRed": return fdcolor.BrightRed
        elif colstr is "BrightGreen": return fdcolor.BrightGreen
        elif colstr is "BrightYellow": return fdcolor.BrightYellow
        elif colstr is "BrightBlue": return fdcolor.BrightBlue
        elif colstr is "BrightMagenta": return fdcolor.BrightMagenta
        elif colstr is "BrightCyan": return fdcolor.BrightCyan
        elif colstr is "BrightWhite": return fdcolor.BrightWhite
        elif colstr is "Bold": return fdcolor.Bold
        elif colstr is "Reset": return fdcolor.Reset
        else:
            fd("Unrecognized color string")
            exit()
    @staticmethod
    def full(color):
        if type(color) is str:
            color = fdcolor.fromstr(color)
        return fs('\033[',color,'m')

def fs(*arg):
    s=""
    for a in arg:
        s+=str(a)
    return s
def fsfw(width, *arg, just="left"):
    """
    Fixed-width string, padding with empty spaces. New version: Does not truncate anymore as less risky, and trivial enough to truncate from outside
    :param width:
    :param arg:
    :param just:
    :return:
    """
    s=fs(*arg)
    n = len(s)
    if just=="left": s=s.ljust(width)
    elif just=="right": s=s.rjust(width)
    elif just=="center": s=s.center(width)
    else: ferr("Unrecognized just param ",just)
    return s
def fd(*arg):
    print(fs(*arg))
def fdsl(*arg): # fd without newline. Cf. also https://stackoverflow.com/questions/5598181/python-multiple-prints-on-the-same-line
    print(fs(*arg),end="",flush=True)
def fdc(color,*arg): # Write colored/formatted string. Color argument either string (cf. fdcolor.fromstr()) or fdcolor type
    print(fdcolor.full(color),fs(*arg),fdcolor.full(fdcolor.Reset))
def fsx(vn): return vn+": "+fs(eval("fs("+vn+")")) # For vn a variable name string, returns name and value
def fdtmp(*arg): # Same as fd but to flag as developer that is only
    # temporarily in code
    fd(*arg)

## Error message
def ferr(*args):
    # Now separately printing the message, for PyCharm compatibility, cf. https://stackoverflow.com/a/38908789/3673329
    fdc('Red','ferr: ',fs(*args))
    sys.exit(1)

def idxmax(arr): # Returns nDim indexes of max in multidimensional array arr. If multiple same max elements, first is taken
    return np.unravel_index(arr.argmax(), arr.shape)
def idxmin(arr): # Returns nDim indexes of min in multidimensional array arr. If multiple same min elements, first is taken
    return np.unravel_index(arr.argmin(), arr.shape)
def maxandidx(arr): # Returns max & indexes of max in the multidimensional array arr. If multiple same max elements, first is taken
    idx = idxmax(arr)
    return arr[idx], idx
def minandidx(arr): # Returns max & its indexes in the multidimensional array arr. If multiple same min elements, first is taken
    idx = idxmin(arr)
    return arr[idx], idx

def fround(x,nsigdig):
    """
    :brief round to nsigdig significant digits, but leave pre-floating dot numbers intact
    :param x:
    :param nsigdig:
    :return:
    """
    a = math.floor(math.log10(abs(x)))
    return round(x,max(0,nsigdig-a))

## Time
def timestamp(dateonly=False):
    if dateonly:
        return datetime.date.today().strftime("%Y%m%d")
    else:
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def daterange(date1, date2):
    """
    Generate dates between two dates
    :param date1: Start date
    :param date2: End date
    :return: Date between two dates. Note includes both given dates i.e. is '[]' rather than '[)'
    """
    for n in range(int((date2 - date1).days)+1):
        yield date1 + datetime.timedelta(n)

def daydelta(days): # Shortcut for the lengthy datetime.timedelta(days=days)
    return datetime.timedelta(days=days)

def weekBoundaries(year, week, doublecheck=True):  # Thanks for inspiration to https://bytes.com/topic/python/answers/499819-getting-start-end-dates-given-week-number, though I had to change bunch, also to make it correct for all years (consider iso standard rule for 4 days)
    # Note, first calendar year week acc. to ISO: is the first week with a majority (4 or more) of its days in January. Cf. https://en.wikipedia.org/wiki/ISO_week_date#First_week
    startOfYear = datetime.date(year, 1, 1)
    week0 = startOfYear - datetime.timedelta(
        days=startOfYear.isoweekday() - 1 +7*(startOfYear.isoweekday()<=4))  # week0 = last week before year's first week week 1. isoweekday has: Monday == 1 ... Sunday == 7!  Mind, by ISO std definition, first week 1 is the one which has at least 4 days in the year, i.e. for Mon until Thu i.e. for weekday <= 4, the beginning of the week of 1 Jan is already week 1, as opposed to last year's last week 'week0'
    mon = week0 + datetime.timedelta(weeks=week) # Recall, 'week0' is really the '0th' calendar week, i.e. last iso week before the year, the last week before the first calendar week
    sun = mon + datetime.timedelta(days=6)
    fassert.eq0(mon.weekday(), "Hm, does not seem to be Monday")  # Mind, weekday() has Mon=0, Sun = 6!
    fassert.eq(sun.weekday(), 6, "Hm, does not seem to be Sunday")  # Mind, weekday() has Mon=0, Sun = 6!
    fassert.eq(mon.isocalendar()[1], week, "Hm, somehow dates now are wrong calendar week")
    return mon, sun


## Generators
def lenOfGenerator(generator):
    return sum(1 for x in generator)

## Files
def mkdirIfNotExist(pathOrFn):
    if not os.path.exists(os.path.dirname(pathOrFn)):
        try:
            os.makedirs(os.path.dirname(pathOrFn))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
def filesinpath(path,abortifnotpath=True):
    """
    List all files (not sub-paths) in path
    Cf. also https://stackoverflow.com/a/3207973/3673329
    :param path:
    :param abortifnotpath:
    :return:
    """
    if not os.path.exists(os.path.dirname(path)):
        if abortifnotpath:
            ferr("Path ",path," does not exist")
        return []
    _, _, filenames = next(os.walk(path), (None, None, []))
    return filenames
def freespaceinfolderMB(path): # Free space in filesystem containing folder,
    #  in Megabytes
    statvfs = os.statvfs(path)
    freeuseablebites = statvfs.f_frsize * statvfs.f_bavail
    return freeuseablebites/1048576 # 1 MB = 1024 * 1024 bytes
def get_sizeMB(start_path = '.'): # Size of all files in folder incl.
    # subfolders, essentially from https://stackoverflow.com/a/1392549/3673329
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size/1048576 # 1 MB = 1024 * 1024 bytes


## Time-series
def MA(ts, radius=None, width=None,mode="NAN"): # mode {NAN,const,trim}: Whether to fill undefined ends (of length=radius=width/2) with NAN or const, or whether trim these away (returning series with the undefined ends removed)
    fassert.f((radius==None) != (width==None),fs("Exactly one of the two, radius and width, must be provided as not-None, but here radius="+str(radius)," and width="+str(width)))
    n = len(ts)
    fassert.f(["NAN","const","trim"])
    if width!=None:
        fassert.eq(width%2,1,"Width must be impair integer (or None, if radius provied instead)")
        radius=int((width-1)/2)
    else:
        width=2*radius+1
    fassert.ge(n,width,"ts shorter than kernel")
    ma = np.zeros(n-2*radius)
    ma[0]=sum(ts[:width])
    for i in range(1,n-2*radius):
        if np.isnan(ma[i-1]):
            ma[i]=sum(ts[i:(width+i)]) # Computationally inefficient way to avoid perpetuating possible NAN
        else:
            ma[i]=ma[i-1]-ts[i-1]+ts[i+width-1]
    if mode!="trim":
        if mode == "NAN":
            val = np.zeros(radius)
            val.fill(np.nan)
            ma=np.concatenate((val,ma,val))
        else:
            val0=valE = np.zeros(radius)
            val0.fill(ma[0])
            valE.fill(ma[-1])
            ma=np.concatenate((val0,ma,valE))
        fassert.eq(len(ts),len(ma),"len(ts)!=len(ma)")
    ma/=width
    fassert.ge(np.nanmax(ts),np.nanmax(ma),"Hm, ma max logically had to be at least ts max")
    fassert.ge(np.nanmin(ma),np.nanmin(ts),"Hm, ma min logically had to be at max ts min")
    return ma

def mypcolor(data, ax=None, basetitle="", xlab=None, ylab=None, xval=None, yval=None, bestdir="max", colorbar=True, dobest=True):
    if not ax: fig, ax = plt.figure()
    pc = ax.pcolor(data.T)
    if colorbar: plt.colorbar(pc)
    nx,ny=data.shape
    if xlab: ax.set_xlabel(xlab)
    if ylab: ax.set_ylabel(ylab)
    if xval is None: xval = range(nx)
    else: fassert.eq(nx,len(xval))
    if yval is None: yval = range(ny)
    else: fassert.eq(ny,len(yval))
    ax.set_xticks(np.arange(nx)+.5)
    ax.set_xticklabels(xval)
    ax.set_yticks(np.arange(ny)+.5)
    ax.set_yticklabels(yval)
    if dobest:
        bestval, idxbest = maxandidx(data) if bestdir is "max" else minandidx(data)
        ibestx, ibesty = idxbest
        # bestval, ibestx, ibesty = bestinarray(data,bestdir)
        bestx = xval[ibestx]
        besty = yval[ibesty]
        ax.scatter(ibestx+.5,ibesty+.5)
        besttitle=fs(". ", bestdir,"=", np.round(bestval,3),"@", bestx, "/", besty)
    else:
        besttitle=""
    ax.set_title(fs(basetitle,besttitle))
    if dobest:
        return bestval, bestx,besty, ibestx, ibesty
    else:
        return None

def show():
    """
    Show the graphs w/o interrupting program. So like pyplot's show() but w/o interrupting
        Convenient also as lets user debug program on console w/o first closing all graphs
    :return:
    """
    plt.draw()
    plt.gcf().canvas.flush_events()
    plt.pause(1e-17)  # Crucial, otherwise the picture updating doesn't happen!
