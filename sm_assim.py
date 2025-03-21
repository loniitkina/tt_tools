import csv
import re
import numpy as np
from tt_func import getColumn, linreg_model
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from scipy.stats import linregress

outpath='../plots_sm/'

inpath='../data/SnowModel/final/'
loc = 'Nloop'
loc = 'Sloop'
loc = 'Runwy'
melt_limit = 2248
name_date='2024_05_15'
fname = inpath+'snow_tice_'+loc+'_'+name_date+'_normal.dat'
print(fname)

results = csv.reader(open(fname))
#get rid of all multi-white spaces and split in those that remain
results_clean = [re.sub(" +", " ",row[0]) for row in results]

#HEADER
#iter,swed_mod1,swed_mod2,snod,sden,dyn_corr,tice,swed_obs,sden_obs,snod_obs,timo_obs

#MODEL
#SWE
swe = [row.split(" ")[3] for row in results_clean]
swe = np.array(swe,dtype=np.float)     
swe = np.ma.array(swe,mask=swe==-9999)

#snow density
sden = [row.split(" ")[5] for row in results_clean]
sden = np.array(sden,dtype=np.float)     
sden = np.ma.array(sden,mask=sden==-9999)

#snow depth
snod = [row.split(" ")[4] for row in results_clean]
snod = np.array(snod,dtype=np.float)     
snod = np.ma.array(snod,mask=snod==-9999)

#OBSERVATIONS
#SWE - obs
swe_o = [row.split(" ")[8] for row in results_clean]
swe_o = np.array(swe_o,dtype=np.float)     
mask_o = swe_o==-9999
swe_o = np.ma.array(swe_o,mask=swe_o==-9999)

#snow density - obs
sden_o = [row.split(" ")[9] for row in results_clean]
sden_o = np.array(sden_o,dtype=np.float)     
sden_o = np.ma.array(sden_o,mask=sden_o==-9999)

#snow depth - obs
snod_o = [row.split(" ")[10] for row in results_clean]
snod_o = np.array(snod_o,dtype=np.float)     
snod_o = np.ma.array(snod_o,mask=snod_o==-9999)

#extract model data for the observations dates
snod_o_m = np.ma.array(snod,mask=mask_o)
sden_o_m = np.ma.array(sden,mask=mask_o)
swe_o_m = np.ma.array(swe,mask=mask_o)

#dates
numdays=366*8
start = datetime(2019,8,1)
dt = [start + timedelta(hours=x*3) for x in range(numdays)]
end = datetime(2020,8,1)

#Plotting the time series and scatter plots
fig1, ax = plt.subplots(3, 2,gridspec_kw={'width_ratios': [1,.5]},figsize=(10,10))

#Time series
ax[0,0].set_ylabel('SWE (m)', fontsize=15)
ax[0,0].text(.05,.9,'a',transform=ax[0,0].transAxes, ha="center", va="center", size=20)
ax[0,0].tick_params(axis="x", labelsize=12)
ax[0,0].tick_params(axis="y", labelsize=12)
ax[0,0].set_xlim(start,end)

ax[0,0].plot(dt,swe,c='k')
ax[0,0].scatter(dt[:melt_limit],swe_o[:melt_limit], marker='o',c='purple',alpha=.5,s=150)
ax[0,0].scatter(dt[melt_limit:],swe_o[melt_limit:], marker='o',c='grey',alpha=.5,s=150)

ax[1,0].set_ylabel('Snow density (kg/m$^3$)', fontsize=15)
ax[1,0].text(.05,.9,'b',transform=ax[1,0].transAxes, ha="center", va="center", size=20)
ax[1,0].tick_params(axis="x", labelsize=12)
ax[1,0].tick_params(axis="y", labelsize=12)
ax[1,0].set_xlim(start,end)

ax[1,0].plot(dt,sden,c='k')
ax[1,0].scatter(dt[:melt_limit],sden_o[:melt_limit], marker='o',c='purple',alpha=.5,s=150)
ax[1,0].scatter(dt[melt_limit:],sden_o[melt_limit:], marker='o',c='grey',alpha=.5,s=150)

ax[2,0].set_ylabel('Snow depth (m)', fontsize=15)
ax[2,0].text(.05,.9,'c',transform=ax[2,0].transAxes, ha="center", va="center", size=20)
ax[2,0].tick_params(axis="x", labelsize=12)
ax[2,0].tick_params(axis="y", labelsize=12)
ax[2,0].set_xlim(start,end)

ax[2,0].plot(dt,snod,c='k')
ax[2,0].scatter(dt[:melt_limit],snod_o[:melt_limit], marker='o',c='purple',alpha=.5,s=150)
ax[2,0].scatter(dt[melt_limit:],snod_o[melt_limit:], marker='o',c='grey',alpha=.5,s=150)

#Scatter plots
ax[0,1].scatter(swe_o[:melt_limit],swe_o_m[:melt_limit], marker='o',c='purple',alpha=.5,s=150)
ax[0,1].scatter(swe_o[melt_limit:],swe_o_m[melt_limit:], marker='o',c='grey',alpha=.5,s=150)

x_lin_reg, y_lin_reg, n, r2 = linreg_model(swe_o.compressed(),swe_o_m.compressed())
ax[0,1].text(.1,.8,'R$^2$ = %0.2f'%(r2),transform=ax[0,1].transAxes, size=12)
ax[0,1].text(.1,.9,'N = %i'%(n),transform=ax[0,1].transAxes, size=12)
ax[0,1].plot(x_lin_reg, y_lin_reg, c='k')

x_lin_reg, y_lin_reg, n, r2 = linreg_model(swe_o[melt_limit:].compressed(),swe_o_m[melt_limit:].compressed())
ax[0,1].text(.1,.6,'R$^2$ = %0.2f'%(r2),transform=ax[0,1].transAxes, size=12,c='grey')
ax[0,1].text(.1,.7,'N = %i'%(n),transform=ax[0,1].transAxes, size=12,c='grey')
x=swe_o[melt_limit:].compressed(); y=swe_o_m[melt_limit:].compressed()
slope,intercept,rvalue,pvalue,stderr=linregress(x,y)
#p-value : two-sided p-value for a hypothesis test whose null hypothesis is that the slope is zero
if pvalue < 0.01:   #significant at 99%
    print('significant!')

ax[0,1].set_xlim(0,.15)
ax[0,1].set_ylim(0,.15)
ax[0,1].tick_params(axis="x", labelsize=12)
ax[0,1].tick_params(axis="y", labelsize=12)

ax[1,1].scatter(sden_o[:melt_limit],sden_o_m[:melt_limit], marker='o',c='purple',alpha=.5,s=150)
ax[1,1].scatter(sden_o[melt_limit:],sden_o_m[melt_limit:], marker='o',c='grey',alpha=.5,s=150)

x_lin_reg, y_lin_reg, n, r2 = linreg_model(sden_o.compressed(),sden_o_m.compressed())
ax[1,1].text(.1,.8,'R$^2$ = %0.2f'%(r2),transform=ax[1,1].transAxes, size=12)
ax[1,1].text(.1,.9,'N = %i'%(n),transform=ax[1,1].transAxes, size=12)
ax[1,1].plot(x_lin_reg, y_lin_reg, c='k')

ax[1,1].set_xlim(200,570)
ax[1,1].set_ylim(200,570)
ax[1,1].tick_params(axis="x", labelsize=12)
ax[1,1].tick_params(axis="y", labelsize=12)

ax[2,1].scatter(snod_o[:melt_limit],snod_o_m[:melt_limit], marker='o',c='purple',alpha=.5,s=150)
ax[2,1].scatter(snod_o[melt_limit:],snod_o_m[melt_limit:], marker='o',c='grey',alpha=.5,s=150)

x_lin_reg, y_lin_reg, n, r2 = linreg_model(snod_o.compressed(),snod_o_m.compressed())
ax[2,1].text(.1,.8,'R$^2$ = %0.2f'%(r2),transform=ax[2,1].transAxes, size=12)
ax[2,1].text(.1,.9,'N = %i'%(n),transform=ax[2,1].transAxes, size=12)
ax[2,1].plot(x_lin_reg, y_lin_reg, c='k')

x_lin_reg, y_lin_reg, n, r2 = linreg_model(snod_o[melt_limit:].compressed(),snod_o_m[melt_limit:].compressed())
ax[2,1].text(.1,.6,'R$^2$ = %0.2f'%(r2),transform=ax[2,1].transAxes, size=12,c='grey')
ax[2,1].text(.1,.7,'N = %i'%(n),transform=ax[2,1].transAxes, size=12,c='grey')
x=snod_o[melt_limit:].compressed(); y=snod_o_m[melt_limit:].compressed()
slope,intercept,rvalue,pvalue,stderr=linregress(x,y)
#p-value : two-sided p-value for a hypothesis test whose null hypothesis is that the slope is zero
if pvalue < 0.01:   #significant at 99%
    print('significant!')

ax[2,1].set_xlim(0,.4)
ax[2,1].set_ylim(0,.4)
ax[2,1].tick_params(axis="x", labelsize=12)
ax[2,1].tick_params(axis="y", labelsize=12)

#fig1.autofmt_xdate()
plt.show()
fig1.savefig(outpath+'sm_assim'+loc+'.png',bbox_inches='tight')
