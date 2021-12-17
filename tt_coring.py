import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from datetime import datetime
from glob import glob
from tt_func import getColumn, polymodel
import pandas as pd
import matplotlib.dates as mdates

inpath='../data/coring_dark_site_Evegnii/'
outpath = inpath

fname = inpath+'All_legs_FYI_it.csv'
fname = inpath+'All_legs_SYI_it.csv'
dt = getColumn(fname,10, skipheader=2)
it = getColumn(fname,13, skipheader=2)
date = [ datetime.strptime(dt[x], "%m/%d/%Y %H:%M") for x in range(len(dt)) ]
it = np.array(it,dtype=np.float)

#plot
plt.plot(date,it)
plt.show()

#prepare output for SnowModel
year = [ datetime.strftime(x, "%Y") for x in date ]
month = [ datetime.strftime(x, "%m") for x in date ]
day = [ datetime.strftime(x, "%d") for x in date ]

#save the data in files
file_name = fname.split('.csv')[0]+'_sm.csv'
print(file_name)

tt = [year,month,day,it]
table = list(zip(*tt))

with open(file_name, 'wb') as f:
    #header
    f.write(b'year,month,day,ice thickness (m)\n')
    np.savetxt(f, table, fmt="%s", delimiter=",")
 




