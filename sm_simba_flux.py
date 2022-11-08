import numpy as np
from datetime import datetime
import pandas as pd
from tt_func import getColumn, smooth
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#get sea ice thickness from PANGAEA - Ruibo

#use all CO and M-site data

#use just conductive heat flux bellow the ice-ocean interface, calculate the latent heat from ice growth in the HIGTSI

outpath_data = '../data/IMB_Lei_PANGAEA/'
outpath='../plots_sm/'

#FYI coring site
fname='../data/IMB_Lei_PANGAEA/2019T62/datasets/2019T62_temp.tab'
fname_rl = '../data/IMB_Lei_PANGAEA/MOSAiC_SIMBA_snow_depth_ice_thickness/datasets/2019T62_snow_depth_ice_thickness.tab'
sii=50    #initial ice-snow interface
ioi=80  #initial ice-ocean interface
skipstart=0 #throw away the hole refreezing period
maxjump=7
cr1 = -1.9375  	#value of the reference isotherm (freezing conditions) - formation stage
cr2 = -1.8375   #melting stage (both are empirical values, only some steps appart in the sensor resolution)

##SYI coring site
#fname='../data/IMB_Lei_PANGAEA/2019T66/datasets/2019T66_temp.tab'
#fname_rl = '../data/IMB_Lei_PANGAEA/MOSAiC_SIMBA_snow_depth_ice_thickness/datasets/2019T66_snow_depth_ice_thickness.tab'
#sii=50    #initial ice-snow interface
#ioi=70 #initial ice-ocean interface
#skipstart=0
#maxjump=10
#cr1 = -1.9375  	#value of the reference isotherm (freezing conditions) - formation stage
#cr2 = -1.8750	#melting stage (both are empirical values, only 1 step appart in the sensor resolution)

##2km SW from PS
#fname='../data/IMB_Lei_PANGAEA/2019T56/datasets/2019T56_temp.tab'
#fname_rl = '../data/IMB_Lei_PANGAEA/MOSAiC_SIMBA_snow_depth_ice_thickness/datasets/2019T56_snow_depth_ice_thickness.tab'
#sii=40    #initial ice-snow interface


##M-site buoys: 58, 64, 68, 69, 72
#fname='../data/IMB_Lei_PANGAEA/2019T58/datasets/2019T58_temp.tab'
#fname_rl = '../data/IMB_Lei_PANGAEA/MOSAiC_SIMBA_snow_depth_ice_thickness/datasets/2019T58_snow_depth_ice_thickness.tab'
#sii=30    #initial ice-snow interface

#fname='../data/IMB_Lei_PANGAEA/2019T64/datasets/2019T64_temp.tab'
#fname_rl = '../data/IMB_Lei_PANGAEA/MOSAiC_SIMBA_snow_depth_ice_thickness/datasets/2019T64_snow_depth_ice_thickness.tab'
#sii=40    #initial ice-snow interface

#fname='../data/IMB_Lei_PANGAEA/2019T68/datasets/2019T68_temp.tab'
#fname_rl = '../data/IMB_Lei_PANGAEA/MOSAiC_SIMBA_snow_depth_ice_thickness/datasets/2019T68_snow_depth_ice_thickness.tab'
#sii=45    #initial ice-snow interface

#fname='../data/IMB_Lei_PANGAEA/2019T69/datasets/2019T69_temp.tab'
#fname_rl = '../data/IMB_Lei_PANGAEA/MOSAiC_SIMBA_snow_depth_ice_thickness/datasets/2019T69_snow_depth_ice_thickness.tab'
#sii=45    #initial ice-snow interface

#fname='../data/IMB_Lei_PANGAEA/2019T72/datasets/2019T72_temp.tab'
#fname_rl = '../data/IMB_Lei_PANGAEA/MOSAiC_SIMBA_snow_depth_ice_thickness/datasets/2019T72_snow_depth_ice_thickness.tab'
#sii=35    #initial ice-snow interface

buoy_name=fname.split('/')[-1].split('_')[0]
print(buoy_name)

melt=datetime(2020,6,1)


#2019-10-29T14:30:00
if fname=='../data/IMB_Lei_PANGAEA/2019T58/datasets/2019T58_temp.tab':
    dates = getColumn(fname,0,skipheader=268, delimiter='\t')[skipstart:]; dt = [ datetime.strptime(x, '%Y-%m-%dT%H:%M') for x in dates ]
else:
    dates = getColumn(fname,0,skipheader=268, delimiter='\t')[skipstart:]; dt = [ datetime.strptime(x, '%Y-%m-%dT%H:%M:%S') for x in dates ]
#lat = getColumn(fname,1,skipheader=268, delimiter='\t')[skipstart:]
#lon = getColumn(fname,2,skipheader=268, delimiter='\t')[skipstart:]

recn=240
tc=np.empty([len(dt),recn])
print(tc.shape)


for tn in range(0,recn):
    tt = getColumn(fname,4+tn,skipheader=268, delimiter='\t')[skipstart:];tt=np.array(tt); tt[tt == ''] = -999#np.nan
    tt = np.array(tt,dtype=np.float)
    
    tc[:,tn]=tt

#plt.imshow(tc.T,vmin=-30,vmax=0)
#plt.show()

#searching for interfaces#################################################################################################3
y = np.arange(0,tc.shape[1])

#ICE-OCEAN INTERFACE
tf = -1.8821	#freezing temperature
#cr1 = -1.9375  	#value of the reference isotherm (freezing conditions) - formation stage
#cr2 = -1.8750	#melting stage (both are empirical values, only 1 step appart in the sensor resolution)
#cr2 = -1.8375
#cr1 = -1.8750
h_oc_ice = [ioi]
for i in range(1,tc.shape[0]):			#for every profile
    #check the date (melt onset) to decide which reference isotherm to use
    if dt[i] < melt:   
      idx = np.argmax(tc[i,90:]>=cr1)+90
    else:
      idx = np.argmax(tc[i,90:]>=cr2)+90
    #smoothing (finding the intersection of freezing temperature and the linear fit through the the sea ice temperature profile)
    #take 7 points above the index from the previous step
    fit = np.polyfit(y[idx-7:idx],tc[i,idx-7:idx],1)
    
    #filter out high jumps
    inter = (tf-fit[1])/fit[0]
    if np.abs(inter-h_oc_ice[-1]) > maxjump:
      print('high jump')
      h_oc_ice.append(h_oc_ice[-1])
    else:
      h_oc_ice.append(inter)

#print(h_oc_ice)

#if the jump is unrealistic (due to bad data that cant be filtered automatically): interpolate
#smoothing window (4=24h)
swin=6
h_oc_ice = np.array(h_oc_ice)
op = np.zeros_like(h_oc_ice)
oa = np.zeros_like(h_oc_ice)
#compare between 1 step before and 3 later (for large windows with errors)
op[1:] = h_oc_ice[:-1]
oa[:-3] = h_oc_ice[3:]
diff1 = np.abs(op-h_oc_ice)
diff2 = np.abs(oa-op)
mask = diff2<diff1
h_oc_ice[mask] = (op[mask]+oa[mask])/2.
#plt.plot(date_tc,h_oc_ice)

h_oc_ice = smooth(h_oc_ice,swin,window='flat')

#interfaces derived by Ruibo
dates = getColumn(fname_rl,0,skipheader=27, delimiter='\t'); dt_rl = [ datetime.strptime(x, '%Y-%m-%dT%H:%M') for x in dates ]
h_oc_ice_rl = getColumn(fname_rl,3,skipheader=27, delimiter='\t');h_oc_ice_rl = np.array(h_oc_ice_rl,dtype=np.float)*100/2 #convert to cm and sensor number
h_ice_sn_rl = getColumn(fname_rl,4,skipheader=27, delimiter='\t');h_ice_sn_rl = np.array(h_ice_sn_rl,dtype=np.float)*100/2

#interpolation to the 6-h original data
ts = pd.Series(h_oc_ice_rl, index=dt_rl)
ttmp = pd.Series(h_oc_ice, index=dt)

ts6h = ts.reindex(ttmp.index, method='bfill')
ts6h = ts6h.interpolate()   #get rid of nans

h_oc_ice_rl_6h = ts6h.values
#tmp = ts6h.index
#print(tmp)









##calculating heat fluxes############################################################################3
#h_oc_ice = np.ma.mask_invalid(h_oc_ice)

h_ice_sn_6h = h_oc_ice -20      #dummy interface

#conductive heat fluxes
#vertical temperature gradient
k_sn = .3
tgrad = (tc[:,1:] - tc[:,:-1])*50    #K/2cm >> K/m
#print tgrad
fc = k_sn *tgrad
#mask all but snow
mask = np.ones_like(fc, dtype=bool)
#for i in range(0,fc.shape[0]):
    #mask[i,int(h_sn_air_6h[i]):int(h_ice_sn_6h[i])] = False
#fc_snow = np.ma.array(fc,mask=mask)

#ice
#k_si = 2.03+0.117*S/T
k_si = 1.9
fc = k_si *tgrad
#smooth
for i in range(0,fc.shape[0]):
    fc[i,:] = smooth(fc[i,:],4,window='flat')
#mask all but ice
mask = np.ones_like(fc, dtype=bool)
fco = np.zeros_like(fc[:,0])
for i in range(0,fc.shape[0]):
    mask[i,int(h_ice_sn_6h[i]):int(h_oc_ice_rl_6h[i])] = False
    fco[i] = fc[i,np.int(h_oc_ice_rl_6h[i])+0]  #conductive heat flux 2 sensors above the interface, change sign to match the sign of the latent heat flux (provided by the ocean to melt the ice) #WARNING: changed to AT INTERFACE
fc_ice = np.ma.array(fc,mask=mask)


#ocean heat fluxes
#latent heat flux ~ Fl = rho * Li * growth
rhoi=900        #kg/m3
li = .89*333500     #J/kg    (J=kg*m^2/s^2)
it = (h_oc_ice - sii) *0.02     #ice thickness in m from initial interface (for detecting bottom growth only)
#print it
growth = it[:-1] - it[1:]               #ice growth in m/6h
#print growth
growth = growth /(6*60*60)                #ice growth in m/s
fl = rhoi*li*growth
fl = smooth(fl,8,window='flat')           #smoothing with 2-day running window
fco = smooth(fco,8,window='flat')  
fo = fl+fco[1:]
fo = fco[1:]    #just conductive heat fluxes (latent heat flux should be re-calculated from HIGTSI ice growth)

#also extract the temperature at the interface (to check the departure from freezing point and compare to Katlein et al, 2020)


###########################################################################################################3
#Plotting
fig1 = plt.figure(figsize=(15,15))
ax = fig1.add_subplot(211)
ax.set_ylabel('Thermistor number',fontsize=20)

bx = fig1.add_subplot(212)
bx.set_ylabel('Ocean heat flux (W/m$^2$)',fontsize=20)


x = mdates.date2num(dt)
ax.set_ylim(y[-1],y[0])    #invert the y-axis
im = ax.pcolor(x,y,tc.T, cmap=plt.cm.RdYlBu_r, vmin=-30, vmax=0)
cb = plt.colorbar(im, ax=ax, pad=.01)
cb.set_label(label='Temperature ($^\circ$C)',fontsize=20)
cb.ax.tick_params(labelsize=20)

#plt.plot(dt,h_oc_ice,'w',linewidth=3)
ax.plot(dt_rl,sii+h_oc_ice_rl,'0.5',linewidth=3)
ax.plot(dt_rl,sii-h_ice_sn_rl,'0.5',linewidth=3)


mask=np.abs(fo)>250

bx.plot(np.ma.array(dt[1:],mask=mask).compressed(),np.ma.array(fo,mask=mask).compressed())
bx.plot(dt[1:],np.zeros_like(fo))
plt.show()

fig1.savefig(outpath+'buoy_'+buoy_name+'.png',bbox_inches='tight')

###############################################################################################################3
#store these data
file_name = outpath_data+'Heat_flux'+buoy_name+'.csv'
print(file_name)

tt = [dt[1:],fo]
table = list(zip(*tt))

with open(file_name, 'wb') as f:
    #header
    f.write(b'date,ocean heat flux (W/m2)\n')
    np.savetxt(f, table, fmt="%s", delimiter=",")
