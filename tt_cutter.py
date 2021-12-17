import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from datetime import datetime
from glob import glob
from tt_func import getColumn, floenavi_coords

outpath='../plots_gridded/'

#snow pits
fpit = '../data/snowpits_wagner/swe_smpdensity_leg1_leg3_archive/cutter/metadata_DensityCutter_removedOvalues.csv'
#header: Device_Operation_ID,Location,Lat,Lon,Timestamp,From snow height (cm),To snow height (cm),'Snow weight (cutter, g)','Snow density (cutter, kg/m3)',Salinity,Sensor cutter,Sensor scale,Comment
doid = np.array(getColumn(fpit,0))
location = np.array(getColumn(fpit,1))
lat = getColumn(fpit,2)
lat = np.array(lat,dtype=np.float)
lon = getColumn(fpit,3)
lon = np.array(lon,dtype=np.float)
date = getColumn(fpit,4)
dt = [ datetime.strptime(date[x], "%m/%d/%Y %H:%M:%S") for x in range(len(date)) ]
h_start = np.array(getColumn(fpit,5))
h_end = np.array(getColumn(fpit,6))
rho = np.array(getColumn(fpit,8))

#get all floenavi master station records
refdate=[]
reflon=[]
reflat=[]
refhead=[]
refstat_files = sorted(glob('../data/floenavi/data_master-solution_mosaic-leg*-floenavi-refstat-v1p0.csv'))
for refstat in refstat_files:
    print(refstat)
    
    refdate.extend(getColumn(refstat,0))
    reflon.extend(getColumn(refstat,1))
    reflat.extend(getColumn(refstat,2))
    refhead.extend(getColumn(refstat,3))
    
refdt = [ datetime.strptime(refdate[x], "%Y-%m-%d %H:%M:%S") for x in range(len(refdate)) ]
reflon = np.array(reflon,dtype=np.float)
reflat = np.array(reflat,dtype=np.float)
refhead = np.array(refhead,dtype=np.float)

#group snowpits by location
snowpits = list(set(doid))

for i in range(0,len(snowpits)):
    print(snowpits[i])
    
    pit = np.ma.array(doid,mask=doid!=snowpits[i])
    loc_pit = np.ma.array(location,mask=pit.mask).compressed()
    h_start_pit = np.ma.array(h_start,mask=pit.mask).compressed()
    h_end_pit = np.ma.array(h_end,mask=pit.mask).compressed()
    rho_pit = np.ma.array(rho,mask=pit.mask).compressed()
    
    date_pit = np.ma.array(dt,mask=pit.mask).compressed()
    lat_pit = np.ma.array(lat,mask=pit.mask).compressed()
    lon_pit = np.ma.array(lon,mask=pit.mask).compressed()
    
    pit = pit.compressed()
    
    ##calculate bulk density: SWE = (rho_s/rho_w) * h_s
    #rho_w = 1000
    #rho_s = ((swe_pit/1000)/snod_pit)*rho_w   
    
    #calculate the local coordinates
    x_pit,y_pit = floenavi_coords(date_pit,lat_pit,lon_pit,refdt,reflat,reflon,refhead)
    
    #simplify diod,date,loc
    pit = pit[0]
    date = datetime.strftime(date_pit[0], "%Y%m%d")
    loc = loc_pit[0]
    
    
    #save the locations to individual files
    file_pit = fpit.split('metadata')[0]+'cutter_'+date+'_'+loc+'_'+pit+'.csv'
    print(file_pit)
    
    tt = [lat_pit,lon_pit,x_pit,y_pit,h_start_pit,h_end_pit,rho_pit]
    table = list(zip(*tt))

    with open(file_pit, 'wb') as f:
        #header
        f.write(b'lat,lon,x,y,h_start,h_end,rho\n')
        np.savetxt(f, table, fmt="%s", delimiter=",")

    
    
    
    
    




    
#ax.plot(rot_x,rot_y,'x',ms=5,c='r')
