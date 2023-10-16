import numpy as np
from glob import glob
from tt_func import getColumn
from scipy.signal import savgol_filter
from scipy.interpolate import griddata
from datetime import datetime
import matplotlib.pyplot as plt

#grid parameters
step = 2        #grid spacing in meters 
step = 1        #for ridges
#step = 5
limit = step*2  #how far from MP coordinate to search 
#limit = 5       #some equivalent to GEM-2 footprint or max thickness measured by GEM-2?
scale_limit=False   #depending on the MP spatial resolution
#method_gem2 = 'linear'  #GEM-2 data needs to be smoothed >> problem: max distance cant be specified! This method gives strange results
method_gem2 = 'nearest'
method_mp = 'nearest'   #at dense grids every measurement should be used separately

#MP file extension depends on the leg
ext_mp='.dat'
#ext_mp='.csv'

window = 5  #with spacing .2m is this 1m  ~MP spacing
polyorder = 3


#show gridded data plot
show=True
show=False

#make mp+gem2 table output
table_output=True

outpath = '../plots_AGU/'
outpath_grid = '../data/grids_AGU/'

#MP
inpath_snow = '../data/MCS/MP/'

#GEM-2
inpath_ice = '../data/MCS/GEM2_thickness/01-ice-thickness/'

#subset locations
loc1=None

#location
loc = 'Nloop'
#loc1 = 'Nloop_spine'    ##overlap with the leg 4 transect (comment if you want the whole loop!) - this will simply cut a small grid
#date = '20191024'   #quite different track
#date = '20191031'   #quite different track
#date = '20191107'
#date = '20191114'
#date = '20191121'
#date = '20191128'
#date = '20191205'
#date = '20191219'   #a bit of GEM-2 track is missing: chicken tail
#date = '20191226'   #no MP data in the Nloop
#date = '20200102'
#date = '20200109'
#date = '20200116'   #bad GPS data on GEM-2
#date = '20200130'
#date = '20200206'   #very bad GEM-2 data in both loops (unrealistic low values in all f.), 18kHz q looks best and is used instead of ip
#date = '20200220'   #suddenly quite thick
#date = '20200227'
#date = '20200305'
#date = '20200320'   #tiny bits of GEM-2 track are missing, chicken neck
#date = '20200326'   #slightly different shape from here on
#date = '20200403'   #bad GPS track - floenavi problem - fixed by PS position, will need some shifting and rotation in the grid!
##date = '20200416'   #!!!no GPS coordinates from GEM-2/use old track
#date = '20200424'
#date = '20200430'   #
#date = '20200507'  #

dates = ['20191024','20191031','20191107','20191114','20191121','20191128','20191205',]#  '20191219','20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227', '20200305','20200320','20200326','20200403','20200416','20200424','20200430','20200507'] 

#loc = 'Sloop'
#date = '20191031'   #2m spacing!
#date = '20191107'   #3.1m spacing!!!
#date = '20191114'   #2.9m spacing!!!    - no visible snowdunes yet...
#date = '20191205'   #1.8m spacing!
#date = '20191226'   #GEM-2 has only level ice/part of the S loop, ice looks very similar to 1 Jan (~almost 1m thick) - use that GEM-2 data
#date = '20200102'
#date = '20200109'
#date = '20200116'   #bad GPS data on GEM-2 - data from last week used, 1.1m MP spacing
#date = '20200130'   #1.05m MP spacing
#date = '20200206'   #very bad GEM-2 data in both loops (unrealistic low values), 1.06m MP spacing, 63kHz q is used as best estimate
#date = '20200220'   #too thick ice in 18KHz and 93KHz?
#date = '20200227'  
#date = '20200305'   #1.5m spacing!   
#date = '20200330'
#date = '20200406'   #floenavi problem, short cut/parallel track in the parts parallel to the main road due to active crack, unrealistic GEM-2 values-63kHz q is best
#date = '20200426'
#date = '20200507'   #only a part of the loop: from cross-roads and almost to the start

#dates = ['20191031','20191107','20191114','20191205',
#         '20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227',
#         '20200305','20200330','20200406','20200426','20200507']
         
#dates = ['20200507']

#location
#loc = 'snow1'
#date = '20191222'
#date = '20200112'
#date = '20200126'   #just a square (half of transect)
#date = '20200207'
#date = '20200223'   #MP GPS is really off the track and messy! Also only about half of the values (Ian did 2m MP spacing?)
#date = '20200406'  #leg 4 - floenavi problem (measurements are not at the same time, 30min delay), do plots by counting the MP measurements, shape of the track is not recognisable... unrealistic GEM-2 values-63kHz q is best

#dates = ['20191222','20200112','20200126','20200207','20200223','20200406']

#location
#loc = 'runway'
#date = '20200112'
#date = '20200119'    #GEM-2 was not used, use the earlier sea ice data
#date = '20200207'

#dates = ['20200112','20200119','20200207']

#location - ridges
#only for ridges that were surveyed with a pulk: othrwise use script tt_grid_ridge.py
#loc = 'ridgeFR1'    #installation (also very close to snow)
#dates = ['20200305']

#loc = 'ridgeA1'    #
#loc = 'ridgeA2'
#loc = 'ridgeA3'
#dates = ['20200410']

#loc = 'ridgeD'
#date = '20200410'
#date = '20200416'
#date = '20200424'
#date = '20200430'
#date = '20200507'

#loc = 'ridgeE'
#dates = ['20200424']

#loc = 'ridge'  #ridge of leg 5
#dates = ['20200828','20200918']    

#special transects of legs 1-3
#date = '20200107'   #Dark site FYI
#date = '20200115'   #Dark site SYI (pulk tipped once in the ridges)
#date = '20200123'  #long transect (and lead event sampling without GEM-2)
#date = '20200126'  #lead event (different track than on 23 Jan)
#date = '20200226'   #lead scounting at the Dranitsyn lead (that did not work out...)
#date = '20200326'  #leg 3 lead at the Nloop (chicken beak)
#date = '20200403'   #RS site (floenavi problem), no GEM-2 data
#date = '20200430'   #RS site

#special transects of leg 4
#loc='special'
#dates = ['20200617']   # two 'initialsurveys'. One nearly full MP transect. GEM-2 coordinates are messed up (times correspond approximately full to transect part)
#dates = ['20200709']    #meltponds, has no GEM-2 measurements
#dates = ['20200718']    #meltponds, has no GEM-2 measurements
#dates = ['20200719']   #'ARIEL'
#dates = ['20200719']   #'drillholes' MP file has missing data, see notes-column for details

#special transects of leg 5
#dates = ['20200827','20200903','20200910'] #'transectport' (August transect has negative values, last transect has a bit different track shape)
#dates = ['20200902']   #'transectstbd'
#dates = ['20200909']   #'transectbow'
#dates = ['20200919']   #'transectgrid' aka RS site

#all special transects
#loc='special'
#dates = ['20200107','20200115','20200123','20200226','20200326','20200430','20200617','20200719','20200719','20200827','20200903','20200910','20200902','20200909','20200919']

#loc = 'recon'   #has no MP data
#dates = ['20200108']; inpath_ice = '../data/MCS/GEM2_thickness/09-ridges-recal/'   #road to Fort Ridge
#dates = ['20200228']   #airport recon
#dates = ['20200226']   #Darnitsyn Lead
#dates = ['20200107']   #Dark site FYI
#dates = ['20200126']   #lead Event
#table_output=True  #not useful
#step=5
#limit = step*2            #no need to search far

#leg4
#loc = 'transect'
#date = '20200617'  #initial survey - MP track looks good and similar to transect, GEM-2 coordinates are messed up.
#date = '20200627'  #only part
#date = '20200628'  #tiny bit og GEM-2, same part of MP as day before
#date = '20200629'  #MP entire, GEM-2 majority
#date = '20200630'  #complete data!
#date = '20200702'
#date = '20200703'
#date = '20200704'
#date = '20200705'  #decent spacing, 2m
#date = '20200706'
#date = '20200707'
#date = '20200708'
#date = '20200710'  #1.8m spacing!
#date = '20200713'
#date = '20200714'
#date = '20200716'  #done with Kathrin, still not processed!, strange GEM-2 data - looks like strong drift
#date = '20200717'
#date = '20200719'  #little GEM-2 data
#date = '20200720'  #part of GEM-2 missing (little bit), but best spacing so far! 1.5m
#date = '20200721'  #1.3 m spacing! most of GEM-2 track is missing
#date = '20200723'  #strange shape
#date = '20200725'  #first good after a while...
#date = '20200726'  #
#date = '20200727'  #partial (and likely wrong direction)
#dates = ['20200627','20200628','20200629','20200630','20200702','20200703','20200704','20200705','20200706','20200707','20200708','20200710','20200713','20200714','20200716','20200719','20200720','20200721','20200723','20200725','20200726','20200727']
#most useful selection
#dates = ['20200717','20200627','20200629','20200630','20200702','20200703','20200704','20200705','20200706','20200707','20200708','20200710','20200713','20200714','20200719','20200720','20200721','20200723','20200725','20200726','20200727']

##short transects of leg 4 and 5
#loc = 'albedoLD'
#dates = ['20200630','20200706','20200707','20200719','20200721','20200724','20200727']
#dates = ['20200707']

#loc = 'albedoRBB'
#dates = ['20200714','20200717','20200630','20200706','20200707','20200719','20200727']

#loc = 'transect'    #Kinder grid
#loc='albedoK'
#date = '20200824'  #includes an extra loop over the ponded area and ridge on the SB side of the ship (i.e. first survey/initial floe survey including MP)
#date = '20200830'  #l:685m, 1.6m
#date = '20200903'  #l:495m, 2.1m (just 230 measurements...)
#date = '20200907'  #l:485m, 2.1m (just 229 measurements...)
#date = '20200910'
#date = '20200918'  #l:493m, 1.7m
#dates = ['20200824','20200830','20200903','20200907','20200910','20200918']

#loc = 'ARIEL'
#dates = '20200914' # no GEM-2 measurements
#dates = ['20200830','20200903','20200907','20200910','20200917']

#loc = 'kuka'
#dates = '20200914' # no GEM-2 measurements
#dates = ['20200907','20200910','20200917']

##Nansen Legacy
#outpath = '../plots_NL/'
#outpath_grid = '../data/grids_NL/'

##MP
#inpath_snow = '../data/NansenLegacy/magnaprobe/'

##GEM-2
#inpath_ice = '../data/NansenLegacy/gem2/'

#loc = 'P4'
#dates = ['20210505']

#loc = 'P5'
#dates = ['20210508']

##loc = 'P6'
##dates = ['20210510']

#loc = 'P7'
#dates = ['20210513']

#CIRFA cruise
outpath = '../plots_cirfa22/'
outpath_grid = '../data/grids_cirfa22/'

##loc='Landfast_S'
##dates=['20220427']

loc='Landfast_M'
dates=['20220501']

#loc='Drift1'
#dates=['20220505']

#loc='Drift2'
#dates=['20220507']

#inpath_ice = '../data/CIRFA22/'+loc+'/'
#inpath_snow = inpath_ice

for dd in range(0,len(dates)):
    date=dates[dd]
    print(date)

    #examples of dates when there is something wrong with the GEM-2 data
    if date == '20191226' and loc=='Sloop':     #only part of the Sloop has GEM-2 data
        date_gem2 = '20200102'
    elif date == '20200116':                      #bad coordinates on both loops/not floenavi problem
        date_gem2 = '20200109'
    elif date == '20200227' and loc=='Nloop':   #incomplete N loop
        date_gem2 = '20200220'
    elif date == '20200416':                    #floenavi problem
        date_gem2 = '20200424'
    elif date == '20200119' and loc=='runway':  #GEM-2 was not used
        date_gem2 = '20200112'
    elif date == '20200119' and loc=='ridgeFR1':  #GEM-2 was not used
        date_gem2 = '20200108'    
    elif date == '20200221' and loc=='ridgeFR2':  #GEM-2 was not used 
        date_gem2 = '20200212' 
    elif date == '20200718' and loc=='special':  #GEM-2 was not used 
        date_gem2 = '20200709'
    else:
        date_gem2 = date

    #problematic MP coordinate days
    if date == '20200223':
        date = '20200207'
        date_gem2 = '20200223'
        
    if date == '20191226' and loc=='Nloop':
        date = '20191219'
        date_gem2 = '20191226'

    print(loc)
    print(date)
    print(date_gem2)

    #we need to merge all GEM-2 survery for that day first
    #coordinates
    xx = []
    yy = []
    fname = glob(inpath_ice+date_gem2+'*/*-track-icecs-xy.csv')
    if outpath == '../plots_cirfa22/':
        fname = glob(inpath_ice+'*'+date_gem2+'*gem2*-track-icecs-xy.csv')
    for fn in fname:
        print(fn)
        x = getColumn(fn,3)
        y = getColumn(fn,4)
    
        xx.extend(x); yy.extend(y)
        
    xx_full = np.array(xx,dtype=float)
    yy_full  = np.array(yy,dtype=float)
        
    #ice thickness data
    tt18 = []; tt5 = []; tt93 = []; ts_gem=[]
    fname = glob(inpath_ice+date_gem2+'*/*-channel-thickness.csv')
    if outpath == '../plots_cirfa22/':
        fname = glob(inpath_ice+'*'+date_gem2+'*-channel-thickness.csv')

    for fn in fname:
        print(fn)
        #time, record_id, longitude, latitude, xc, yc, f1525Hz_hcp_i, f1525Hz_hcp_q, f5325Hz_hcp_i, f5325Hz_hcp_q, f18325Hz_hcp_i, f18325Hz_hcp_q, f63025Hz_hcp_i, f63025Hz_hcp_q, f93075Hz_hcp_i, f93075Hz_hcp_q
        if date=='20200206' or date=='20200406':    #problems with instruments take q of 18kHz, 63kHz and 93kHz
            t18 = getColumn(fn,11)
            t5 = getColumn(fn,13)
            t93 = getColumn(fn,15)
            ts = getColumn(fn,0)
            
        elif outpath == '../plots_cirfa22/':
            t18 = getColumn(fn,12)        #take 18KHz ip (12)
            t5 = getColumn(fn,10)        #take 1.5KHz ip (10)
            t93 = getColumn(fn,14)         #take 63KHz ip (14)
            ts = getColumn(fn,0)

        elif 'ridge' in loc:
            t18 = getColumn(fn,8)        #take 5KHz ip (8)
            t5 = getColumn(fn,10)        #take 18KHz ip (10)
            t93 = getColumn(fn,15)         #take 93KHz q (15)
            ts = getColumn(fn,0)

        else:
            t18 = getColumn(fn,12)        #take 18KHz ip (10)
            t5 = getColumn(fn,10)        #take 5KHz ip (8)
            t93 = getColumn(fn,14)         #take 93KHz ip (14) 
            ts = getColumn(fn,0)

        tt18.extend(t18[1:-1])     #floenavi scripts looses coordinates at the start and end of the file
        tt5.extend(t5[1:-1])
        tt93.extend(t93[1:-1])
        ts_gem.extend(ts[1:-1])
        
    tt18 = np.array(tt18,dtype=float)
    tt5 = np.array(tt5,dtype=float)
    tt93 = np.array(tt93,dtype=float)
    
    tmp=[]
    for x in ts_gem:
        try:
            #timestamp has milliseconds
            ttmp = datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f")
        except:
            #but some rows dont have it and have a leading empty space instead
            ttmp = datetime.strptime(x, "       %Y-%m-%dT%H:%M:%S")
        tmp.append(ttmp)
        
    ts_gem = np.array(tmp,dtype=np.datetime64)
    
    #run these through a running window smoothing filter - we can then easily use the nearest neighbor also for the GEM-2
    tt18 = savgol_filter(tt18, window, polyorder)
    tt5 = savgol_filter(tt5, window, polyorder)
    tt93 = savgol_filter(tt93, window, polyorder)
    
    #MP
    #get magnaprobe track file
    if loc != 'recon':
        
        if outpath == '../plots_cirfa22/':
            fname = glob(inpath_snow+'*magnaprobe-'+loc+'-'+date+'*-track-icecs-xy_corr.csv')[0]
            
        else:
            fname = glob(inpath_snow+'*/magnaprobe-transect-'+date+'*'+loc+'-track-icecs-xy_corr.csv')[0]
        
        #on certain dates there can be more than one 'special' transect on same date
        if loc == 'special':
            flist=glob(inpath_snow+'*/magnaprobe-transect-'+date+'*'+loc+'-track-icecs-xy_corr.csv')
            if len(flist)>1:
                print('special transect with options',len(flist))
                #on 23 Jan 2020 there were two transects (lead event and long), only long transect has GEM-2 measurements
                if date=='20200123':
                    fname = glob(inpath_snow+'*/magnaprobe-transect-'+date+'*'+'21-140'+'*'+loc+'-track-icecs-xy_corr.csv')[0]   #this should be 21-140
        
                #on 16 June 2020 there were two initial surveys of floe, both with loc=special, only second one has GEM-2 measurements
                if date=='20200617':
                    fname = glob(inpath_snow+'*/magnaprobe-transect-'+date+'*'+'44-266'+'*'+loc+'-track-icecs-xy_corr.csv')[0]
                #on 19 July 'drillholes' and 'ARIEL' are both special    
                if date=='20200719':
                    if dates[dd-1] =='20200617': #first transect
                        fname = glob(inpath_snow+'*/magnaprobe-transect-'+date+'*'+'47-224'+'*'+loc+'-track-icecs-xy_corr.csv')[0]
                    if dates[dd-1] =='20200719': #second transect
                        fname = glob(inpath_snow+'*/magnaprobe-transect-'+date+'*'+'47-226'+'*'+loc+'-track-icecs-xy_corr.csv')[0]
                        
                print(fname)
        
        
        
        print(fname)

        dt = getColumn(fname,0,skipheader=1)
        lon = getColumn(fname,1,skipheader=1)
        lat = getColumn(fname,2,skipheader=1)

        mxx = getColumn(fname,3,skipheader=1)
        mxx = np.array(mxx,dtype=float)

        myy = getColumn(fname,4,skipheader=1)
        myy = np.array(myy,dtype=float)
            
        #get some meta data for the MP transect:
        dx = mxx[1:]-mxx[:-1]
        dy = myy[1:]-myy[:-1]
        d = np.sum(np.sqrt(dx**2+dy**2))
        print('transect length:')
        print(d)
        print('MP measurement spacing:')
        spacing = np.mean(np.sqrt(dx**2+dy**2))
        print(spacing)
        
        #make straight lines of pulk ridge transects
        if 'ridge' in loc:
            ##ridges with pulk
            window = 3  #smoothing filter window for GEM-2 (with spacing .2m is this 60cm!)
            polyorder = 0

            #ridge transects were taken along a line with nominal spacing, 1m
            #the GPS coordinates have precision of about 2-5m and are worse
            #make sure that the lenght of coordinate vectors is same as originally
            print(len(mxx))
            print(len(myy))
            
            print((mxx))
            print((myy))

            if np.abs(mxx[0]-mxx[-1])<4:
                mxx[:] = np.mean(mxx)
            else:
                mdx = np.round(np.abs(mxx[0]-mxx[-1])/len(mxx),2)
                mxx[:] = np.arange(mxx[0],mxx[-1],mdx)[:len(mxx)]


            if np.abs(myy[0]-myy[-1])<5:
                myy[:] = np.mean(myy)
            else:
                mdy = np.abs(myy[0]-myy[-1])/len(myy)
                myy[:] = np.arange(myy[0],myy[-1],mdy)[:len(myy)]


        if scale_limit==True:
            limit = spacing*2

        of = fname.split('track')[0]+'meta.txt'
        print(of)
        np.savetxt(of, (d,spacing))

        #snow depth data
        #try to do something with the bad coordinate data of MP
        if (date_gem2 == '20200223') and (date == '20200207'):
            date = '20200223'
            date_gem2 = '20200223'
            
            #local coordinates
            #there is only 276 valid measurements that day (compared to 458 measurements 07/02/2020) - Ian did 2m spacing with MP?
            print(mxx.shape)
            mxx = mxx[::2]
            myy = myy[::2]
            
            #timestamp and lat/lon
            dt = np.ones_like(mxx)*-999
            
            #use non-physical values for lat/lon
            lat = np.ones_like(mxx)*-999
            lon = np.ones_like(mxx)*-999

        #read in magnaprobe data
        fname = fname.split('-track')[0]+ext_mp
        print(fname)
        
        snod = getColumn(fname,3, delimiter=',', skipheader=4)
        snod = np.array(snod,dtype=float)[:-2]/100             #convert from cm to m
        #change all negative data to zero
        snod = np.where(snod<0,0,snod)
        
        if date == '20200223':
            print(snod.shape)
            snod = snod[:len(mxx)+1]
            
        #there is no floenavi data between 2 and 8 April - ship coordinates are used instead, but there is lots of deformation still...
        #this data need some manual fixing
        #first apply some shifts to get it to aprox same place in our grid
        if date == '20200406':
            myy = myy-500
            yy_full = yy_full-500
            
        #lateral movement out of the grid at the end of CO2 - just shift in
        if date == '20200507' and loc=='Sloop':
            mxx = mxx+150
            xx_full = xx_full+150
                      
    #rcon data is GEM-2 only - get dummy values with reduced spacing comparing to GEM-2, usually ski-doo - fast motion and standing...
    else:
        mxx = np.ma.masked_invalid(xx_full[::5])
        myy = np.ma.masked_invalid(yy_full[::5])
        snod = np.ones_like(mxx)*0 #some mean value
        
        #also get other data that other transects get from MP
        dt = []
        lon = []
        lat = []
        tmp = glob(inpath_ice+date_gem2+'*/*-track-icecs-xy.csv')
        for fn in tmp:
            print(fn)
            dt0 = getColumn(fn,0)[::5]
            lon0 = getColumn(fn,1)[::5]
            lat0 = getColumn(fn,2)[::5]
        
            dt.extend(dt0); lon.extend(lon0); lat.extend(lat0)
            
        
    #####################################################################################################################################3
    #lets make a regular grid with 'step' m spacing, corresponding to the CO local coordinate boundaries
    grid_x, grid_y = np.mgrid[-950:820:step, -1200:650:step]
    extent=(-950,820,-1200,650)

    #long transect, needs a different grid
    if date == '20200123':
        grid_x, grid_y = np.mgrid[-7000:-3000:step, 1775:3625:step]
        extent = (-7000,-3000,1775,3625)
        
    #event transect
    if loc == 'special' and date == '20200126':
        grid_x, grid_y = np.mgrid[-1300:-1000:step, 400:650:step]
        extent=(-1300,-1000,400,650)
        
    #dark site transects
    if date == '20200107':
        grid_x, grid_y = np.mgrid[1000:1600:step, -650:-100:step]
        extent=(1000,1600,-650,-100)

    if date == '20200115':
        grid_x, grid_y = np.mgrid[1600:1750:step, -350:-200:step]
        extent=(1600,1750,-350,-200)

    #lead recon (Dranitsyn lead)
    if date == '20200226':
        grid_x, grid_y = np.mgrid[-1100:-1000:step, 50:100:step]
        extent=(-1100,-1000,50,100)

    #ridge transects
    if 'ridge' in loc and date != '20200828' and date != '20200918':
        print('Ridge!')
        
        grid_x, grid_y = np.mgrid[200:900:step, -600:100:step]
        extent=(200,900,-600,100)

    #whole CO
    if loc == 'recon':
        grid_x, grid_y = np.mgrid[-1300:1500:step, -850:1100:step]
        extent=(-1300,1500,-850,1100)
    
    if loc1 == 'Nloop_spine':
        grid_x, grid_y = np.mgrid[460:850:step, -500:-180:step]
        extent=(460,850,-500,-180)
        
        if date == '20200320':
            grid_x, grid_y = np.mgrid[450:850:step, -550:-200:step]
            extent=(450,850,-550,-200)
            
        if date == '20200326':
            grid_x, grid_y = np.mgrid[420:850:step, -550:-210:step]
            extent=(420,850,-550,-210)
            
        if date == '20200424' or date == '20200430' or date == '20200507':
            grid_x, grid_y = np.mgrid[460:850:step, -550:-210:step]
            extent=(460,850,-550,-210)
    
    #leg5 whole CO
    if loc == 'special':
        if date == '20200827' or date=='20200903' or date=='20200910':
            grid_x, grid_y = np.mgrid[-300:700:step, -800:1000:step]
            extent=(-300,700,-800,1000)
    
    #assign values to be used for gridding
    sd_points = np.column_stack((mxx,myy))

    #something fishy here - consequence of floenavi coordinate conversion (beginning and end of files can be cut off)
    if loc == 'Sloop' and date == '20191205':
        sd_points = np.column_stack((mxx[1:],myy[1:]))
        dt = dt[1:]
        lon = lon[1:]
        lat = lat[1:]

    sd_values = snod[1:]
    if loc == 'Sloop':
        if date=='20191107' or date == '20191114' or date == '20191205' or date == '20191031':
            sd_values = snod

    if date=='20200119' or loc=='recon':
        sd_values = snod

    print(sd_points.shape)
    print(sd_values.shape)

    #interpolate the data to regular grid
    grid_sd = griddata(sd_points, sd_values, (grid_x, grid_y), method=method_mp)       

    #run through all the grid and identify all the grid cells that are actually close enough to the data
    mask_g = np.ones_like(grid_x)

    for m in range(0,grid_x.shape[0]):
        for n in range(0,grid_x.shape[1]):
            dx = mxx-grid_x[m,n]
            dy = myy-grid_y[m,n]                    
            dg = np.sqrt(dx**2+dy**2)
            
            if np.min(dg) < limit: mask_g[m,n]=0

    #total thickness data
    channels = [tt18,tt5,tt93]
    ch_name =  ['_18kHz','_5kHz','_93kHz']
    grid_tt18=[];grid_tt5=[];grid_tt93=[]
    output_tt = [grid_tt18,grid_tt5,grid_tt93]

    for ch in range(0,len(channels)):
        print(ch_name[ch])
        #print(channels[ch])
        #get all original coordinates for each channel
        xx = xx_full.copy()
        yy = yy_full.copy()        
        
        #there can be nans in the thickness data, fix this before we proceed
        tt = np.ma.masked_invalid(channels[ch])  
        
        #time stamps should only be interpolated for one of the channels
        
        xx = xx[tt.mask == False]
        yy = yy[tt.mask == False]
        if ch_name[ch] ==  '_18kHz':
            ts_gem = ts_gem[tt.mask == False]
        tt = tt[tt.mask == False]

        #there can also be nans in position, fix this before we proceed
        xx = np.ma.masked_invalid(xx)
        yy = yy[xx.mask == False]
        tt = tt[xx.mask == False]
        if ch_name[ch] ==  '_18kHz':
            ts_gem = ts_gem[xx.mask == False]
        xx = xx[xx.mask == False]

        points = np.column_stack((xx,yy))
        values = tt
        grid_tt = griddata(points, values, (grid_x, grid_y), method=method_gem2)

        #difference = sea ice thickness
        grid_it = grid_tt - grid_sd

        #keep the original grid for nn search later
        output_tt[ch] = grid_tt.copy()
        
        #ensure that we have data for exactly same grid points
        data_mask = (np.isnan(grid_sd)) | (np.isnan(grid_tt)) | (mask_g == 1)
        grid_sd = np.ma.array(grid_sd,mask=data_mask).filled(np.nan)
        grid_tt = np.ma.array(grid_tt,mask=data_mask).filled(np.nan)
        grid_it = np.ma.array(grid_it,mask=data_mask).filled(np.nan)
        
        if show==True:
            ##lets check how this looks like
            plt.subplot(221)
            plt.imshow(mask_g.T, extent=extent, origin='lower')
            plt.title('Original')
            plt.subplot(222)
            plt.imshow(grid_sd.T, extent=extent, origin='lower',vmin=0,vmax=.5, cmap=plt.cm.Spectral_r)
            plt.colorbar()
            plt.title('Snow')
            plt.subplot(223)
            plt.imshow(grid_tt.T, extent=extent, origin='lower',vmin=0,vmax=4, cmap=plt.cm.Spectral_r)
            plt.colorbar()
            plt.title('Total')
            plt.subplot(224)
            plt.imshow(grid_it.T, extent=extent, origin='lower',vmin=0,vmax=4, cmap=plt.cm.Spectral_r)
            plt.colorbar()
            plt.title('Ice')
            plt.gcf().set_size_inches(6, 6)
            plt.show()

        #save all these gridded data
        stp = str(step)
        #of = outpath_grid+loc+'_'+date+'_'+stp+'m.npz'
        of = outpath_grid+loc+'_'+date+'_'+stp+'m_'+method_gem2+ch_name[ch]+'.npz'
        if (date_gem2 == '20200223') or (date_gem2 == '20191226' and loc=='Nloop'):
            of = outpath_grid+loc+'_'+date_gem2+'_'+stp+'m_'+method_gem2+ch_name[ch]+'.npz'
        if loc1=='Nloop_spine':
            of = outpath_grid+loc1+'_'+date+'_'+stp+'m_'+method_gem2+ch_name[ch]+'.npz'
        print(of)
        with open(of, 'wb') as f:
            np.savez(f, x = grid_x, y = grid_y, snow = grid_sd, tt = grid_tt, ice = grid_it)
            
        #do the same for the timestamp
        if ch_name[ch] ==  '_18kHz':
            values = ts_gem
            grid_ts = griddata(points, values, (grid_x, grid_y), method=method_gem2)
            output_ts = grid_ts.copy()

    ##########################################################################################################
    if table_output==True:
        #write out the ice mass balance transect collocated tables
        
        #create output name
        if loc=='recon':
            outname = inpath_snow+'recon/magna+gem2'+date+'_'+loc+'.csv'
        else:
            outname = fname.split('probe')[0]+'+gem2'+fname.split('probe')[1].split('.dat')[0]+'.csv'
            #new version with GEM-2 timestamp
            outname = fname.split('probe')[0]+'+gem2'+fname.split('probe')[1].split('.dat')[0]+'_GEM2_ts.csv'
        
        #sampling subsets
        if loc1=='Nloop_spine':
            outname = fname.split('probe')[0]+'+gem2'+fname.split('probe')[1].split('.dat')[0]+'_spine.csv'
        
        if (date_gem2 == '20200223'):
            outname = fname.split('probe')[0]+'+gem2'+fname.split('probe')[1].split('.dat')[0]+'_coords_from_20200207.csv'
        
        if (date_gem2 == '20191226' and loc=='Nloop'):
            outname = fname.split('probe')[0]+'+gem2'+fname.split('probe')[1].split('.dat')[0]+'_ice_from_'+date_gem2+'.csv'

        #Nansen Legacy
        if 'P' in loc:
            outname = fname.split('probe-')[0]+'+gem2'+fname.split('probe-')[1].split('.dat')[0]+'.csv'

        tt_nn18 = np.zeros_like(sd_values)
        tt_nn5 = np.zeros_like(sd_values)
        tt_nn93 = np.zeros_like(sd_values)
        ts_nngem2 = np.empty((sd_values.shape[0]),dtype='datetime64[ns]')
        #find nearest tt and it values to original mp/sd points        
        for i in range(0,tt_nn18.shape[0]):
            dx = sd_points[:,0][i]-grid_x
            dy = sd_points[:,1][i]-grid_y                  
            dg = np.sqrt(dx**2+dy**2)
            dgf = dg.flatten()
            
            #don take values too far away
            if np.min(dgf) > 4:
                tt_nn18[i] = -999; tt_nn5[i] = -999; tt_nn93[i] = -999; ts_nngem2[i] = np.datetime64('nat')
            else:
                #find nearest tt and it value
                nn = np.argmin(dgf)
                tt_nn18[i] = output_tt[0].flatten()[nn]
                tt_nn5[i] = output_tt[1].flatten()[nn]
                tt_nn93[i] = output_tt[2].flatten()[nn]              
                ts_nngem2[i] = np.datetime64(output_ts.flatten()[nn])
                
                #there can be nans...
                #replace with mean in the closest n values
                n=3
                while (np.isnan(tt_nn18[i]) and n < 25):
                    nn = np.argpartition(dgf,n)[:n]
                    tmp18 = output_tt[0].flatten()[nn]
                    tmp5 = output_tt[1].flatten()[nn]
                    tmp93 = output_tt[2].flatten()[nn]
                    tmpts = output_ts.flatten()[nn]

                    tt_nn18[i] = np.mean(np.ma.masked_invalid(tmp18))
                    tt_nn5[i] = np.mean(np.ma.masked_invalid(tmp5))
                    tt_nn93[i] = np.mean(np.ma.masked_invalid(tmp93))
                    ts_nngem2[i] = np.datetime64(tmpts[0]) #WARNING take the first value (and not the mean)
                    
                    n = n+1
        
        mask = (tt_nn18 == -999) | (lon==0)                         #recon and others based on GEM-2 has some zero coordinates
        tt_nn18 = np.ma.array(tt_nn18, mask=mask).compressed()
        tt_nn5 = np.ma.array(tt_nn5, mask=mask).compressed()
        tt_nn93 = np.ma.array(tt_nn93, mask=mask).compressed()
        ts_nngem2 = np.ma.array(ts_nngem2, mask=mask).compressed()
        sd = np.ma.array(sd_values.data, mask=mask).compressed()    #there can be some masked values in here already...
        
        dt = np.ma.array(dt, mask=mask).compressed()
        lon = np.ma.array(lon, mask=mask).compressed()
        lat = np.ma.array(lat, mask=mask).compressed()
        sd_points0 = np.ma.array(sd_points[:,0], mask=mask).compressed()
        sd_points1 = np.ma.array(sd_points[:,1], mask=mask).compressed()
        
        it_nn18 = tt_nn18 - sd
        it_nn5 = tt_nn5 - sd
        it_nn93 = tt_nn93 - sd
        
        ##in summer some ice thickness values are negative!!! Are these salty melt ponds? (connected to sea water somewhere)
        #negative values could be used for detection of salty melt ponds!
        #if tt_nn18 < 0: it_nn18 = 0
        #if tt_nn5 < 0: it_nn5 = 0
        #if tt_nn93 < 0: it_nn93 = 0
                
        #print(it_nn18)
        
        #mixed surface data (snow=1, SSL/mixed=2 and melt ponds=-1, frozen pond=3) for legs 4 and 5
        #this has to be done here, so that SSL and melt ponds are subtracted from total thickness
        if ('transect' in loc) or ('albedo' in loc) or loc == 'ARIEL' or loc == 'kuka' or date =='20200827' or date=='20200903' or date=='20200910' or date=='20200902' or date=='20200909' or date=='20200919':
            print(loc, 'has recorded surface...')
            surface = getColumn(fname,22, delimiter=',', skipheader=4)
            surface = np.array(surface,dtype=np.int)[1:-2]      #use some values less, just like sd...
            
            #SSL is also snow here
            surface_mask = np.where(surface>0,1,0)
            #make all melt pond surface into zero snow depth
            surface_mask = np.ma.array(surface_mask, mask=mask);surface_mask = surface_mask.compressed()
            sd = sd*surface_mask
            
            #melt pond depths
            surface_mask_mpd = np.where(surface<0,1,0)
            mpd = sd_values*surface_mask_mpd
            
            #use unphysical value (-1) where zero            
            sd = np.where(sd==0,-1,sd_values)
            mpd = np.where(mpd==0,-1,mpd)
            
        else:
            #winter legs get some dummy values
            mpd = np.ones_like(sd)*-1
            surface = np.ones_like(sd_values)

        #convert back to milliseconds string
        ##datetime only works to microseconds (ms) precision
        #dt = ts_nngem2.astype('M8[ms]').astype('O')
        #ts_nngem2 = [ datetime.strftime(x, "%Y-%m-%dT%H:%M:%S.%f") for x in dt ]
        
        #try pandas instead
        import pandas as pd
        ts_nngem2 = pd.to_datetime(ts_nngem2, format='%Y-%m-%dT%H:%M:%S.%f')
            
        #write new csv file with all the ice mass balance variables
        tt = [dt,lon,lat,sd_points0,sd_points1,sd,mpd,surface,it_nn18,it_nn5,it_nn93,ts_nngem2]
        table = list(zip(*tt))

        print(outname)
        with open(outname, 'wb') as f:
            #header
            if date=='20200206' or date=='20200406':
                f.write(b'Date/Time, Lon, Lat, Local X, Local Y, Snow Depth (m), Melt Pond Depth (m), Surface Type, Ice Thickness 18kHz q (m), Ice Thickness 63kHz q (m), Ice Thickness 93kHz q (m), GEM2 timestamp\n')
            else:
                f.write(b'Date/Time, Lon, Lat, Local X, Local Y, Snow Depth (m), Melt Pond Depth (m), Surface Type, Ice Thickness 18kHz ip (m), Ice Thickness 5kHz ip (m), Ice Thickness 93kHz ip (m), GEM2 timestamp\n')
            np.savetxt(f, table, fmt='%s', delimiter=",")

