import csv
import re
import numpy as np
from tt_func import getColumn, linreg_model
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

inpath='../data/SnowModel/'
outpath='../plots_sm/'

#MODEL

fname = inpath+'sden_snod_swed_from_swe_and_den_assim.dat'
print(fname)

results = csv.reader(open(fname))
#get rid of all multi-white spaces and split in those that remain
results_clean = [re.sub(" +", " ",row[0]) for row in results]

#snow density
sden = [row.split(" ")[2] for row in results_clean]
sden = np.array(sden,dtype=np.float)     
sden = np.ma.array(sden,mask=sden==-9999)

#snow density
snod = [row.split(" ")[3] for row in results_clean]
snod = np.array(snod,dtype=np.float)     
snod = np.ma.array(snod,mask=snod==-9999)/100

#SWE
swe = [row.split(" ")[4] for row in results_clean]
swe = np.array(swe,dtype=np.float)     
swe = np.ma.array(swe,mask=swe==-9999)/100

#dates
numdays=366*8
start = datetime(2019,8,1)
dt = [start + timedelta(hours=x*3) for x in range(numdays)]
end = datetime(2020,8,1)

#OBSERVATIONS
fname = '../data/MCS/MP/SnowModel_Sloop_level_swe.csv'
print(fname)

#snow depth
snod_o = getColumn(fname,3, delimiter=',')
snod_o = np.array(snod_o,dtype=np.float)     

snod_o_std = getColumn(fname,4, delimiter=',')
snod_o_std = np.array(snod_o_std,dtype=np.float)     

#snow density
sden_o = getColumn(fname,-2, delimiter=',')
sden_o = np.array(sden_o,dtype=np.float)     


#SWE 
swe_o = getColumn(fname,-1, delimiter=',')
swe_o = np.array(swe_o,dtype=np.float)  


#observation dates
year = np.array(getColumn(fname,0),dtype=int)
month = np.array(getColumn(fname,1),dtype=int)
day = np.array(getColumn(fname,2),dtype=int)
dt_o = [ datetime(year[x],month[x],day[x]) for x in range(0,len(year)) ]

#extract model data for the observations dates
snod_o_m=[]
sden_o_m=[]
swe_o_m=[]

for i in range(0,len(dt_o)):
    argmin = np.argmin(np.abs([ dt_o[i]-x for x in dt]) )+1 #add one as assimilation only gets effect in the next step
    snod_o_m.append(snod[argmin])
    sden_o_m.append(sden[argmin])
    swe_o_m.append(swe[argmin])
    
#Plotting the time series and scatter plots
fig1, ax = plt.subplots(3, 2,gridspec_kw={'width_ratios': [1,.5]},figsize=(10,10))

#Time series
ax[0,0].set_ylabel('SWE (m)', fontsize=15)
ax[0,0].tick_params(axis="x", labelsize=12)
ax[0,0].tick_params(axis="y", labelsize=12)
ax[0,0].set_xlim(start,end)

ax[0,0].plot(dt,swe,c='k')
ax[0,0].scatter(dt_o,swe_o, marker='o',c='purple',alpha=.5,s=150)

ax[1,0].set_ylabel('Snow density (kg/m$^3$)', fontsize=15)
ax[1,0].tick_params(axis="x", labelsize=12)
ax[1,0].tick_params(axis="y", labelsize=12)
ax[1,0].set_xlim(start,end)

ax[1,0].plot(dt,sden,c='k')
ax[1,0].scatter(dt_o,sden_o, marker='o',c='purple',alpha=.5,s=150)

ax[2,0].set_ylabel('Snow depth (m)', fontsize=15)
ax[2,0].tick_params(axis="x", labelsize=12)
ax[2,0].tick_params(axis="y", labelsize=12)
ax[2,0].set_xlim(start,end)

ax[2,0].plot(dt,snod,c='k')
ax[2,0].errorbar(dt_o,snod_o, snod_o_std, linestyle='None', marker='o',c='purple',alpha=.5,ms=14)

#Scatter plots
ax[0,1].scatter(swe_o,swe_o_m, marker='o',c='purple',alpha=.5,s=150)
x_lin_reg, y_lin_reg, n, r2 = linreg_model(swe_o,swe_o_m)
ax[0,1].text(.1,.9,'n = %i'%(n),transform=ax[0,1].transAxes )
ax[0,1].text(.1,.8,'R$^2$ = %0.2f'%(r2),transform=ax[0,1].transAxes )
ax[0,1].plot(x_lin_reg, y_lin_reg, c='k')
ax[0,1].set_xlim(0,.1)
ax[0,1].set_ylim(0,.1)

ax[1,1].scatter(sden_o,sden_o_m, marker='o',c='purple',alpha=.5,s=150)
x_lin_reg, y_lin_reg, n, r2 = linreg_model(sden_o,sden_o_m)
ax[1,1].text(.1,.9,'n = %i'%(n),transform=ax[1,1].transAxes )
ax[1,1].text(.1,.8,'R$^2$ = %0.2f'%(r2),transform=ax[1,1].transAxes )
ax[1,1].plot(x_lin_reg, y_lin_reg, c='k')
ax[1,1].set_xlim(200,400)
ax[1,1].set_ylim(200,400)

ax[2,1].scatter(snod_o,snod_o_m, marker='o',c='purple',alpha=.5,s=150)
x_lin_reg, y_lin_reg, n, r2 = linreg_model(snod_o,snod_o_m)
ax[2,1].text(.1,.9,'n = %i'%(n),transform=ax[2,1].transAxes )
ax[2,1].text(.1,.8,'R$^2$ = %0.2f'%(r2),transform=ax[2,1].transAxes )
ax[2,1].plot(x_lin_reg, y_lin_reg, c='k')
ax[2,1].set_xlim(0,.2)
ax[2,1].set_ylim(0,.2)



#plt.show()
fig1.savefig(outpath+'sm_assim.png',bbox_inches='tight')
