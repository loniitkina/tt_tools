import numpy as np
from glob import glob
import os
from datetime import datetime, timedelta
from tt_func import *

#remove old data by:
#rm ../data/MCS/MP/*-PS122-4_*/magnaprobe-transect-*_PS122-4_*_*-track.csv


leg = 0 #use zero for Nansen Legacy
ext = '.dat'

#MOSAiC
path = '../data/MCS/MP/'
#NansenLegacy
path = '../data/NansenLegacy/'

flist = sorted(glob(path+'/**/magnaprobe-*'+ext))
print(flist)



for i in flist:
    #open data file
    fname = i
    print(fname)

    lat1 = getColumn(fname,5, delimiter=',', magnaprobe=True)
    lat2 = getColumn(fname,14, delimiter=',', magnaprobe=True)

    lon1 = getColumn(fname,7, delimiter=',', magnaprobe=True)
    lon2 = getColumn(fname,15, delimiter=',', magnaprobe=True)

    date = getColumn(fname,0, delimiter=',', magnaprobe=True)
        
    dc = [ date[x].split('.')[0] for x in range(len(date)) ]                        #get rid of the annoyting milliseconds
    
    if leg<4 or i.split('_')[-1]=='raw.dat' or \
    i=='../data/MCS/MP/20200721-PS122-4_48-275/magnaprobe-transect-20200721_PS122-4_48-275_ridge.dat' or \
    i=='../data/MCS/MP/20200824-PS122-5_59-256/magnaprobe-transect-20200824_PS122-5_59-256_transect.dat' or \
    i=='../data/MCS/MP/20200910-PS122-5_61-216/magnaprobe-transect-20200910_PS122-5_61-216_ARIEL.dat' or \
    i=='../data/MCS/MP/20200910-PS122-5_61-216/magnaprobe-transect-20200910_PS122-5_61-216_kuka.dat' or \
    i=='../data/MCS/MP/20200910-PS122-5_61-216/magnaprobe-transect-20200910_PS122-5_61-216_transect.dat' or \
    i=='../data/MCS/MP/20200910-PS122-5_61-217/magnaprobe-transect-20200910_PS122-5_61-217_transectport.dat' or \
    i=='../data/MCS/MP/20200914-PS122-5_62-17/magnaprobe-transect-20200914_PS122-5_62-17_ARIEL.dat' or \
    i=='../data/MCS/MP/20200914-PS122-5_62-17/magnaprobe-transect-20200914_PS122-5_62-17_kuka.dat'  or \
    i=='../data/MCS/MP/20200917-PS122-5_62-239/magnaprobe-transect-20200917_PS122-5_62-239_ARIEL.dat' or \
    i=='../data/MCS/MP/20200919-PS122-5_62-244/magnaprobe-transect-20200919_PS122-5_62-244_transect.dat'    :
        dt = [ datetime.strptime(dc[x], "%Y-%m-%d %H:%M:%S") for x in range(len(dc)) ]  #"2020-02-20 10:43:44"
        dt64 = np.array(dt, dtype='datetime64[s]')
        
    else:    
        dt = [ datetime.strptime(dc[x], "%m/%d/%Y %H:%M:%S") for x in range(len(dc)) ]  #'6/17/2020 12:51:31 AM'
        dt64 = np.array(dt, dtype='datetime64[s]')
        
        #AM/PM
        dc2 =  [ date[x].split(' ')[-1] for x in range(len(date)) ]
        dc2 = np.array(dc2)
        add12 = np.timedelta64(12, 'h')
        
        noon = [ x.hour for x in dt ]
        noon = np.array(noon)
        #print(noon)
        mask = (noon!=12) & (dc2=='PM')

        dt64 = np.where(mask,dt64+add12,dt64)
    
    #time on many AWI magnaprobes not UTC! (Anja is OK)
    name = fname.split('/')[-1].split('_')[0]
    print(name)
    date = dt[0].strftime('%Y%m%d')
    print(date)
    #Kathrin is UTC-6h
    if date == '20191222' or date == '20191219' or date == '20191226':    #some dates at the start of leg 2
        dt64 = dt64 + np.timedelta64(6, 'h')
    if leg == 1:
        dt64 = dt64 + np.timedelta64(6, 'h')                              #Katrin was used always on leg 1
    #BRUCE is very wierd    
    if date == '20000522' or date == '20000523':    #FYI dark side transect
        bruce = datetime(2000,5,23,7,51,23) #2000-05-23 07:51:24.25
        cynthia = datetime(2020,1,7,7,53,36) #2020-01-07T07:53:36.453125
        diff = cynthia-bruce
        diff = int(diff.total_seconds())         #this is approximate and will require additional displacement in space
        
        #diff2 = (cynthia-bruce).days
        dt64 = dt64 + np.timedelta64(diff, 's')
        dt[0] = dt[0] + timedelta(seconds=diff) #to get the name right
        print(dt[0])
        
        lat2 = getColumn(fname,13, delimiter=',', magnaprobe=True)
        lon2 = getColumn(fname,14, delimiter=',', magnaprobe=True)
    #Glen's Magnaprobe is in Alaska Standard time (UTC-9)
    if leg==0:
        dt64 = dt64 + np.timedelta64(9, 'h')
    
    lat1 = np.array(lat1,dtype=np.float)
    lat2 = np.array(lat2,dtype=np.float)
    lat = lat1+lat2
    
    lon1 = np.array(lon1,dtype=np.float)
    lon2 = np.array(lon2,dtype=np.float)
    lon = lon1+lon2    

    #rename all files by convention suggested by Stefan: magnaprobe-transect-20191114-PS122-1_7-62.dat
    #for leg 1 this was already done. Polona has manually split into raw and loop files
    #keep original files as: magnaprobe-transect-20191114-PS122-1_7-62_raw.dat
    #also keep all extra location information in the file name in: magnaprobe-transect-20191114-PS122-1_7-62_Nloop
    #in the manual overlay (tt_track_overlay.py) individual locaitons sometimes require differnet shifts
    #valid locations are:
    #leg 2: Nloop, Sloop, snow1, runway, special, ridgeFR1 (installation), ridgeFR2 (coring), ridgeFR3 (optics), ridgeA1 (center), ridgeA2 (N), ridgeA3 (S)
    #leg 3: Nloop, Sloop, snow1, ridgeFR1 (installation), ridgeA1 (center), ridgeA2 (N), ridgeA3 (S), ridgeD (davids), ridgeE (eco), special
    #for leg1:
    if (leg > 1) and (leg < 4):
        location = fname.split('_')[-1].split('.dat')[0]
        try:
            int(location); end = '_raw.dat'
        except:
            end = '_'+location+'.dat' 
        fname_path = fname.split('/')[0]+'/'+fname.split('/')[1]+'/'+fname.split('/')[2]+'/'+fname.split('/')[3]+'/'+fname.split('/')[4]+'/'
        date = dt[0].strftime('%Y%m%d')
        activity = fname.split('/')[4]
        new_fname = fname_path+'magnaprobe-transect-'+date+'_'+activity+end
        print(fname)
        print(new_fname)
        os.rename(fname,fname_path+'magnaprobe-transect-'+date+'_'+activity+end)
        fname = new_fname
        #continue


    #write new csv file with time and coordinates only
    tt = [dt64,lon,lat]
    table = list(zip(*tt))

    outname = fname.split(ext)[0]+'-track.csv'
    print(outname)
    with open(outname, 'wb') as f:
        np.savetxt(f, table, fmt="%s", delimiter=",")


#then convert coordinates by:
#cd ../../coord_trans/psref-gps2xy/
#python psref_gps2xy.py ../../transect/data/MCS/MP/PS122-1_4-1/magnaprobe-transect-20191024-PS122-1_4-1_Nloop-track.csv ../dshipextracts/transect_legs/position_leg1.dat
#or using the list in psref_gps2xy.sh

#gem-2 converts by
#python psref_gps2xy.py ../../../MOSAiC/thickness_workspace/01-ice-thickness/20191219_PS122-2_16-48/mosaic-transect-20191219-gem2-556-track.csv ../dshipextracts/polarstern-ref-20191101to20200222.dat.txt
