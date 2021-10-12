import numpy as np
from osgeo import gdal, osr
import matplotlib.pyplot as plt
from datetime import datetime
from glob import glob
from tt_func import getColumn

#This is the TSX scene for 2019-11-14 surrounding the ship, as we discussed. 
#It's cropped by a rectangle in the epsg:3575 projection.
#time stamp is 20191114T042434_20191114T042456


ds = gdal.Open('../data/mosaic_floe_cut3575.tif', gdal.GA_ReadOnly) # Note GetRasterBand() takes band no. starting from 1 not 0
band = ds.GetRasterBand(1)
arr = band.ReadAsArray()
plt.imshow(arr)
plt.show()


# For no. of bands and resolution
print(ds.RasterCount, ds.RasterXSize, ds.RasterYSize)
# stats about image
#min, max, mean std
print(band.GetStatistics( True, True ))


#get the geo transform matrix
#xoffset, px_w, rot1, yoffset, px_h, rot2 = ds.GetGeoTransform()
#print(xoffset, px_w, rot1, yoffset, px_h, rot2)
#correct?
xoffset, px_w, rot1, yoffset, rot2, px_h = ds.GetGeoTransform()
print(xoffset, px_w, rot1, yoffset, px_h, rot2)
#exit()

#pixel coordinates
x, y = np.mgrid[0:ds.RasterXSize, 0:ds.RasterYSize]
#print(x,y)

# supposing x and y are your pixel coordinate this 
# is how to get the coordinate in space.
posX = px_w * x + rot1 * y + xoffset
posY = rot2 * x + px_h * y + yoffset

# shift to the center of the pixel
posX += px_w / 2.0
posY += px_h / 2.0

#print(posX,posY)

# get CRS from dataset 
crs = osr.SpatialReference()
crs.ImportFromWkt(ds.GetProjectionRef())
inProj=crs.ExportToProj4()
print(inProj)

from pyproj import Proj, transform
outProj = Proj(init='epsg:4326')
lon,lat = transform(inProj,outProj,posX, posY)
print(lon,lat)

#instead outProj should be FloeNavi proj!!!
#proj='stere', lon_0=lon_0, lat_0=lat_0, lat_ts=lat_0, ellps='WGS84'
#lon_0 = np.nanmedian(self.refstat.longitude)
#lat_0 = np.nanmedian(self.refstat.latitude)
#ref station then:
#2019-11-14 04:24:00,118.16217076435768,86.15982474551613,300.56654264271526,4.141477302772724,0.6866326529852491

FloeNaviProj = Proj('+proj=stere +lat_0=86.15982474551613 +lon_0=118.16217076435768 +x_0=0 +y_0=0 +ellps=WGS84')
x,y = transform(outProj,FloeNaviProj,lon,lat)
print(x,y)


xref,yref = transform(outProj,FloeNaviProj,118.16217076435768,86.15982474551613)
print(xref,yref)


##Rotate into reference system of base station
##The heading offset is 90: to get from default positive x-axis to positive y-axis
x_temp, y_temp = x.copy(), y.copy()
#heading_radian = np.deg2rad(-1.0 * self.refstat.heading + self.base_heading + self.heading_offset_deg)
heading_radian = np.deg2rad(-1.0 * (300.56-90))            
rot_x = np.cos(heading_radian) * x_temp + np.sin(heading_radian) * y_temp
rot_y = -1.0 * np.sin(heading_radian) * x_temp + np.cos(heading_radian) * y_temp





print(x.shape)
print(y.shape)
print(arr.shape)


CS = plt.contourf(rot_x, rot_y, arr.T, 15,
                  vmax=abs(arr).max(), vmin=-abs(arr).max())
plt.colorbar()  # draw colorbar

#plt.scatter(rot_x, rot_y, c=arr.T)

#plot some transect tracks
inpath = '../data/MCS/GEM2_thickness/01-ice-thickness/'
flist = glob(inpath+'*PS122-[1-2]?*/mosaic-*-*-gem2-*-track-icecs-xy.csv')
flist.sort()

for i in range(0,len(flist)):
    
    fname = flist[i]

    xx = getColumn(fname,3, delimiter=',', magnaprobe=False)
    xx = np.array(xx,dtype=np.float)
    
    yy = getColumn(fname,4, delimiter=',', magnaprobe=False)
    yy = np.array(yy,dtype=np.float)
    
    #GEM-2 files contain nans and zeros
    xx = np.ma.masked_invalid(xx).compressed()
    yy = np.ma.masked_invalid(yy).compressed()
    
    xx = np.ma.array(xx,mask=xx==0).compressed()
    yy = np.ma.array(yy,mask=yy==0).compressed()
    
    #plot GEM-tracks
    plt.plot(xx,yy,'o',ms=1)
 


plt.show()

exit()


#get datetime
dt = datetime(2019,11,14,4,24,34)
print(dt)

#ref station then:
#2019-11-14 04:24:00,118.16217076435768,86.15982474551613,300.56654264271526,4.141477302772724,0.6866326529852491

dta = np.empty_like(lon, dtype='datetime64[s]')
dta[:] = dt

#write out cvs files that floenavi expects
outpath = '../data/'
outname = outpath+'PS122-1_TSX-track.csv'

tt = [dta.flatten(),lon.flatten(),lat.flatten()]
table = list(zip(*tt))


print(outname)
with open(outname, 'wb') as f:
    np.savetxt(f, table, fmt="%s", delimiter=",")



