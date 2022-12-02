import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import rfft, rfftfreq
from scipy.stats import chi2
from datetime import datetime
import locale

inpath_grid = '../data/grids_AGU/'
outpath = '../plots_revision/'
step = 1
stp = str(step)
method_gem2 = 'nearest'
ch_name = '_18kHz'
loc = 'Sloop'

dates = ['20191031','20191107','20191114','20191205',   '20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227','20200305','20200330','20200406','20200426','20200507']

selection = ['20191031','20191107','20191114','20191205','20200102','20200109','20200130','20200220','20200227','20200305','20200330','20200426']  #best data

##level ice triangle sides - pick one
#per - perpendicular to PS
#par - parallel to PS
#dia - diagonal to PS
#par+dia - parallel and diagonal
#all - whole triangle on the level ice
suff = '_all'
#suff = '_per'
#suff = '_par'
#suff = '_dia'

inf = inpath_grid+loc+'_'+stp+'m_'+method_gem2+ch_name+'_track2.npz'
data = np.load(inf)
transect_snow = data['snow']
transect_ice = data['ice']

accsi=[]
accit=[]

fig1 = plt.figure(figsize=(18,5))
fx = fig1.add_subplot(122)
#fx.set_xlabel('Frequency ($m^{-1}$)', fontsize=20)
fx.set_xlabel('Wavelength (m)', fontsize=20)
fx.set_ylabel('Fourier power spectrum', fontsize=20)
fx.tick_params(axis="x", labelsize=14)
fx.tick_params(axis="y", labelsize=14)


gx = fig1.add_subplot(121)
#gx.set_xlabel('Frequency ($m^{-1}$)', fontsize=20)
gx.set_xlabel('Wavelength (m)', fontsize=20)
gx.set_ylabel('Fourier power spectrum', fontsize=20)
gx.tick_params(axis="x", labelsize=14)
gx.tick_params(axis="y", labelsize=14)


if suff=='_per':
    fx.set_ylim(0,.1)
fx.set_xscale('log')
#frequnecy scale
#fx.set_xlim(0.0066,.2)
#fx.set_xticks([0.0066,0.01,.0142,.02,.0286,.04,.066,.1,.143,0.2])
#fx.set_xticklabels([r'$\frac{1}{150}$',r'$\frac{1}{100}$',r'$\frac{1}{70}$',r'$\frac{1}{50}$',r'$\frac{1}{35}$',r'$\frac{1}{25}$',r'$\frac{1}{15}$',r'$\frac{1}{10}$',r'$\frac{1}{7}$',r'$\frac{1}{5}$'])
#wavelenght scale
fx.set_xlim(5,150)
fx.grid(which='both',axis='x')

#gx.set_ylim(0,.2)
gx.set_xscale('log')
#frequnecy scale
#gx.set_xlim(0.0066,.2)  #from 150m to 5m!
#gx.set_xticks([0.0066,0.01,.0142,.02,.0286,.04,.066,.1,.143,0.2])
#gx.set_xticklabels([r'$\frac{1}{150}$',r'$\frac{1}{100}$',r'$\frac{1}{70}$',r'$\frac{1}{50}$',r'$\frac{1}{35}$',r'$\frac{1}{25}$',r'$\frac{1}{15}$',r'$\frac{1}{10}$',r'$\frac{1}{7}$',r'$\frac{1}{5}$'])
#wavelenght scale
gx.set_xlim(5,150)
gx.grid(which='both',axis='x')

colors = plt.cm.rainbow(np.linspace(0, 1, len(dates)))

#for dd in range(3,19):
for dd in range(0,len(dates)-2):
    
    date=dates[dd+2]
    
    #get the date format that the publisher wants
    dt = datetime.strptime(date, '%Y%m%d')
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    datel = datetime.strftime(dt, '%b %d, %Y')
    print(datel)
    
    if date in selection:
    
        mxx = transect_snow[:,0]    #these are MP coordinates from 20200116
        myy = transect_snow[:,1]

        #get distances between points
        dx = mxx[1:]-mxx[:-1]
        dy = myy[1:]-myy[:-1]
        md = np.sqrt(dx**2+dy**2)
        x = np.zeros_like(mxx)
        x[1:] = np.cumsum(md)
        
        si = transect_snow[:,dd+2]
        it = transect_ice[:,dd+2]

        #all level ice between 0 and 600m distance
        #level ice is typically thiner than 2m (start of the winter rubble thickness), but this gets fuzzy towards the end of the winter
        #ax.set_title('All level ice - several lines', fontsize=25)
        if suff=='_all':
            mask = (x<0) | (x>700)  #| (it>2)
        
        
        #parallel to ship heading - 260 m long
        #this side gets influenced by ROV hut (November-December) and a small ridge (February-)
        if suff=='_par':
            mask = (x<0) | (x>260)
        

        #perpendicular to ship heading - 180m long
        if suff=='_per':
            mask = (x<260) | (x>440)
       

        #diagonal to ship heading - 260 m long
        if suff=='_dia':
            mask = (x<440) | (x>700)
        
        #both continiously undeformed sides
        if suff=='_per+dia':
            mask = (x<260) | (x>700)
        

        it = np.ma.array(it,mask=mask).compressed()
        si = np.ma.array(si,mask=mask).compressed()
        mxx = np.ma.array(mxx,mask=mask).compressed()
        myy = np.ma.array(myy,mask=mask).compressed()

        #bad values in it
        it = np.ma.masked_invalid(it)
        si = np.ma.array(si,mask=it.mask)

        mxx = np.ma.array(mxx,mask=it.mask); mxx = mxx.compressed()
        myy = np.ma.array(myy,mask=it.mask); myy = myy.compressed()

        si = si.compressed()
        it = it.compressed()
        
        #============================================================
        #Fourier transform (discrete) - only real part
        #=============================
        #snow depth
        #number of sample points
        N = si.shape[0]

        #sample spacing
        dx = mxx[1:]-mxx[:-1]
        dy = myy[1:]-myy[:-1]
        d = np.sqrt(dx**2+dy**2)
        T=np.mean(d)      #This is already gridded data!!!, default T=1
        #print(T)
        
        #signal
        y = si
        yf = rfft(y)         #should we use fftn (instead of fft) to compute the DFT, since it has more than one dimension (map)?
        
        #frequency
        #unit: cycles/meter (5m=0.25,10m=.1,20m=0.05,30m=0.033,40m=0.025,5m=0.02) - larger values are shorter lenghts!!!
        #[:N//2] takes only real/positive part of the spectrum
        xf = rfftfreq(N, T)[:N//2]   

        #plotting
        #fx.plot(xf, 2.0/N * np.abs(yf[0:N//2]), color=colors[dd],label=datel,alpha=.9,lw=3)
        #plot wavelenght instead of frequnecy
        fx.plot(1/xf, 2.0/N * np.abs(yf[0:N//2]), color=colors[dd],label=datel,alpha=.9,lw=3)
    
        #==================================================
        #ice thickness
        y = it
        yf = rfft(y)
        xf = rfftfreq(N, T)[:N//2]

        #plotting
        #gx.plot(xf, 2.0/N * np.abs(yf[0:N//2]), color=colors[dd],label=datel,alpha=.9,lw=3)
        #plot wavelenght instead of frequnecy
        gx.plot(1/xf, 2.0/N * np.abs(yf[0:N//2]), color=colors[dd],label=datel,alpha=.9,lw=3)

        #aggreagte these data to construct 'seasonal' white and red nosie confidence levels
        #adjust the mean
        adjsi = si - np.mean(si)
        adjit = it - np.mean(it)
        
        accsi.extend(adjsi)
        accit.extend(adjit)

        #print(si)

        #check what kind of distribution this data is
        
        ##does it pass the Shapiro-Wilk test?
        ##if the p-value is less than .05, we reject the null hypothesis of the Shapiro-Wilk test.
        #from scipy.stats import shapiro 
        #print(shapiro(si))
        #print(shapiro(it))

        ##does it pass the Kolmogorov-Smirnov test?
        ##If the p-value is less than .05, we reject the null hypothesis of the Kolmogorov-Smirnov test.
        #from scipy.stats import kstest

        #print(kstest(si, 'norm'))
        #print(kstest(it, 'norm'))


        ##is it normal distribution
        ##from: https://www.statology.org/normality-test-python/
        ##is is bell shape histrogram?
        #plt.subplot(2,1,1)
        #plt.hist(si, bins=20, density=True, label='snow')
        #plt.text(np.mean(si),.5,shapiro(si)[1],c='b')
        #plt.text(np.mean(si),.4,kstest(si, 'norm')[1],c='b')
        
        
        
        #plt.subplot(2,1,2)
        #plt.hist(it, bins=20, density=True, label='ice')
        #plt.text(np.mean(it),2,shapiro(it)[1])
        #plt.text(np.mean(it),1,kstest(it, 'norm')[1])
        
        #plt.show()
        
        
        ##try q-q plots instead
        #import statsmodels.api as sm
        ##from scipy.stats import norm
        #import scipy.stats as stats
        ##plt.subplot(2,1,1)
        #sm.qqplot(si, stats.t, distargs=(2,), line='45',c='g')
        ##plt.text(np.mean(si),.5,shapiro(si)[1],c='b')
        ##plt.text(np.mean(si),.4,kstest(si, 'norm')[1],c='b')
        
        #plt.show()
        
        ##plt.subplot(2,1,2)
        #sm.qqplot(it, stats.t, distargs=(2,), line='45',c='orange')
        ##plt.text(np.mean(it),2,shapiro(it)[1])
        ##plt.text(np.mean(it),1,kstest(it, 'norm')[1])
        
        #plt.show()
    



accsilog = np.log(accsi)
accitlog = np.log(accit)


#first demonstrate that these seasonal agregated data is long-normal distributed
#distribution is normal (statistical tests) if log(x)

#though q-q plot shows still exponential distribution after tranformation
#histogram is still somewhat skewed to left
#both indicating that this is actually close to gamma distribution
    
import statsmodels.api as sm
import scipy.stats as stats
from scipy.stats import shapiro
from scipy.stats import kstest

fig2 = plt.figure(figsize=(5,18))
ax = fig2.add_subplot(421)
accsilog=np.array(accsilog)
ax=sm.qqplot(accsilog, stats.t, distargs=(5,), line='45',c='g')
#plt.show()

bx = fig2.add_subplot(422)
accitlog=np.array(accitlog)
bx=sm.qqplot(accitlog, stats.t, distargs=(5,), line='45',c='orange')
#plt.show()

cx = fig2.add_subplot(423)
cx.hist(accsilog, bins=50, density=True, label='snow')
cx.text(-6,.2,shapiro(accsilog)[1],c='b')
cx.text(-6,.1,kstest(accsilog, 'norm')[1],c='b')

dx = fig2.add_subplot(424)
dx.hist(accitlog, bins=50, density=True, label='ice')
dx.text(-6,.2,shapiro(accitlog)[1])
dx.text(-6,.1,kstest(accitlog, 'norm')[1])

##Fourier transform (discrete)
##number of sample points
#N = si.shape[0]

##sample spacing
#dx = mxx[1:]-mxx[:-1]
#dy = myy[1:]-myy[:-1]
#d = np.sqrt(dx**2+dy**2)
#T=np.mean(d)      #This is already gridded data!!!, default T=1
##print(T)

##signal
#y = si
#yf = rfft(y)         #should we use fftn (instead of fft) to compute the DFT, since it has more than one dimension (map)?

##frequency
##unit: cycles/meter (5m=0.25,10m=.1,20m=0.05,30m=0.033,40m=0.025,5m=0.02) - larger values are shorter lenghts!!!
##[:N//2] takes only real/positive part of the spectrum
#xf = rfftfreq(N, T)[:N//2]   


##estimates of white noise confidence levels
### frequencies (30min resolution)
##f_u01=np.zeros(n/2+1,np.float)
##f_u01=np.linspace(0,1,num=(n/2.+1))/(30*60*2)  
#### Variance of data as power spectrum of white noise
#var=np.var(si)
#### degrees of freedom
#M=int(N/2)
#phi=(2*(N-1)-M/2.)/M
##phi=(2*N-M/2.)/M
#print(phi)
####values of chi-squared
#chi_val_99 = chi2.isf(q=0.01/2, df=phi) #/2 for two-sided test
#chi_val_95 = chi2.isf(q=0.05/2, df=phi)

##estimates for red noise
##https://www.mathworks.com/matlabcentral/fileexchange/45539-rednoise_confidencelevels
##% rhoAR1 subroutine
##%
##% this subroutine calculates the lag-1 autocorrelation coefficient 
##% for an AR1 autocorrelation of data with fixed sampling step d.
##% In case of a constant sampling step, a=rho^(1/d) (with 0<a<1)
##%                                  
##%                                         _n             _n
##% then, according to Mudelsee 2002,  rho= \ (x(i)x(i-1)/ \x(i-1)^2
##%                                         /              /
##%                                         i=2            i=2
##%
##%
##%
##%
##% Inputs : 
##% datax = 1 column array with measures resampled with a constant sampling step.
##%
##% Outputs :
##% rho = lag-1 autocorrelation coefficient.
##%
##% Dorothée Husson, November 2012
##function [rho]=rhoAR1(datax)
##nrho=length(datax);
##rho=0;
##sommesup=0;
##sommeinf=0;
##moy=sum(datax)/nrho;
##datam=datax-moy;
##for i=2:nrho
    ##j=i-1;
    ##sommesup=sommesup+(datam(i)*datam(j));
    ##sommeinf=sommeinf+((datam(j))^2);
##end
##rho=sommesup/sommeinf;
##end




#### normalization of power spectrum with 1/n
##plt.figure(figsize=(5,5))
##plt.plot(fft[0:M],abs[0:M]/n, color='k')  
#plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]), color='r',alpha=.9,lw=3)
#plt.axhline(y=(var/N)*(chi_val_99/phi),color='0.4',linestyle='--')
#plt.axhline(y=(var/N)*(chi_val_95/phi),color='0.4',linestyle='--')
##plt.ylim(0,.1)
##plt.xlim(0.0066,.2)
#plt.show()



#==================================================
#snow
data=np.ma.masked_invalid(accsi).compressed()

#yf = rfft(data)
#xf = rfftfreq(len(data), 1) 
#n=len(data)

#var=np.var(si)

#### degrees of freedom
#M=n/2
#phi=(2*(n-1)-M/2.)/M       
####values of chi-squared
#chi_val_99 = chi2.isf(q=0.01/2, df=phi) #/2 for two-sided test
#chi_val_95 = chi2.isf(q=0.05/2, df=phi)



#### normalization of power spectrum with 1/n
#plt.figure(figsize=(5,5))
#plt.plot(xf,np.abs(yf)/n, color='k')  
#plt.axhline(y=(var/n)*(chi_val_95/phi),color='r',linestyle='--')
#plt.show()


from scipy.stats import gamma

#discrete Fourier Transform (DFT) of a real-valued array
yf = rfft(data)
xf = rfftfreq(len(data), 1)
n=len(data)
var=np.var(data)

#show that this data are similar to a theoretical gamma function/model
spectrum = np.abs(yf)**2/len(data)
a2x = fig2.add_subplot(425)
a2x.hist(spectrum, bins=100, density=True, label='data')
z = np.linspace(0, np.max(spectrum), 100)
a2x.plot(z, gamma.pdf(z, 1, scale=1.0/12), 'k', label='$\Gamma(1,{:.3f})$'.format(1.0/12))


# degrees of freedom
phi = 2
###values of chi-squared
chi_val_95 = chi2.isf(q=0.05/2, df=phi) #/2 for two-sided test

### normalization of power spectrum with 1/n

c2x = fig2.add_subplot(427)
c2x.plot(xf,np.abs(yf)**2/n, color='k')
# the following two lines should overlap - red and white noise
c2x.axhline(y=gamma.isf(q=0.05/phi, a=1, scale=var),color='b')
c2x.axhline(y=var*(chi_val_95/phi),color='r',linestyle='--')
#plt.ylim(0,.2)
#plt.xlim(0.0066,.2)


#draw these same lines on the Figure 1
#fx.axhline(y=gamma.isf(q=0.05/phi, a=1, scale=var),color='0.5')
fx.axhline(y=var*(chi_val_95/phi),color='0.5',linestyle=':',lw=4, label = '95% white noise conf. level')



## remove outliers
#threshold = np.percentile(np.abs(yf)**2, 95) 
#filtered = [x for x in np.abs(yf)**2 if x <= threshold]

## estimate variance
## In time-domain variance ~ np.sum(data**2)/len(data))
## In frequency-domain, using Parseval's theorem we get np.sum(data**2)/len(data) = np.mean(np.abs(spectrum)**2)/len(data)
#var = np.mean(filtered)/len(data)

#plt.figure(figsize=(5,5))
#plt.plot(xf,10*np.log10(np.abs(yf)**2/n), color='k')  
#plt.axhline(y=10*np.log10(gamma.isf(q=0.05/2, a=1, scale=var)),color='r',linestyle='--')
#plt.show()


#==================================================
#ice
data=np.ma.masked_invalid(accit).compressed()

#discrete Fourier Transform (DFT) of a real-valued array
yf = rfft(data)
xf = rfftfreq(len(data), 1)
n=len(data)
var=np.var(data)

#show that this data are similar to a theoretical gamma function/model
spectrum = np.abs(yf)**2/len(data)
b2x = fig2.add_subplot(426)
b2x.hist(spectrum, bins=100, density=True, label='data')
z = np.linspace(0, np.max(spectrum), 100)
b2x.plot(z, gamma.pdf(z, 1, scale=1.0/12), 'k', label='$\Gamma(1,{:.3f})$'.format(1.0/12))


# degrees of freedom
phi = 2
###values of chi-squared
chi_val_95 = chi2.isf(q=0.05/2, df=phi) #/2 for two-sided test

### normalization of power spectrum with 1/n

d2x = fig2.add_subplot(428)
d2x.plot(xf,np.abs(yf)**2/n, color='k')
# the following two lines should overlap - red and white noise
d2x.axhline(y=gamma.isf(q=0.05/phi, a=1, scale=var),color='b')
d2x.axhline(y=var*(chi_val_95/phi),color='r',linestyle=':')
#plt.ylim(0,.2)
#plt.xlim(0.0066,.2)


#draw these same lines on the Figure 1
#gx.axhline(y=gamma.isf(q=0.05/phi, a=1, scale=var),color='0.5')
gx.axhline(y=var*(chi_val_95/phi),color='0.5',lw=4,linestyle=':', label = '95% white noise conf. level')

#plt.show()

from spectrum import cspectrum

#==================================================
#snow
a=np.ma.masked_invalid(accit).compressed()

#get distances between points
dx = mxx[1:]-mxx[:-1]
dy = myy[1:]-myy[:-1]
md = np.sqrt(dx**2+dy**2)
x = np.zeros_like(si)
x[1:] = np.cumsum(md)

t=x

#n = 1000
n=len(data)

t=np.cumsum(np.ones_like(data)) #abount one meter distance as dummy

#largest distance in m
m = 150
#m = int(x[-1])
#print(m)
#m=100
#exit()
if suff=='_par': m=260
if suff=='_per': m=180
if suff=='_dia': m=260
if suff=='_all': m=700

#confidence level
p = 0.01
p = 0.05    #95%
#p = 0.1

ol, tl, sl, st, strw = cspectrum(n,m,a,p)


import matplotlib.pyplot as plt
plt.subplot(2,1,1)
plt.plot(t, a)
plt.title('signal', fontsize = 20)
plt.xlim([0,m])
plt.subplot(2,1,2)
plt.plot(tl, sl, label = 'spectrum')
plt.plot(tl, st, label = '99% red confidence level')
plt.xscale('log')
plt.xlim([1,m])
plt.legend(fontsize = 20)
#plt.show()

#change tl to frequnecy domain
#tlfreq=1/tl
#fx.plot(tlfreq, sl, label = 'spectrum')
#fx.plot(tlfreq, st,'--k',lw=4, label = '95% red noise confidence level')

#leave as wavelenght
fx.plot(tl, st,'--k',lw=4, label = '95% red noise conf. level')

#==================================================
#ice
a=np.ma.masked_invalid(accit).compressed()

#get distances between points
dx = mxx[1:]-mxx[:-1]
dy = myy[1:]-myy[:-1]
md = np.sqrt(dx**2+dy**2)
x = np.zeros_like(si)
x[1:] = np.cumsum(md)

t=x

#n = 1000
n=len(data)

t=np.cumsum(np.ones_like(data)) #abount one meter distance as dummy

#largest distance in m
m = 150
#m = int(x[-1])
#print(m)
#m=100
#exit()
if suff=='_par': m=260
if suff=='_per': m=180
if suff=='_dia': m=260
if suff=='_all': m=700

#confidence level
p = 0.01
p = 0.05    #95%
#p = 0.1

ol, tl, sl, st, strw = cspectrum(n,m,a,p)


import matplotlib.pyplot as plt
plt.subplot(2,1,1)
plt.plot(t, a)
plt.title('signal', fontsize = 20)
plt.xlim([0,m])
plt.subplot(2,1,2)
plt.plot(tl, sl, label = 'spectrum')
plt.plot(tl, st, label = '99% red confidence level')
plt.xscale('log')
plt.xlim([1,m])
plt.legend(fontsize = 20)
#plt.show()

#change tl to frequnecy domain
#tlfreq=1/tl
#gx.plot(tlfreq, sl, label = 'spectrum')
#gx.plot(tlfreq, st,'--k',lw=4, label = '95% red noise confidence level')

#leave as wavelenght
gx.plot(tl, st,'--k',lw=4, label = '95% red noise conf. level')

#fx.legend(ncol=4)
gx.legend(ncol=2)

#make simple figure annotation
gymin, gymax = gx.get_ylim()
fymin, fymax = fx.get_ylim()
if suff=='_dia':
    fx.text(3, fymax, "h", ha="center", va="center", size=45)
    gx.text(3, gymax, "g", ha="center", va="center", size=45)
    
elif suff=='_per':
    fx.text(3, fymax, "f", ha="center", va="center", size=45)
    gx.text(3, gymax, "e", ha="center", va="center", size=45)
    
elif suff=='_par':
    fx.text(3, fymax, "d", ha="center", va="center", size=45)
    gx.text(3, gymax, "c", ha="center", va="center", size=45)
    
elif suff=='_all':
    fx.text(3, fymax, "b", ha="center", va="center", size=45)
    gx.text(3, gymax, "a", ha="center", va="center", size=45)

fig1.savefig(outpath+'fft_'+str(step)+'_'+loc+suff,bbox_inches='tight')

#plt.show()

exit()

##estimate AR1
##calculation of the lag-1 autocorrelation coefficient
#def rhoAR1(data):
    #nrho=len(data)
    #rho=0
    #sommesup=0
    #sommeinf=0
    #moy=sum(data)/nrho
    #datam=data-moy
    #for i in range(1,nrho):
        #j=i-1
        #sommesup=sommesup+(datam[i]*datam[j])
        #sommeinf=sommeinf+((datam[j])**2)

    #rho=sommesup/sommeinf
    
    #print(rho)
    
    #return(rho)

#rho=rhoAR1(data)


##calculation of nsim red noise models
#def rednoise(timex,rho,nsim=1000):
    ##nsim= number of red noise simulations performed within the Monte Carlo loop. 1000 or 1500 are usually enough.
    ##timex= one column array with time or depth corresponding to each values of the signal studied
    #nt=len(timex)
    ## disp('How many values ?');
    ## nt=input('number of values for the red noise : ');
    #rzero=0
    #redtab=np.zeros((nsim,nt))
    #red=np.zeros((nt))

    #srho=np.sqrt(1-rho**2)
    #for i in range(0,nsim):
        #white=srho*np.random.randn()
        #red[0]=rho*rzero+white
        #for j in range(0,nt):
            #white=srho*np.random.randn()
            #red[j]=rho*red[j-1]+white
        
        ##print(red.shape)
        ##print(redtab.shape)
        ##print(redtab[i,:].shape)
        
        #redtab[i,:]=red

    #return(redtab,nt)



##get distances between points
#dx = mxx[1:]-mxx[:-1]
#dy = myy[1:]-myy[:-1]
#md = np.sqrt(dx**2+dy**2)
#x = np.zeros_like(si)
#x[1:] = np.cumsum(md)

#redtab,nt=rednoise(x,rho)

##spectral analysis of the nsim red noise signals and power normalization of each specra.
#nt=len(x)
#red2=np.zeros((nt))
#specred=[]

#def pmtm():
    

#for i in range(0,nsim):
    #red2=redtab(:,i)
    #red2m=sum(red2)/nt
    #red2n=red2-red2m #cf commentaire precedent (enlever la moyenne de red2)
    #[pr,wr]=pmtm(red2n,nw);
    #npr=size(pr,1);
    ##calculation of the area of the power spectrum of the rednoise
    #Ar=sum(pr)/npr;
    #pr=pr*(Ax/Ar);
    #specred(:,i)=pr;
#end
#% Calculation of the mean rednoise spectra and normalization of the power.
#i=1;
#j=1;
#Mpr=0;
#Mspecred=[];
#for i=1:npr
    #Mpr=specred(i,1);
    #for j=2:nsim
        #Mpr=Mpr+specred(i,j);
    #end
    #Mspecred(i)=Mpr/nsim;
#end
#fr=wr/(2*pi*dt);

import numpy as np
import matplotlib.pyplot as plt

def plot_spectrum(s):
    f = np.fft.rfftfreq(len(s))
    plt.loglog(f, np.abs(np.fft.rfft(s)))


def noise_psd(N, psd = lambda f: 1):
        X_white = np.fft.rfft(np.random.randn(N));          #we need to generate white noise here with same mean, var as original data. AR=1
        S = psd(np.fft.rfftfreq(N))
        # Normalize S
        S = S / np.sqrt(np.mean(S**2))
        X_shaped = X_white * S;
        return np.fft.irfft(X_shaped);

def PSDGenerator(f):
    return lambda N: noise_psd(N, f)

@PSDGenerator
def white_noise(f):
    return 1;

@PSDGenerator
def blue_noise(f):
    return np.sqrt(f);

@PSDGenerator
def violet_noise(f):
    return f;

@PSDGenerator
def brownian_noise(f):
    return 1/np.where(f == 0, float('inf'), f)

@PSDGenerator
def pink_noise(f):
    return 1/np.where(f == 0, float('inf'), np.sqrt(f))

plt.figure(figsize=(8, 8))
    
yf = rfft(data)
xf = rfftfreq(len(data), 1) 
n=len(data)
plt.plot(xf,np.abs(yf)/n, color='k')  

for G in [brownian_noise,  white_noise]:
    plot_spectrum(G(n))

    
plt.legend(['data', 'brownian', 'white'])
#plt.ylim([1e-3, None]);


plt.xticks([0.0066,0.01,.0142,.02,.0286,.04,.066,.1,.143,0.2])
#plt.xticklabels([r'$\frac{1}{150}$',r'$\frac{1}{100}$',r'$\frac{1}{70}$',r'$\frac{1}{50}$',r'$\frac{1}{35}$',r'$\frac{1}{25}$',r'$\frac{1}{15}$',r'$\frac{1}{10}$',r'$\frac{1}{7}$',r'$\frac{1}{5}$'])



plt.show()







#create noise with same mu, sigma and size as data
sample=np.random.normal(0, 1, size=10)

# reproduction of random numbers
np.random.seed(1234)
alpha= 0.8

# generate samples using Numpy
random_seed = np.random.RandomState(1234)
noise = random_seed.normal(0,1,len(data)) * np.std(data) * 0.2
a = np.zeros_like(data)

for i in range(1, noise.size):
    a[i] = noise[i] + a[i - 1] * alpha

data_noise = data + a
