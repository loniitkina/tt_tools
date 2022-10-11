import numpy as np
from glob import glob
from tt_func import getColumn
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates

inpath_table = '../data/MCS/MP/'
inpath_table = '../plots_meltponds/'
outpath = '../plots_meltponds/'
loc = 'Nloop'

types = ['level','rubble','ridge','deformed']

fig1 = plt.figure(figsize=(10,20))
ax = fig1.add_subplot(211)
bx = fig1.add_subplot(212)

for tt in types:

    fname = glob(inpath_table+'meltponds_'+loc+'_'+tt+'.csv')[0]
    print(fname)

    #b'date,snow depth (m),snow depth std (m),ice thickness (m),ice thickness std (m),ice mode (m)\n'

    dates = getColumn(fname,0)
    dt = [ datetime.strptime(x, '%Y%m%d') for x in dates ]
    snod = getColumn(fname,1);snod = np.array(snod,dtype=np.float)
    it = getColumn(fname,3);it = np.array(it,dtype=np.float)


    #fit the curve - snow
    x = mdates.date2num(dt) #convert time tuples to numbers
    y = snod
    model = np.polyfit(x, y, 2) #decide here the curve-order
    predict = np.poly1d(model)

    xmodel = np.arange(min(x),max(x),1) #convert numbers to dates for plotting
    dd = mdates.num2date(xmodel)
    ymodel = predict(xmodel)

    ax.plot(dd, ymodel,ls=':',alpha=.9,lw=3,label=tt)
    ax.plot(dt,snod,'x')

    #fit the curve - ice
    y = it
    model = np.polyfit(x, y, 2) #decide here the curve-order
    predict = np.poly1d(model)

    ymodel = predict(xmodel)

    bx.plot(dd, ymodel,ls=':',alpha=.9,lw=3,label=tt)
    bx.plot(dt,it,'x')
    
ax.legend()
bx.legend()
    
plt.show()
fig1.savefig(outpath+'ts_ice_type_forLinda_doubleTH.png')
