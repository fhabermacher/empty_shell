## Testing flib components

import datetime
import os
import errno
import numpy as np # just to be able to plot nicely, easily
import flib.fassert as fassert
import flib.flib as flib

# Test flib.MA
testdat = np.random.rand(100)
rad = 10
testMA = flib.MA(testdat,radius=rad,mode="NAN")
for i in range(rad,100-rad):
    fassert.eqtol(testMA,np.mean(testdat[i-rad:i+rad+1])
