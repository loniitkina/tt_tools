import numpy as np
from glob import glob
from tt_func import getColumn
from scipy.signal import savgol_filter
from scipy.interpolate import griddata
from scipy import ndimage
from datetime import datetime
import matplotlib.pyplot as plt

#grid parameters
step = 2        #grid spacing in meters 
#step = 1        #for ridges
#step = 5
limit = step*2  #how far from MP coordinate to search 
#limit = 5       #some equivalent to GEM-2 footprint or max thickness measured by GEM-2?
scale_limit=False   #depending on the MP spatial resolution
#smoothing from 0.2m reslution by continious walking spacing
#resolution is much more fine when we stop or cross ridges
#aim for something similar to instrument footprint and search step
#1m ~MP spacing
#window = 5
#4m GEM-2 footprint on level ice of 1m
window = 21
polyorder = 3

#method_gem2 = 'linear'  #GEM-2 data needs to be smoothed >> problem: max distance cant be specified! This method gives strange results
method_gem2 = 'nearest'
method_mp = 'nearest'   #at dense grids every measurement should be used separately

#MP file extension depends on the leg
ext_mp='.dat'
#ext_mp='.csv'

#show gridded data plot
show=True
show=False

#make mp+gem2 table output
table_output=True

outpath = '../plots_ridges/'
outpath_data = '../data/ridges_multif/'

#MP
inpath_snow = '../data/MCS/MP/'

#GEM-2
inpath_ice = '../data/MCS/GEM2_thickness/01-ice-thickness/'

#subset locations
loc1=None

#location
#loc = 'Nloop'
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

#dates = ['20191024','20191031','20191107','20191114','20191121','20191128','20191205','20191219',
       #'20200102','20200109','20200130','20200220','20200305','20200320','20200326','20200403',
       #'20200424','20200430','20200507'] 

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
        #'20200102','20200109','20200130','20200220','20200227',
        #'20200305','20200330','20200426','20200507']

#leg4
#loc = 'transect'
#date = '20200629'  #MP entire, GEM-2 majority
#date = '20200630'  #complete data!  
#date = '20200705'  #decent spacing, 2m
#date = '20200706'
#date = '20200707'
#date = '20200708'
#date = '20200710'  #1.8m spacing!
#dates = ['20200629','20200630','20200705','20200710','20200720']
#dates = ['20200720']    #Melinda's pick

#roads and recons, has no MP data
#loc = 'recon'; step=5 
#what else could be added here: 20200102-roads between the transects, 20200108-road to Fort Ridge, 20200305-maybe some roads
#dates = ['20200108']; inpath_ice = '../data/MCS/GEM2_thickness/09-ridges-recal/'   #road to Fort Ridge
#dates = ['20200228']   #airport recon
#dates = ['20200226']   #Darnitsyn Lead
#dates = ['20200107']   #Dark site FYI
#dates = ['20200126']   #lead Event
#dates = ['20200221']   #Christian and Erik recon
#dates = ['20200123']    #long transect
#dates = ['20200227'] #February roads
#table_output=True  #not useful
#limit = step*2            #no need to search far
#dates =['20200108','20200228','20200226','20200107','20200126']

#special transects of legs 1-2
#loc = 'special'; step=5
#date = '20200107'   #Dark site FYI
#date = '20200115'   #Dark site SYI (pulk tipped once in the ridges)
#date = '20200123'  #long transect (and lead event sampling without GEM-2)
#date = '20200126'  #lead event (different track than on 23 Jan)
#date = '20200226'   #lead scounting at the Dranitsyn lead (that did not work out...)
#dates = ['20200107','20200115','20200123','20200126','20200226']

#location - ridges
#only for ridges that were surveyed with a pulk: othrwise use script tt_grid_ridge.py
loc = 'ridgeFR1'    #installation (also very close to snow)
dates = ['20200305']

#loc = 'ridgeA1'
#loc = 'ridgeA2'
#loc = 'ridgeA3'
#dates = ['20200410']

#loc = 'ridgeD'
#date = '20200410'
#date = '20200416'
#date = '20200424'
#date = '20200430'
#date = '20200507'
#dates = ['20200410','20200416','20200424','20200430','20200507']

#loc = 'ridgeE'
#dates = ['20200424']

#loc = 'ridge'  #ridge of leg 5
#dates = ['20200828','20200918']    



for dd in range(0,len(dates)):
    date=dates[dd]
    print(date)


    date_gem2 = date

    print(loc)
    print(date_gem2)

    #we need to merge all GEM-2 survery for that day first
    #coordinates
    xx = []
    yy = []
    fname = glob(inpath_ice+date_gem2+'*/*-track-icecs-xy.csv')
    for fn in fname:
        print(fn)
        x = getColumn(fn,3)
        y = getColumn(fn,4)
    
        xx.extend(x); yy.extend(y)
        
    xx_full = np.array(xx,dtype=float)
    yy_full  = np.array(yy,dtype=float)
        
    #GEM-2 data
    tt1 = []; tt2 = []; tt3 = []; tt4 = []; tt5 = []; tt6 = [];tt7 = []; tt8 = []; tt9 = [];tt10 = []
    ts_gem=[]
    fname_ice = glob(inpath_ice+date_gem2+'*/*-channel-thickness.csv')
    for fn in fname_ice:
        print(fn)
        #time, record_id, longitude, latitude, xc, yc, f1525Hz_hcp_i, f1525Hz_hcp_q, f5325Hz_hcp_i, f5325Hz_hcp_q, f18325Hz_hcp_i, f18325Hz_hcp_q, f63025Hz_hcp_i, f63025Hz_hcp_q, f93075Hz_hcp_i, f93075Hz_hcp_q

        t1 = getColumn(fn,6); t2 = getColumn(fn,7); t3 = getColumn(fn,8); t4 = getColumn(fn,9); t5 = getColumn(fn,10)
        t6 = getColumn(fn,11); t7 = getColumn(fn,12); t8 = getColumn(fn,13); t9 = getColumn(fn,14); t10 = getColumn(fn,15) 
        ts = getColumn(fn,0)

        #floenavi scripts looses coordinates at the start and end of the file
        tt1.extend(t1[1:-1]); tt2.extend(t2[1:-1]); tt3.extend(t3[1:-1]);tt4.extend(t4[1:-1]);tt5.extend(t5[1:-1])
        tt6.extend(t6[1:-1]); tt7.extend(t7[1:-1]); tt8.extend(t8[1:-1]);tt9.extend(t9[1:-1]);tt10.extend(t10[1:-1])
        ts_gem.extend(ts[1:-1])
        
    tt1 = np.array(tt1,dtype=float);tt2 = np.array(tt2,dtype=float);tt3 = np.array(tt3,dtype=float);tt4 = np.array(tt4,dtype=float);tt5 = np.array(tt5,dtype=float)
    tt6 = np.array(tt6,dtype=float);tt7 = np.array(tt7,dtype=float);tt8 = np.array(tt8,dtype=float);tt9 = np.array(tt9,dtype=float);tt10 = np.array(tt10,dtype=float)
    
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
    
    #MP
    if loc=='recon':
        #rcon data is GEM-2 only - get dummy values with reduced spacing comparing to GEM-2, usually ski-doo - fast motion and standing...
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
    else:
        #get magnaprobe track file
        fname = glob(inpath_snow+'*/magnaprobe-transect-'+date+'*'+loc+'-track-icecs-xy_corr.csv')[0]
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


        #read in magnaprobe data
        fname = fname.split('-track')[0]+ext_mp
        print(fname)
        
        snod = getColumn(fname,3, delimiter=',', skipheader=4)
        snod = np.array(snod,dtype=float)[:-2]/100             #convert from cm to m
        #change all negative data to zero
        snod = np.where(snod<0,0,snod)
                
    #lateral movement out of the grid at the end of CO2 - just shift in
    if date == '20200507' and loc=='Sloop':
        mxx = mxx+150
        xx_full = xx_full+150
    
    #####################################################################################################################################3
    #lets make a regular grid with 'step' m spacing, corresponding to the CO local coordinate boundaries
    grid_x, grid_y = np.mgrid[-950:820:step, -1200:650:step]
    extent=(-950,820,-1200,650)
    
    #whole CO
    if loc == 'recon' or loc == 'special':
        grid_x, grid_y = np.mgrid[-1300:1500:step, -850:1100:step]
        extent=(-1300,1500,-850,1100)

    #ridge transects
    if 'ridge' in loc and date != '20200828' and date != '20200918':
        print('Ridge!')
        
        grid_x, grid_y = np.mgrid[200:900:step, -600:100:step]
        extent=(200,900,-600,100)

    
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
    if loc == 'recon':
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
    channels = [tt1,tt2,tt3,tt4,tt5,tt6,tt7,tt8,tt9,tt10]
    ch_name =  ['_f1525Hz_hcp_i','_f1525Hz_hcp_q', '_f5325Hz_hcp_i', '_f5325Hz_hcp_q', '_f18325Hz_hcp_i',
                '_f18325Hz_hcp_q', '_f63025Hz_hcp_i', '_f63025Hz_hcp_q', '_f93075Hz_hcp_i','_f93075Hz_hcp_q']
    grid_mit1=[];grid_mit2=[];grid_mit3=[];grid_mit4=[];grid_mit5=[];grid_mit6=[];grid_mit7=[];grid_mit8=[];grid_mit9=[];grid_mit10=[]
    output_tt = [grid_mit1,grid_mit2,grid_mit3,grid_mit4,grid_mit5,grid_mit6,grid_mit7,grid_mit8,grid_mit9,grid_mit10]
    
    for ch in range(0,len(channels)):
        print(ch_name[ch])
        #print(channels[ch])
        #get all original coordinates for each channel
        xx = xx_full.copy()
        yy = yy_full.copy()        
        
        #there can be nans in the thickness data, fix this before we proceed
        #also there may be negative values
        tt = np.nan_to_num(channels[ch], nan=-9999)
        tt = np.ma.array(tt,mask=tt<0)
        
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
        
        #smoothing to avoid extreme values - this is NN interpolation!
        if len(tt)>0:
            tt = savgol_filter(tt, window, polyorder)

            points = np.column_stack((xx,yy))
            values = tt
        
            grid_tt = griddata(points, values, (grid_x, grid_y), method=method_gem2)

            #difference = sea ice thickness
            grid_it = grid_tt - grid_sd

            #keep the original grid for nn search later
            output_tt[ch] = grid_tt.copy()
            
            if show==True:
                ##lets check how this looks like
            
                #ensure that we have data for exactly same grid points
                data_mask = (np.isnan(grid_sd)) | (np.isnan(grid_tt)) | (mask_g == 1)
                grid_sd = np.ma.array(grid_sd,mask=data_mask).filled(np.nan)
                grid_tt = np.ma.array(grid_tt,mask=data_mask).filled(np.nan)
                grid_it = np.ma.array(grid_it,mask=data_mask).filled(np.nan)
            
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

    ##########################################################################################################
    if table_output==True:
        #write out the ice mass balance transect collocated tables
        
        #create output name
        stp = str(step)
        outname = outpath_data+'mosaic_gem-2+mp_'+date+'_'+loc+'_'+stp+'.csv'

        tt_nn = np.zeros((len(channels),len(sd_values)))
        
        #during melt perod the grid is shifted and rotated, match to winter locations - centered to 20200630
        if loc == 'transect':
            sd_points_corr = np.zeros_like(sd_points)
            grid_x_corr = ndimage.rotate(grid_x, 40, reshape=False,order=0,mode='nearest')
            grid_y_corr = ndimage.rotate(grid_y, 40, reshape=False,order=0,mode='nearest')
            grid_x_corr = grid_x_corr+1320
            grid_y_corr = grid_y_corr+10
        
        #find nearest tt and it values to original mp/sd points        
        for i in range(0,sd_values.shape[0]):
            dx = sd_points[:,0][i]-grid_x
            dy = sd_points[:,1][i]-grid_y                  
            dg = np.sqrt(dx**2+dy**2)
            
            #find nearest tt and it value
            dgf = dg.flatten()
            nn = np.argmin(dgf)
            
            for ch in range(0,len(channels)):
                if len(output_tt[ch]) > 0:
                    tt_nn[ch][i] = output_tt[ch].flatten()[nn]
        
            #during melt perod the grid is shifted and rotated, match to winter locations
            if loc == 'transect':
                        
                sd_points_corr[i,0] = grid_x_corr.flatten()[nn]
                sd_points_corr[i,1] = grid_y_corr.flatten()[nn]
            
        #convert to ice thickness
        if len(tt_nn[ch]) > 0:    
            it_nn = tt_nn - sd_values
        
        #write new csv file with all the ice mass balance variables
        tt = [dt,lon,lat,sd_points[:,0],sd_points[:,1],sd_values,it_nn[0],it_nn[1],it_nn[2],it_nn[3],it_nn[4],it_nn[5],it_nn[6],it_nn[7],it_nn[8],it_nn[9]]
        
        if loc == 'transect':
            tt = [dt,lon,lat,sd_points_corr[:,0],sd_points_corr[:,1],sd_values,it_nn[0],it_nn[1],it_nn[2],it_nn[3],it_nn[4],it_nn[5],it_nn[6],it_nn[7],it_nn[8],it_nn[9]]
        
        table = list(zip(*tt))

        print(outname)
        with open(outname, 'wb') as f:
            #header
            f.write(b'Date/Time, Lon, Lat, Local X, Local Y, Snow Depth (m), Ice Thickness f1525Hz_hcp_i (m), Ice Thickness f1525Hz_hcp_q (m), Ice Thickness f5325Hz_hcp_i (m), Ice Thickness f5325Hz_hcp_q (m), Ice Thickness f18325Hz_hcp_i (m), Ice Thickness f18325Hz_hcp_q (m), Ice Thickness f63025Hz_hcp_i (m),Ice Thickness f63025Hz_hcp_q (m), Ice Thickness f93075Hz_hcp_i (m), Ice Thickness f93075Hz_hcp_q (m)\n')
            np.savetxt(f, table, fmt="%s", delimiter=",")
