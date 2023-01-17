import numpy as np
import csv
from pyproj import Proj, transform
from osgeo import gdal, osr
import matplotlib.pyplot as plt
import gc
from scipy.optimize import curve_fit
import warnings

from mpl_toolkits.basemap import Basemap
import rasterio
from pyproj import Transformer

from sklearn.metrics import r2_score

def getColumn(filename, column, delimiter=',', skipinitialspace=False, skipheader=1):
    results = csv.reader(open(filename),delimiter=delimiter,skipinitialspace=skipinitialspace)
    while skipheader>0:
        next(results, None)
        skipheader=skipheader-1
        
    return [result[column] for result in results]


def linreg_model(x,y):
    model = np.polyfit(x,y, 1)
    predict = np.poly1d(model)
    
    r2 = r2_score(y, predict(x))

    x_lin_reg = np.arange(0, max(x)*3,max(x)/2)
    y_lin_reg = predict(x_lin_reg)
    
    n=len(x)
    
    return(x_lin_reg, y_lin_reg, n, r2)




#f1525Hz_hcp_i, f1525Hz_hcp_q, f5325Hz_hcp_i, f5325Hz_hcp_q, f18325Hz_hcp_i, f18325Hz_hcp_q, f63025Hz_hcp_i, f63025Hz_hcp_q, f93075Hz_hcp_i, f93075Hz_hcp_q
def ridge_thick(fname): 
    #f1525Hz_hcp_i
    it1 = getColumn(fname,6, delimiter=',')
    
    #f1525Hz_hcp_q
    it2 = getColumn(fname,7, delimiter=',')

    #f5325Hz_hcp_i
    it3 = getColumn(fname,8, delimiter=',')

    #f5325Hz_hcp_q
    it4 = getColumn(fname,9, delimiter=',')

    #f18325Hz_hcp_i
    it5 = getColumn(fname,10, delimiter=',')

    #f18325Hz_hcp_q
    it6 = getColumn(fname,11, delimiter=',')

    #f63025Hz_hcp_i
    it7 = getColumn(fname,12, delimiter=',')
    
    #f63025Hz_hcp_q
    it8 = getColumn(fname,13, delimiter=',')

    #f93075Hz_hcp_i
    it9 = getColumn(fname,14, delimiter=',')
    
    #f93075Hz_hcp_q
    it10 = getColumn(fname,15, delimiter=',')

    #get lat to check where it has zero values
    lat = getColumn(fname,3, delimiter=',')
    lat = np.array(lat,dtype=np.float)
    
    #prepare lists of channels
    channels = [it1,it2,it3,it4,it5,it6,it7,it8,it9,it10]
    mit1=[];mit2=[];mit3=[];mit4=[];mit5=[];mit6=[];mit7=[];mit8=[];mit9=[];mit10=[]
    output_mit = [mit1,mit2,mit3,mit4,mit5,mit6,mit7,mit8,mit9,mit10]

    for ch in range(0,len(channels)):
        
        #get rid of nans
        channels[ch] = np.array(channels[ch],dtype=np.float)
        channels[ch] = np.ma.masked_invalid(channels[ch]).filled(999)

        #make mean of values between the 0 values for lat (beginning of each point)
        c=0
        c1=0
        m1=0
        fz=True
        
        for i in range(0,len(lat)):
            if lat[i] != 0:
                if channels[ch][i]==999:
                    if c == 0:  #some channels have just nans, we need to mark those and append some dymmy value
                        c1 = 1
                    else:
                        continue
                    
                
                else:
                    m1 = m1+channels[ch][i]
                    c = c+1
                    fz = True
            else:
                if (fz == True) and (c>0): 
                    mm1 = m1/c
                    output_mit[ch].append(mm1)
                    fz = False
                elif c1==1: 
                    output_mit[ch].append(np.nan)
                c=0
                c1=0
                m1=0
                continue
        
    return(mit1,mit2,mit3,mit4,mit5,mit6,mit7,mit8,mit9,mit10)

def ridge_xy(fname):
    x = getColumn(fname,3, delimiter=',')
    y = getColumn(fname,4, delimiter=',')
    
    x = np.array(x,dtype=np.float)
    y = np.array(y,dtype=np.float)
    
    #get lat to check where it has zero values
    lat = getColumn(fname,2, delimiter=',')
    lat = np.array(lat,dtype=np.float)

    #get rid of nans
    x = np.ma.masked_invalid(x).filled(999)
    y = np.ma.masked_invalid(y).filled(999)
        
    #make mean of values between the nn values (beginning of each point)
    c=0
    m1=0; m2=0
    fz=True
    mit1=[]; mit2=[]
    for i in range(0,len(x)):
        if lat[i] != 0:
            if x[i]==999:
                continue
            else:
                m1 = m1+x[i]; m2 = m2+y[i]
                c = c+1
                fz = True
            
        else:
            if (fz == True) and (c>0): 
                mm1 = m1/c; mm2 = m2/c
                mit1.append(mm1); mit2.append(mm2)
                fz = False
            c=0
            m1=0; m2=0
            continue

    return(mit1,mit2)

def semivar(h,lim,val,xx,yy):
    '''A function to create semivariogram parameters. 
    Sum of all squares of all differences between measurements inside each of the loops - divided by sample number and halved (semi-variogram).
    Normally, they can be done in 3-D, but in our case the distance is just along the track
    
    Parameters
    ---------
    h       : distance step in m
    lim     : longest distance in m
    val     : variable (e.g. snow depth)
    xx     : x coordinate in m
    yy     : y coordinate in m
    
    Returns
    ---------
    maxd    : distances
    semivar : semi-var values for each distance
    
    '''
    
    #get a list/array of distances for each point to all other points
    semivar = []
    
    maxd = np.arange(0,lim,h)
    for i in range(0,len(maxd)):
        #print(i)
        
        #for every value
        ssum=0
        scnt=0
        for j in range(0,len(val)):
            dx = xx[j]-xx
            dy = yy[j]-yy
            d = np.sqrt(dx**2+dy**2)            
            #print(d)
            
            #mask all but this bin
            mask = (d > maxd[i]+h) | (d < maxd[i])
            dj = np.ma.array(d,mask=mask)
            sj = np.ma.array(val,mask=mask)
            
            sj = sj.compressed()
            #dj = dj.compressed()
            #print(dj)
            
            ssum = ssum + np.sum((val[j]-sj)**2)
            scnt = scnt + sj.shape[0]
        
        #print(scnt)
        svh = ssum / (scnt * 2)
    
        semivar.append(svh)
        
    return(maxd,semivar)

def polymodel(x,y,lim,deg=1):    
    ## LOOCV selects the correct model
    #for deg in range(1, 5):
        #print('Degree = %d, RSS=%.2f' % (deg, loocv(x, y, np.polyfit, np.polyval, deg)))
    
    model = np.polyfit(x, y, deg)
    predict = np.poly1d(model)

    x_lin_reg = np.arange(0, lim,1)
    y_lin_reg = predict(x_lin_reg)

    return(x_lin_reg,y_lin_reg)
    
def running_stats(x, n):            #n has to be dividable by 2!
        sum1 = np.zeros_like(x)
        sum2 = np.zeros_like(x)
        x2 = x**2
        n2 = int(n/2)
        
        for i in range(n2,len(x)-n2):
            #print(i)
            #print(len(x[i-n2:i+n2]))
            #print(x[i-n2:i+n2])
            #print(np.sum(x[i-n2:i+n2]))
            sum1[i] = np.sum(x[i-n2:i+n2])
            sum2[i] = np.sum(x2[i-n2:i+n2])
            
            #print(sum1[i])
            #print(sum2[i])
        #exit()
        
        mean = sum1/n
        var = (sum2/n - mean**2)
        return (mean,var)
    
def proj_sat(tif,lon0,lat0,head0,spacing=1,band=1,alos=False,ps_pos=False):
    ds = gdal.Open(tif, gdal.GA_ReadOnly) # Note GetRasterBand() takes band no. starting from 1 not 0
    band = ds.GetRasterBand(band)
    arr = band.ReadAsArray()
    #plt.imshow(arr)
    #plt.show()
    #exit()
    
    #lat,lon projection
    outProj = Proj(init='epsg:4326')

    if alos:
        #get lat, lon as bands
        band=ds.GetRasterBand(5)
        lat = band.ReadAsArray()
        band=ds.GetRasterBand(6)
        lon = band.ReadAsArray()

        #scale the values
        arr=10.*np.log10(arr)


    else:
        #construct grid and calculate lat,lon
        
        ## For no. of bands and resolution
        #print(ds.RasterCount, ds.RasterXSize, ds.RasterYSize)
        ## stats about image
        ##min, max, mean std
        #print(band.GetStatistics( True, True ))

        #get the geo transform matrix
        xoffset, px_w, rot1, yoffset, rot2, px_h = ds.GetGeoTransform()
        print(xoffset, px_w, rot1, yoffset, px_h, rot2)

        #pixel coordinates
        #x, y = np.mgrid[0:ds.RasterXSize, 0:ds.RasterYSize]

        #ALS data has 0.5 meter resolution, this is way more than needed, use 10m resolution for beginning...
        x, y = np.mgrid[0:ds.RasterXSize:spacing, 0:ds.RasterYSize:spacing]
        arr = arr[::spacing,::spacing]

        print(x.shape,y.shape)
        print(arr.shape)

        # supposing x and y are your pixel coordinate this 
        # is how to get the coordinate in space.
        posX = px_w * x + rot1 * y + xoffset
        posY = rot2 * x + px_h * y + yoffset

        # shift to the center of the pixel
        posX += px_w / 2.0
        posY += px_h / 2.0

        # get CRS from dataset 
        crs = osr.SpatialReference()
        crs.ImportFromWkt(ds.GetProjectionRef())
        inProj=crs.ExportToProj4()
        print(inProj)
        
        #transform coordinates to lat,lon
        lon,lat = transform(inProj,outProj,posX, posY)
         
        del posX,posY
        gc.collect()

    #transform to the FloeNavi local coordinates
    FloeNaviProj = Proj('+proj=stere +lat_0=%f +lon_0=%f +x_0=0 +y_0=0 +ellps=WGS84'%(lat0,lon0))
    x,y = transform(outProj,FloeNaviProj,lon,lat)
    
    del lon,lat
    gc.collect()

    #check orgin location - should be sub-meter away from 0,0
    xref,yref = transform(outProj,FloeNaviProj,lon0,lat0)
    print(xref,yref)
    
    if ps_pos:
        #if position is not from FloeNavi but from PS, apply an offest between ship and the ref station on ice
        ##2019/12/31 11:18:00	117.877961	86.588972	207.9
        #lon0=117.877961
        #lat0=86.588972
        #xref,yref = transform(outProj,FloeNaviProj,lon0,lat0)
        
        #print(xref,yref)
        ##exit()
        ##difference in x,y
        #0.0023430867721458927 0.0555309670589043
        #53.43683464292577 3.5778224217515917
        x=x+53
        y=y+3


    print('rotate')
    ##Rotate into reference system of base station
    ##The heading offset is 90: to get from default positive x-axis to positive y-axis
    x_temp, y_temp = x.copy(), y.copy()
    #heading_radian = np.deg2rad(-1.0 * self.refstat.heading + self.base_heading + self.heading_offset_deg)
    heading_radian = np.deg2rad(-1.0 * (head0-90))

    rot_x = np.cos(heading_radian) * x_temp + np.sin(heading_radian) * y_temp
    rot_y = -1.0 * np.sin(heading_radian) * x_temp + np.cos(heading_radian) * y_temp
    
    del x,y,x_temp,y_temp
    gc.collect()
   
    return(arr,rot_x,rot_y)

def proj_rov(tif,lon0,lat0,head0,lon_origin,lat_origin):
    ds = gdal.Open(tif, gdal.GA_ReadOnly) # Note GetRasterBand() takes band no. starting from 1 not 0
    band = ds.GetRasterBand(1)
    arr = band.ReadAsArray()
    #plt.imshow(arr)
    #plt.show()
    #exit()
    
    #lat,lon projection
    outProj = Proj(init='epsg:4326')

    #construct grid and calculate lat,lon
    #get the geo transform matrix
    xoffset, px_w, rot1, yoffset, rot2, px_h = ds.GetGeoTransform()
    print(xoffset, px_w, rot1, yoffset, px_h, rot2)
    
    #degrees longitude are too large for 87N, adjust
    px_w=px_w*18

    #pixel coordinates
    x, y = np.mgrid[0:ds.RasterXSize, 0:ds.RasterYSize]

    # supposing x and y are your pixel coordinate this 
    # is how to get the coordinate in space.
    posX = px_w * x + rot1 * y + xoffset
    posY = rot2 * x + px_h * y + yoffset

    # shift to the center of the pixel
    posX += px_w / 2.0
    posY += px_h / 2.0

    # get CRS from dataset 
    crs = osr.SpatialReference()
    crs.ImportFromWkt(ds.GetProjectionRef())
    inProj=crs.ExportToProj4()
    print(inProj)
    
    #transform coordinates to lat,lon
    lon,lat = transform(inProj,outProj,posX, posY)

    #shift to the drive hole origin
    lon = lon+lon_origin-1
    lat = lat+lat_origin-1
        
    del posX,posY
    gc.collect()

    #transform to the FloeNavi local coordinates
    FloeNaviProj = Proj('+proj=stere +lat_0=%f +lon_0=%f +x_0=0 +y_0=0 +ellps=WGS84'%(lat0,lon0))
    x,y = transform(outProj,FloeNaviProj,lon,lat)
    
    del lon,lat
    gc.collect()

    #check orgin location - should be sub-meter away from 0,0
    xref,yref = transform(outProj,FloeNaviProj,lon0,lat0)
    print(xref,yref)

    print('rotate')
    ##Rotate into reference system of base station
    ##The heading offset is 90: to get from default positive x-axis to positive y-axis
    x_temp, y_temp = x.copy(), y.copy()
    #heading_radian = np.deg2rad(-1.0 * self.refstat.heading + self.base_heading + self.heading_offset_deg)
    heading_radian = np.deg2rad(-1.0 * (head0-90))

    rot_x = np.cos(heading_radian) * x_temp + np.sin(heading_radian) * y_temp
    rot_y = -1.0 * np.sin(heading_radian) * x_temp + np.cos(heading_radian) * y_temp
    
    del x,y,x_temp,y_temp
    gc.collect()
   
    return(arr,rot_x,rot_y)

def floenavi_coords(dt,lat,lon,refdt,reflat,reflon,refhead):

    #lat,lon projection
    outProj = Proj(init='epsg:4326')

    rot_x_list=[]
    rot_y_list=[]
    for i in range(0,len(dt)):
        
        #find closest date
        k = np.argmin(np.abs(np.array(refdt) - dt[i]))
        #print('reference: ',refdt[k])
        #print('snow pit: ',dt[i])
        
        lat0=reflat[k]
        lon0=reflon[k]
        head0=refhead[k]
            
        #transform to the FloeNavi local coordinates
        FloeNaviProj = Proj('+proj=stere +lat_0=%f +lon_0=%f +x_0=0 +y_0=0 +ellps=WGS84'%(lat0,lon0))
        x,y = transform(outProj,FloeNaviProj,lon[i],lat[i])
            
        #if ps_pos:
            #x=x+53
            #y=y+3
            
        ##Rotate into reference system of base station
        ##The heading offset is 90: to get from default positive x-axis to positive y-axis
        heading_radian = np.deg2rad(-1.0 * (head0-90))

        rot_x = np.cos(heading_radian) * x + np.sin(heading_radian) * y
        rot_y = -1.0 * np.sin(heading_radian) * x + np.cos(heading_radian) * y
        
        rot_x_list.append(rot_x)
        rot_y_list.append(rot_y)

    return(rot_x_list,rot_y_list)

def floenavi_coords_buoy(dt,lon,lat,refdt,reflon,reflat,refhead):

    #lat,lon projection
    outProj = Proj(init='epsg:4326')

    #find closest date
    k = np.argmin(np.abs(np.array(refdt) - dt))
    #print('reference: ',refdt)
    #print('buoy: ',dt[k])
    
    lat0=reflat
    lon0=reflon
    head0=refhead
        
    #transform to the FloeNavi local coordinates
    FloeNaviProj = Proj('+proj=stere +lat_0=%f +lon_0=%f +x_0=0 +y_0=0 +ellps=WGS84'%(lat0,lon0))
    x,y = transform(outProj,FloeNaviProj,lon[k],lat[k])
    
    ##Rotate into reference system of base station
    ##The heading offset is 90: to get from default positive x-axis to positive y-axis
    heading_radian = np.deg2rad(-1.0 * (head0-90))

    rot_x = np.cos(heading_radian) * x + np.sin(heading_radian) * y
    rot_y = -1.0 * np.sin(heading_radian) * x + np.cos(heading_radian) * y
    
    return(rot_x,rot_y)

def get_ice_mode(it,irbins):
    
    hist = np.histogram(it,bins=irbins)
    srt = np.argsort(hist[0])                           #indexes that would sort the array
    mm = srt[-1]                                        #same as: np.argmax(hist[0])
    mm1 = np.argmax(hist[0])
    mo = (hist[1][mm] + hist[1][mm+1])/2           #take mean of the bin for the mode value

    return(mo)

def minang_tri(vert):
  #find smallest angle to filter out too acute triangles
  
  #sides of triangle
  ta = np.sqrt((vert[1,0]-vert[0,0])**2+(vert[1,1]-vert[0,1])**2)
  tb = np.sqrt((vert[2,0]-vert[1,0])**2+(vert[2,1]-vert[1,1])**2)
  tc = np.sqrt((vert[2,0]-vert[0,0])**2+(vert[2,1]-vert[0,1])**2)
  sides = [ta,tb,tc]
  srt = min(sides)
  srtid = np.argmin(sides)
  lng = np.delete(sides,srtid)
  
  #law of cosine
  #minang(ii) = acosd((sides(1)^2+sides(2)^2-shortest^2)/2/sides(1)/sides(2))
  minang = np.degrees(np.arccos((lng[0]**2+lng[1]**2-srt**2)/2/lng[0]/lng[1]))

  return(minang)

def deformation(vert,uvert,vvert):

  #smallest angle of triangle
  minang = minang_tri(vert)
  
  ##area of triangle
  #Hutchings etal, 2012 (ISPOL)
  area = .5* (vert[0,0]*vert[1,1] - vert[0,1]*vert[1,0] + vert[1,0]*vert[2,1] - vert[1,1]*vert[2,0] + vert[2,0]*vert[0,1] - vert[2,1]*vert[0,0])
  if area < 0: print('not counter-clockwise oriented triangle!'); exit()
  
  #some filtering to throw out the erroneous GPS positioning. If the accuracy is 2m.
  if area < 1: print(area); return 0,0,0,0,0,0	#Hutchings etal, 2011 (SEDNA)
    
  #calculate line integrals
  dux = (.5 / area) * (
    (uvert[1]+uvert[0])*(vert[1,1]-vert[0,1])+
    (uvert[2]+uvert[1])*(vert[2,1]-vert[1,1])+
    (uvert[0]+uvert[2])*(vert[0,1]-vert[2,1]) )
  
  duy = -(.5 / area) * (
    (uvert[1]+uvert[0])*(vert[1,0]-vert[0,0])+
    (uvert[2]+uvert[1])*(vert[2,0]-vert[1,0])+
    (uvert[0]+uvert[2])*(vert[0,0]-vert[2,0]) )
  
  dvx = (.5 / area) * (
    (vvert[1]+vvert[0])*(vert[1,1]-vert[0,1])+
    (vvert[2]+vvert[1])*(vert[2,1]-vert[1,1])+
    (vvert[0]+vvert[2])*(vert[0,1]-vert[2,1]) )
    
  dvy = -(.5 / area) * (
    (vvert[1]+vvert[0])*(vert[1,0]-vert[0,0])+
    (vvert[2]+vvert[1])*(vert[2,0]-vert[1,0])+
    (vvert[0]+vvert[2])*(vert[0,0]-vert[2,0]) )
  
  return dux,duy,dvx,dvy,minang,area

def logfit(x_data,y_data):
    #fit a logarithmic function to this data
    warnings.filterwarnings("ignore")

    def func(x, a, b, c): # x-shifted log
        return a*np.log(x + b)+c

    # these are the same as the scipy defaults
    initialParameters = np.array([1.0, 1.0, 1.0])

    fittedParameters, pcov = curve_fit(func, x_data, y_data, initialParameters)

    modelPredictions = func(x_data, *fittedParameters) 

    absError = modelPredictions - y_data

    SE = np.square(absError) # squared errors
    MSE = np.mean(SE) # mean squared errors
    RMSE = np.sqrt(MSE) # Root Mean Squared Error, RMSE
    Rsquared = 1.0 - (np.var(absError) / np.var(y_data))

    print('Parameters:', fittedParameters)
    print('RMSE:', RMSE)
    print('R-squared:', Rsquared)


    # create data for the fitted equation plot
    x_model = np.linspace(min(x_data), max(x_data))
    y_model = func(x_model, *fittedParameters)

    return(x_model,y_model, RMSE, Rsquared)

def plot_gtiff(fpath):
    """
    Args
        fpath :string: path to geotiff file
    """
    with rasterio.open(fpath) as src:
        band1 = src.read(1)
        trs = src.transform
        height = band1.shape[0]
        width = band1.shape[1]
        cols, rows = np.meshgrid(np.arange(width), np.arange(height))
        xs, ys = rasterio.transform.xy(src.transform, rows, cols)
        transformer = Transformer.from_crs(src.crs, "EPSG:4326", src.crs)

        lons= np.array(xs)
        lats = np.array(ys)
        lon, lat = transformer.transform(lons,lats)

        fig, ax = plt.subplots(1,1,figsize=(25,15))

        # setup mercator map projection.
        map = Basemap(llcrnrlon=-2.,llcrnrlat=-70.51,urcrnrlon=10,urcrnrlat=-69,\
                    rsphere=(6378137.00,6356752.3142),\
                    resolution='i',projection='merc',\
                    lat_0=-68.,lon_0=5.,lat_ts=-70.)

        map.pcolormesh(lat,lon, band1,latlon=True,vmin=50,vmax=100)

        map.drawcoastlines()
        map.fillcontinents()
        map.drawparallels(np.arange(-90,90,1),labels=[1,1,0,1])

        map.drawmeridians(np.arange(-180,180,1),labels=[1,1,0,1])

def smooth(x,window_len=11,window='hanning'):
        if x.ndim != 1:
                raise ValueError("smooth only accepts 1 dimension arrays.")
        if x.size < window_len:
                raise ValueError("Input vector needs to be bigger than window size.")
        if window_len<3:
                return x
        if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
                raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")
        s=np.r_[2*x[0]-x[window_len-1::-1],x,2*x[-1]-x[-1:-window_len:-1]]
        if window == 'flat': #moving average
                w=np.ones(window_len,'d')
        else:  
                w=eval('np.'+window+'(window_len)')
        y=np.convolve(w/w.sum(),s,mode='same')
        return y[window_len:-window_len+1]
