import numpy as np
from glob import glob
from tt_func import getColumn
from scipy.signal import savgol_filter
from scipy.interpolate import griddata
import matplotlib.pyplot as plt

#grid parameters
step = 2        #grid spacing in meters 
step = 1        #for ridges
step = 5
limit = step*2  #how far from MP coordinate to search 
#limit = 5       #some equivalent to GEM-2 footprint or max thickness measured by GEM-2?
scale_limit=False   #depending on the MP spatial resolution
#method_gem2 = 'linear'  #GEM-2 data needs to be smoothed >> problem: max distance cant be specified! This method gives strange results
method_gem2 = 'nearest'
method_mp = 'nearest'   #at dense grids every measurement should be used separately

#MP file extension depends on the leg
ext_mp='.dat'
ext_mp='.csv'

window = 5  #with spacing .2m is this 1m  ~MP spacing
polyorder = 3

##ridges with pulk
#window = 3  #smoothing filter window for GEM-2 (with spacing .2m is this 60cm!)
#polyorder = 0

#show gridded data
show=True

#make mp+gem2 table output
table_output=True

outpath = '../plots_AGU/'
outpath_grid = '../data/grids_AGU/'

#MP
#inpath_snow = '../../../MOSAiC/leg2_ICE/transect/'
inpath_snow = '../data/MCS/MP/'

#GEM-2
#inpath_ice = '../../../MOSAiC/thickness_workspace/01-ice-thickness/'
inpath_ice = '../data/MCS/GEM2_thickness/01-ice-thickness/'
#inpath_ice = '../data/MCS/01-ice-thickness/'


#location
loc = 'Nloop'
#loc1 = 'Nloop_spine'
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
#date = '20200206'   #very bad GEM-2 data in both loops (unrealistic low values in all f.)
#date = '20200220'   #suddenly quite thick
#date = '20200227'
#date = '20200305'
#date = '20200320'   #tiny bits of GEM-2 track are missing, chicken neck
#date = '20200326'   #slightly different shape from here on
#date = '20200403'   #bad GPS track - floenavi problem - fixed by PS position, will need some shifting and rotation in the grid!
##date = '20200416'   #!!!no GPS coordinates from GEM-2/use old track
#date = '20200424'
#date = '20200430'   #
#date = '20200507'

dates = ['20191024','20191031','20191107','20191114','20191121','20191128','20191205',  '20191219','20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227', '20200305','20200320','20200326','20200403','20200416','20200424','20200430','20200507'] 

dates = ['20200507'] 

loc = 'Sloop'
#date = '20191031'   #2m spacing!
#date = '20191107'   #3.1m spacing!!!
#date = '20191114'   #2.9m spacing!!!    - no visible snowdunes yet...
#date = '20191205'   #1.8m spacing!
#date = '20191226'   #GEM-2 has only level ice/part of the S loop
#date = '20200102'
#date = '20200109'
#date = '20200116'   #bad GPS data on GEM-2 - data from last week used, 1.1m MP spacing
#date = '20200130'   #1.05m MP spacing
#date = '20200206'   #very bad GEM-2 data in both loops (unrealistic low values), 1.06m MP spacing
#date = '20200220'   #too thick ice in 18KHz and 93KHz?
#date = '20200227'  
#date = '20200305'   #1.5m spacing!   
#date = '20200330'
#date = '20200406'   #floenavi problem
#date = '20200426'
date = '20200507'   #only a part of the loop: from cross-roads to the main ridge corner

#location
#loc = 'snow1'
#date = '20191222'
#date = '20200112'
#date = '20200126'   #just a square (half of transect)
#date = '20200207'
#date = '20200223'   #MP GPS is really off the track and messy!
#date = '20200604'  #leg 4

#location
#loc = 'runway'
#date = '20200112'
#date = '20200119'
#date = '20200207'

#location - ridges
#only for ridges that were surveyed with a pulk: othrwise use script tt_grid_ridge.py
#loc = 'ridgeFR1'    #installation (also very close to snow)
#date = '20200305'

#loc = 'ridgeA1'    #
#loc = 'ridgeA2'
#loc = 'ridgeA3'
#date = '20200410'
loc = 'ridge'
dates = ['20200628','20200728']

#loc = 'ridgeD'
#date = '20200410'
#date = '20200416'
#date = '20200424'
#date = '20200430'
#date = '20200507'

#loc = 'ridgeE'
#date = '20200424'


###location
#loc = 'special'
#date = '20200107'   #Dark site FYI
#date = '20200115'   #Dark site SYI
#date = '20200123'  #long transect
#date = '20200326'  #leg 3 lead at the Nloop (chicken beak)
#date = '20200226'   #lead scounting at the Dranitsyn lead (that did not work out...)

#loc = 'recon'
#date = '20200228'   #airport recon - has no MP data
#table_output=False  #not useful
#step=5
#limit = step*2            #no need to search far


#leg4
#loc = 'transect'
#date = '20200629'
#date = '20200630'  #complete data!
#date = '20200703'
#date = '20200704'
#date = '20200705'  #decent spacing, 2m
#date = '20200706'
#date = '20200707'
#date = '20200708'
#date = '20200710'  #1.8m spacing!
#date = '20200714'   #includes branches/albedo lines
#date = '20200719'
#date = '20200720'  #part of GEM-2 missing (little bit), but best spacing so far! 1.5m
#date = '20200725'  #first good after a while...
#date = '20200726'

#leg5
#date = '20200830'  #l:685m, 1.6m
#date = '20200903'  #l:495m, 2.1m (just 230 measurements...)
#date = '20200907'  #l:485m, 2.1m (just 229 measurements...)
#date = '20200918'  #l:493m, 1.7m

##special transects of leg 4
#loc = 'albedoLD'
#dates = ['20200630','20200706','20200707','20200721']

#loc = 'albedoRBB'
#dates = ['20200630','20200706','20200707']

#special transects of leg 5

for dd in dates:
    date=dd
    print(date)

    #examples of dates when there is something wrong with the GEM-2 data
    if date == '20200116':                      #bad coordinates on both loops/not floenavi problem
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
    fname = glob(inpath_ice+date_gem2+'*/mosaic-transect-*-gem2-*-track-icecs-xy.csv')
    for fn in fname:
        print(fname)
        x = getColumn(fn,3, delimiter=',', magnaprobe=False)
        y = getColumn(fn,4, delimiter=',', magnaprobe=False)
        
        xx.extend(x); yy.extend(y)
        
    xx_full = np.array(xx,dtype=np.float)
    yy_full  = np.array(yy,dtype=np.float)
        
    #ice thickness data
    tt18 = []; tt5 = []; tt93 = []
    fname = glob(inpath_ice+date_gem2+'*/mosaic-transect-*-gem2-*-channel-thickness.csv')
    for fn in fname:
        
        #time, record_id, longitude, latitude, xc, yc, f1525Hz_hcp_i, f1525Hz_hcp_q, f5325Hz_hcp_i, f5325Hz_hcp_q, f18325Hz_hcp_i, f18325Hz_hcp_q, f63025Hz_hcp_i, f63025Hz_hcp_q, f93075Hz_hcp_i, f93075Hz_hcp_q
        t18 = getColumn(fn,10, delimiter=',', magnaprobe=False)        #take 18KHz ip
        t5 = getColumn(fn,8, delimiter=',', magnaprobe=False)        #take 5KHz ip
        t93 = getColumn(fn,14, delimiter=',', magnaprobe=False)        #take 93KHz ip

        tt18.extend(t18[1:-1])     #floenavi scripts looses coordinates at the start and end of the file
        tt5.extend(t5[1:-1])
        tt93.extend(t93[1:-1])
        
    tt18 = np.array(tt18,dtype=np.float)
    tt5 = np.array(tt5,dtype=np.float)
    tt93 = np.array(tt93,dtype=np.float)

    #run these through a running window smoothing filter - we can then easily use the nearest neighbor also for the GEM-2
    tt18 = savgol_filter(tt18, window, polyorder)
    tt5 = savgol_filter(tt5, window, polyorder)
    tt93 = savgol_filter(tt93, window, polyorder)

    #MP
    if loc != 'recon':
        fname = glob(inpath_snow+'*/magnaprobe-transect-'+date+'*'+loc+'-track-icecs-xy_corr.csv')[0]
        print(fname)

        dt = getColumn(fname,0, delimiter=',', magnaprobe=False)
        lon = getColumn(fname,1, delimiter=',', magnaprobe=False)
        lat = getColumn(fname,2, delimiter=',', magnaprobe=False)

        mxx = getColumn(fname,3, delimiter=',', magnaprobe=False)
        mxx = np.array(mxx,dtype=np.float)

        myy = getColumn(fname,4, delimiter=',', magnaprobe=False)
        myy = np.array(myy,dtype=np.float)
            
        #get some meta data for the MP transect:
        dx = mxx[1:]-mxx[:-1]
        dy = myy[1:]-myy[:-1]
        d = np.sum(np.sqrt(dx**2+dy**2))
        print('transect length:')
        print(d)
        print('MP measurement spacing:')
        spacing = np.mean(np.sqrt(dx**2+dy**2))
        print(spacing)

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
            
            mxx = mxx[::2]
            myy = myy[::2]

        fname = glob(inpath_snow+'*/magnaprobe-transect-'+date+'*'+loc+ext_mp)[0]
        print(fname)
        snod = getColumn(fname,3, delimiter=',', magnaprobe=True)
        snod = np.array(snod,dtype=np.float)[:-2]/100             #convert from cm to m
        #change all negative data to zero
        snod = np.where(snod<0,0,snod)

        if date == '20200223':
            snod = snod[:len(mxx)+1]
            
        if date == '20200406':
            #there is no floenavi data between 2 and 8 April - ship coordinates are used instead, but there is lots of deformation still...
            #this data need some manual fixing
            #first apply some shifts to get it to aprox same place in our grid
            myy = myy-500
            yy_full = yy_full-500        

    #rcon data is GEM-2 only
    else:
        mxx = np.ma.masked_invalid(xx_full)
        myy = np.ma.masked_invalid(yy_full)
        snod = np.ones_like(mxx)*.2
        
    #####################################################################################################################################3
    #lets make a regular grid with 'step' m spacing, corresponding to the CO local coordinate boundaries
    grid_x, grid_y = np.mgrid[-950:820:step, -1200:650:step]
    extent=(-950,850,-1200,620)

    #previously: extent=(-950,850,-600,620)

    #bring the data closer to the source (but keep same grid dimensions, so that we can overlay!!!)
    if date == '20200507' and loc=='Sloop':
        grid_x, grid_y = np.mgrid[-1100:670:step, -600:650:step]
        extent=(-1100,670,-600,650)

    #long transect, needs a different grid
    if date == '20200123':
        grid_x, grid_y = np.mgrid[-7000:-3000:step, 1775:3625:step]
        extent = (-7000,-3000,1775,3625)
        
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
    if 'ridge' in loc:
        print('Ridge!')
        
        grid_x, grid_y = np.mgrid[200:900:step, -600:100:step]
        extent=(200,900,-600,100)

    #whole CO
    if loc == 'recon':
        grid_x, grid_y = np.mgrid[-1000:250:step, -800:1100:step]
        extent=(-1000,250,-800,1100)
    
    #if loc1 == 'Nloop_spine':
        #loc = loc1
        #grid_x, grid_y = np.mgrid[460:850:step, -500:-180:step]
        #extent=(460,850,-500,-180)
        
        #if date == '20200320':
            #grid_x, grid_y = np.mgrid[450:850:step, -550:-200:step]
            #extent=(450,850,-550,-200)
            
        #if date == '20200326':
            #grid_x, grid_y = np.mgrid[420:850:step, -550:-210:step]
            #extent=(420,850,-550,-210)
            
        #if date == '20200424' or date == '20200430' or date == '20200507':
            #grid_x, grid_y = np.mgrid[460:850:step, -550:-210:step]
            #extent=(460,850,-550,-210)
            
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
        #get all original coordinates for each channel
        xx = xx_full.copy()
        yy = yy_full.copy()
        
        #there can be nans in the thickness data, fix this before we proceed
        tt = np.ma.masked_invalid(channels[ch])
        xx = xx[tt.mask == False]
        yy = yy[tt.mask == False]
        tt = tt[tt.mask == False]

        #there can also be nans in position, fix this before we proceed
        xx = np.ma.masked_invalid(xx)
        yy = yy[xx.mask == False]
        tt = tt[xx.mask == False]
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
        print(of)
        with open(of, 'wb') as f:
            np.savez(f, x = grid_x, y = grid_y, snow = grid_sd, tt = grid_tt, ice = grid_it)

    ##########################################################################################################
    if table_output==True:
        #write out the ice mass balance transect collocated tables
        
        #create output name
        outname = fname.split('probe')[0]+'+gem2'+fname.split('probe')[1].split('.dat')[0]+'.csv'
        
        #sampling subsets
        if loc == 'Nloop_spine':
            outname = fname.split('probe')[0]+'+gem2'+fname.split('probe')[1].split('.dat')[0]+'_spine.csv'
        
        if (date_gem2 == '20200223') or (date_gem2 == '20191226' and loc=='Nloop'):
            outname = fname.split('probe')[0]+'+gem2'+fname.split('probe')[1].split('.dat')[0]+'_ice_from_'+date_gem2+'.csv'


        tt_nn18 = np.zeros_like(sd_values)
        tt_nn5 = np.zeros_like(sd_values)
        tt_nn93 = np.zeros_like(sd_values)
        #find nearest tt and it values to original mp/sd points        
        for i in range(0,tt_nn18.shape[0]):
            dx = sd_points[:,0][i]-grid_x
            dy = sd_points[:,1][i]-grid_y                  
            dg = np.sqrt(dx**2+dy**2)
            dgf = dg.flatten()
            
            #don take values too far away
            if np.min(dgf) > 4:
                tt_nn18[i] = -999; tt_nn5[i] = -999; tt_nn93[i] = -999
            else:
                #find nearest tt and it value
                nn = np.argmin(dgf)
                tt_nn18[i] = output_tt[0].flatten()[nn]
                tt_nn5[i] = output_tt[1].flatten()[nn]
                tt_nn93[i] = output_tt[2].flatten()[nn]

                #there can be nans...
                #replace with mean in the closest n values
                n=3
                while (np.isnan(tt_nn18[i]) and n < 25):
                    nn = np.argpartition(dgf,n)[:n]
                    tmp18 = output_tt[0].flatten()[nn]
                    tmp5 = output_tt[1].flatten()[nn]
                    tmp93 = output_tt[2].flatten()[nn]

                    tt_nn18[i] = np.mean(np.ma.masked_invalid(tmp18))
                    tt_nn5[i] = np.mean(np.ma.masked_invalid(tmp5))
                    tt_nn93[i] = np.mean(np.ma.masked_invalid(tmp93))
                    
                    n = n+1
        
        mask = tt_nn18 == -999
        tt_nn18 = np.ma.array(tt_nn18, mask=mask);tt_nn18 = tt_nn18.compressed()
        tt_nn5 = np.ma.array(tt_nn5, mask=mask);tt_nn5 = tt_nn5.compressed()
        tt_nn93 = np.ma.array(tt_nn93, mask=mask);tt_nn93 = tt_nn93.compressed()
        sd_values = np.ma.array(sd_values, mask=mask);sd_values = sd_values.compressed()
        
        dt = np.ma.array(dt, mask=mask);dt = dt.compressed()
        lon = np.ma.array(lon , mask=mask);lon = lon.compressed()
        lat = np.ma.array(lat, mask=mask);lat = lat.compressed()
        sd_points0 = np.ma.array(sd_points[:,0], mask=mask);sd_points0 = sd_points0.compressed()
        sd_points1 = np.ma.array(sd_points[:,1], mask=mask);sd_points1 = sd_points1.compressed()
        
        it_nn18 = tt_nn18 - sd_values
        it_nn5 = tt_nn5 - sd_values
        it_nn93 = tt_nn93 - sd_values
        print(it_nn18)
        
        #write new csv file with all the ice mass balance variables
        tt = [dt,lon,lat,sd_points0,sd_points1,sd_values,it_nn18,it_nn5,it_nn93]
        table = list(zip(*tt))

        print(outname)
        with open(outname, 'wb') as f:
            #header
            f.write(b'Date/Time, Lon, Lat, Local X, Local Y, Snow Depth (m), Ice Thickness 18kHz ip (m), Ice Thickness 5kHz ip (m), Ice Thickness 93kHz ip (m),\n')
            np.savetxt(f, table, fmt="%s", delimiter=",")

