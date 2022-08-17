from scipy.stats import chi2
import numpy as np

def cspectrum(n,m,x,p):
    '''Continuous spectrum analysis of an one-dimensional series
    Input parameters and arrays: n, m, x, p
        n: number of data
        m: biggest lag time length. Generally, m is between n/3 and n/10.
        x: raw series
        p: confidence for red or white noise (e.g. 0.01 for 99%)
    Output variables:
        ol: frequency array
        tl: periodic array  
        sl: power spectrum. Its sum from 0 to m is 1.
        st: (1-p) confidence upper limit of red or white noise spectrum
        strw: spectrum density of red or white noise 
    Usage:
        See sanity check in main or just run this script.
    The original code is written by Dr. Li Jianping in Fortran77 on May 12, 1998. 
    http://lijianping.cn/dct/attach/Y2xiOmNsYjpmOjk4Mw== (retrieved on May 5, 2022)
    This python version is by CUI Yingzhe, May 5, 2022. Email: cuiyingzhe@stu.ouc.edu.cn
    
    #This code has been adopted by Polona Itkin, polona.itkin@uit.no 
    #and adjusted so that significance level calculations fit to: Torrence and Campo: A Practical Guide to Wavelet Analysis, 1998
    '''
    sl = np.zeros((m+1))
    ol = np.zeros((m+1))
    tl = np.zeros((m+1))
    r = np.zeros((m+1))
    y = x.copy()
    r[0] = 1    #zero auto-correlation
    y -= y.mean()
    #auto-correlation
    for i in range(1, m+1):
        r[i] = sum(y[1:n-i]*y[i+1:n])/n/y.var()
    cc = np.pi*np.arange(1,m+1)/m
    for l in range(m+1):
        sl[l] = r[0] + sum(r[1:]*(1+np.cos(cc))*np.cos(l*cc))
    sl[0] /= 2
    sl[m] /= 2
    sl /= m
    ol[1:] = np.pi*np.arange(1,m+1)/m
    tl[1:] = 2*m/np.arange(1,m+1)
    ol[0] = 0
    tl[0] = 100*tl[1]
    a = sl.sum()/len(sl)
    
    #red noise estimated from AR1
    r2 = r[1]*r[1]
    print('alpha:',r[1])
        
    ##alpha as in Torrence and Campo, 1998 - usef for modeling ENSO
    #alpha = (r[1]+np.sqrt(r[2]))/2
    #r2 = alpha**2
    #print('alpha as in Torrence and Campo, 1998:',(r[1]+np.sqrt(r[2]))/2)

    v = (2*n-m/2)/m
    iv = np.floor(v)    #Return the floor of the input (closest integer larger than original element), element-wise.
    c = chi2.isf(p, iv) + (v-iv)*(chi2.isf(p, iv+1) - chi2.isf(p, iv))
    if (r[1] > 0):
        r3 = 1+r2-2*r[1]*np.cos(np.arange(m+1)*np.pi/m)
        strw = a*(1-r2)/r3
        st = strw*c/v
    else:
        strw = a
        st = a*c/v
    return ol, tl, sl, st, strw

if __name__=="__main__":
    '''Sanity check
    '''
    omega1 = 2*np.pi/10
    omega2 = 2*np.pi/100
    t = np.arange(1000)
    a = np.cos(omega1*t)+np.cos(omega2*t)
    n = 1000
    m = 300
    p = 0.01
    ol, tl, sl, st, strw = cspectrum(n,m,a,p)
    import matplotlib.pyplot as plt
    plt.subplot(2,1,1)
    plt.plot(t, a)
    plt.title('signal', fontsize = 20)
    plt.xlim([0,1000])
    plt.subplot(2,1,2)
    plt.plot(tl, sl, label = 'spectrum')
    plt.plot(tl, st, label = '99% red noise test')
    plt.xscale('log')
    plt.xlim([1,1000])
    plt.legend(fontsize = 20)
    plt.show()
