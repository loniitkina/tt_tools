import numpy as np
from glob import glob
from tt_func import getColumn, running_stats
from scipy.signal import savgol_filter
from datetime import datetime
import matplotlib.pyplot as plt

#MOSAiC
inpath = '../data/ridges/'
inpath_table = '../data/MCS/GEM2_thickness/09-ridges-recal/'
outpath = '../plots_ridges/'

#elevation from ALS 
als_elev=True
#als_elev=False

#loc = 'ridgeFR1'
#dates = ['20200108']
#start = [0,1]
#elev_bias = [0.3,0.2,]  #manual adjustment to have freeboard measurements for drill holes at about zero elevation
#title = 'Fort Ridge Installation Transect '

#loc = 'ridgeFR2'    #coring
#dates = ['20200110','20200212']
#start = [0,0,6]
#elev_bias = [0.2,0.2,0.2]  #manual adjustment to have freeboard measurements for drill holes at about zero elevation
#title = 'Fort Ridge Coring Transect '

#loc = 'ridgeFR3'
#dates = ['20200131']
#start = [0]
#elev_bias = [0.2]
#title = 'Fort Ridge Optics Transect '

#loc = 'ridgeA1'    #central
#dates = ['20200117','20200131','20200228','20200410','20200628']
##dates = ['20200117','20200131','20200228','20200628']
#start = [0,-4,-8,0,0]   #some transect lines were extended X meters over the Nloop/road
#elev_bias = [.5,-.5,-.5,-.5,-.5]   #not important as we dont have draft data here
#title = "Alli's Ridge Central Transect "

locs = ['ridgeFR1','ridgeFR2','ridgeFR2','ridgeFR3','ridgeA1']#,'ridgeA1']
dates = ['20200108','20200110','20200212','20200131','20200117']#,'20200117']
start = [0,0,0,0,0,-4]
elev_bias = [0.3,0.2,0.2,0.2,0.5,0.5]
seq = ['f','f','s','f','f','s'] #first of second in the sequence

#plot
fig1 = plt.figure(figsize=(20,10))

ax = fig1.add_subplot(121)
ax.set_xlabel('Drill hole thickness (m)', fontsize=25)
ax.set_title('Total thickness', fontsize=30, loc='left')
ax.set_ylabel('EMI thickness (m)', fontsize=25)
ax.tick_params(axis="x", labelsize=24)
ax.tick_params(axis="y", labelsize=24)
#ax.set_facecolor('0.8')

bx = fig1.add_subplot(122)
bx.set_xlabel('Drill hole thickness (m)', fontsize=25)
bx.set_title('Consolidated layer thickness', fontsize=30, loc='left')
bx.set_ylabel('EMI thickness (m)', fontsize=25)
bx.tick_params(axis="x", labelsize=24)
bx.tick_params(axis="y", labelsize=24)
#bx.set_facecolor('0.8')

x_ii=[]
x_cc=[]
y_ii=[]
y_cc=[]

for dd in range(0,len(dates)):
    loc = locs[dd]
    date = dates[dd]
    print(loc, date)
    
    ##fname = glob(inpath_table+'*/magna+gem2*'+date+'*'+loc+'.csv')[0]
    try:
        fname = glob(inpath_table+date+'/mosaic-*-gem2-*'+loc+'.csv')[0]
    except:
        try:
            fname = glob('../data/MCS/GEM2_thickness/01-ice-thickness/'+date+'*/mosaic-*-gem2-*'+loc+'.csv')[0]
        except:
            #pulk transects    
            #fname = glob('../data/MCS/MP/*/magna+gem2*'+date+'*'+loc+'.csv')[0]
            fname = glob('../data/ridges_multif/mosaic_gem-2+mp_'+date+'_'+loc+'_2.csv')[0]

    print(fname)

    #snow depth
    snod = getColumn(fname,5);si = np.array(snod,dtype=np.float)  #snow depth
    
    #Date,Lon,Lat,X,Y,Snow,f1525Hz_hcp_i,f1525Hz_hcp_q,f5325Hz_hcp_i,f5325Hz_hcp_q,18325Hz_hcp_i,f18325Hz_hcp_q,f63025Hz_hcp_i,f63025Hz_hcp_q,f93075Hz_hcp_i,f93075Hz_hcp_q
    it1 = getColumn(fname,6);it1 = np.array(it1,dtype=np.float)
    it2 = getColumn(fname,7);it2 = np.array(it2,dtype=np.float)
    it3 = getColumn(fname,8);it3 = np.array(it3,dtype=np.float)
    it4 = getColumn(fname,9);it4 = np.array(it4,dtype=np.float)
    it5 = getColumn(fname,10);it5 = np.array(it5,dtype=np.float)      #closer to real thickness, but still influenced by consolidation (has detection limit)
    it6 = getColumn(fname,11);it6 = np.array(it6,dtype=np.float)      #consolidation can be seen in column 13 (63kHz q) and 15 (93kHz q)
    it7 = getColumn(fname,12);it7 = np.array(it7,dtype=np.float)
    it8 = getColumn(fname,13);it8 = np.array(it8,dtype=np.float)
    it9 = getColumn(fname,14);it9 = np.array(it9,dtype=np.float)
    it10 = getColumn(fname,15);it10 = np.array(it10,dtype=np.float)
    
    #exclude the A1 values where the 1.4kHz values are very high
    it1 = np.where(it1>10,np.nan,it1)
    
    #ice thickness
    ii = np.empty((3,len(it3)))
    ii[0,:]=np.nan_to_num(it3, nan=-9999)
    ii[1,:]=np.nan_to_num(it5, nan=-9999)
    ii[2,:]=np.nan_to_num(it1, nan=-9999)
    ii = np.mean(np.ma.array(ii,mask=ii<0),axis=0)
    
    #consolidated layer thickness
    cc = np.empty((3,len(it3)))
    cc[0,:]=np.nan_to_num(it10, nan=-9999)
    cc[1,:]=np.nan_to_num(it8, nan=-9999)
    cc[2,:]=np.nan_to_num(it6, nan=-9999)
    cc = np.mean(np.ma.array(cc,mask=cc<0),axis=0)
            
    #surface elevation - determine just for the first of the repeated transects
    if seq[dd]=='f':
        #hydrostatic equilibrium with mean snow density and sea ice density
        rho_i = 882 #assuming 10% air content in the bulk of the ridge = 30% of the sail (level ice density 882). This corresponds well with total macroporosity from drillings 20-30%
        rho_w = 1025
        rho_s = 313

        #following Forsstrom et al, 2011, Annals of Glaciology
        #fb = (ii - si * (rho_s/(rho_w-rho_i))) * (rho_w-rho_i)/rho_w
        fb = (ii * (rho_w-rho_i)/rho_w ) - (si * rho_s/rho_w)
        fb_hs = fb

        #ALS elevation
        if als_elev:
                #ef = glob(inpath+'magna+gem2-transect-'+date+'*'+loc+'_ALS2.csv')[0]
                #ef = glob(inpath+'magna+gem2-transect-'+date+'*'+loc+'_ALS_1_corr3.csv')[0]
                #ef = glob(inpath+'magna+gem2-transect-'+date+'*'+loc+'_ALS_1_corr4.csv')[0]
                ef = glob(inpath+'mosaic-transect-'+date+'-gem2-556+mp_'+loc+'_ALS_1_corr4.csv')[0]
                print(ef)
                elev = getColumn(ef,2)
                elev = np.array(elev,dtype=np.float)
                
                #if loc=='ridgeA2':
                    #elev[25:33] = elev[25:33]+.5

                
                ##estimate offset for the negative values
                #offset_elev = np.min(elev-si)
                #if offset_elev < 0:
                    #elev = elev + offset_elev*-1
                fb = elev - si + elev_bias[dd]
                fb_first = fb.copy()

                
                if loc=='ridgeFR1' or loc=='ridgeFR2' or loc=='ridgeFR3':
                    #ROV multibeam draft
                    #df = glob(inpath+'magna+gem2-transect-'+date+'*'+loc+'_ROV.csv')[0]
                    #df = glob(inpath+'magna+gem2-transect-'+date+'*'+loc+'_ROV_20200128.csv')[0]
                    df = glob(inpath+'mosaic-transect-'+date+'-gem2-556+mp_'+loc+'_ROV_20200128.csv')[0]
                    df = glob(inpath+'mosaic-transect-'+date+'-gem2-556+mp_'+loc+'_ROV_20200128_match.csv')[0]
                    print(df)
                    draft = getColumn(df,2) #closest value 
                    
                    ##footprint=4x total thickness
                    #draft_m = getColumn(df,3) #footprint average
                    #draft_std = getColumn(df,4) #footprint STD
                    
                    ##footprint=2m (radius)
                    draft_m = getColumn(df,7) #footprint average
                    draft_std = getColumn(df,8) #footprint STD
                    
                    draft = np.array(draft,dtype=np.float)*-1
                    draft_m = np.array(draft_m,dtype=np.float)*-1
                    draft_std = np.array(draft_std,dtype=np.float)*-1
                    draft_first = draft.copy()
                    draft_m_first = draft_m.copy()
                    draft_std_first = draft_std.copy()
                    
                

    #cumulative distance allong the fixed date MP transect
    #ridge transects have a known distance 1 meter
    #add a bit at the end
    x = np.arange(start[dd],len(si)+start[dd])
        
    #check that the elevation and profile length match
    print(len(x))
    print(len(fb))
    
    if date=='20200228' and loc=='ridgeA2':
        fb  = np.ones_like(x)*fb_first[-1]
        fb[start[dd]*-1:]=fb_first[:start[dd]]
    if date=='20200228' and loc=='ridgeA3':
        fb  = np.ones_like(x)*fb_first[-1]
        fb[start[dd]*-1:]=fb_first[:start[dd]]
    
    if len(x)!=len(fb):
        print('Elevation and profile length dont match!', dates[dd])
        print(start[dd])
        #extend/reduce the elevation vector
        fb  = np.ones_like(x)*fb_first[-1] #extend the last values (lead)
        print(len(fb))
        print(len(fb_first))
        if date=='20200131':
            fb[start[dd]*-1:]=fb_first
        if date=='20200228' and loc=='ridgeA1':
            fb[start[dd]*-1:len(fb_first)+start[dd]*-1]=fb_first
        if date=='20200228' and loc=='ridgeA2':
            fb[start[dd]*-1:]=fb_first[:start[dd]]
        if date=='20200228' and loc=='ridgeA3':
            fb[:]=fb_first[:-6]
        if date=='20200119':
            fb[0:len(fb_first)]=fb_first[:]
        if date=='20200212' and loc=='ridgeFR2':
            fb[:]=fb_first[:-1]
        if date=='20200221' and loc=='ridgeFR1':
            fb[:]=fb_first[start[dd]:len(fb)+start[dd]]
        if date=='20200221' and loc=='ridgeFR2':
            fb[:]=fb_first[:-1]
        if date=='20200305':
            fb[:]=fb_first[start[dd]:len(fb)+start[dd]]
        if date=='20200410' and loc=='ridgeA1': #started at the road?
            fb[0:len(fb_first)]=fb_first[:]
        if date=='20200410' and loc=='ridgeA2':
            fb[:]=fb_first[start[dd]:len(fb)+start[dd]]
        if date=='20200410' and loc=='ridgeA3': #started at the road?
             fb[:]=fb_first[start[dd]:len(fb)+start[dd]]
            
        if date=='20200628' and loc=='ridgeA1': #started at the road?
            fb[0:len(fb_first)]=fb_first[:]
        if date=='20200628' and loc=='ridgeA2': #started at the road?
            fb[:]=fb_first[start[dd]:len(fb)+start[dd]]
        if date=='20200628' and loc=='ridgeA3': #started at the road?
            fb[:]=fb_first[start[dd]:len(fb)+start[dd]]
            
            
        if loc=='ridgeFR1' or loc=='ridgeFR2' or loc=='ridgeFR3':
            draft  = np.ones_like(x)*draft_first[-1]
            draft_m  = np.ones_like(x)*draft_first[-1]
            draft_std  = np.ones_like(x)*draft_std_first[-1]
            if date=='20200131':
                draft[1:-3]=draft_first[:]
                draft_m[1:-3]=draft_first[:]
                draft_std[1:-3]=draft_std_first[:]
            if date=='20200119':
                fb[0:len(fb_first)]=fb_first[:]
                draft[0:len(fb_first)]=draft_first[:]
                draft_m[0:len(fb_first)]=draft_m_first[:]
                draft_std[0:len(fb_first)]=draft_std_first[:]
            if date=='20200212' and loc=='ridgeFR2':
                draft[:]=draft_first[:-1]
                draft_m[:]=draft_m_first[:-1]
                draft_std[:]=draft_std_first[:-1]
            if date=='20200221' and loc=='ridgeFR1':
                draft[:]=draft_first[start[dd]:len(fb)+start[dd]]
                draft_m[:]=draft_m_first[start[dd]:len(fb)+start[dd]]
                draft_std[:]=draft_std_first[start[dd]:len(fb)+start[dd]]
            if date=='20200221' and loc=='ridgeFR2':
                draft[:]=draft_first[:-1]
                draft_m[:]=draft_m_first[:-1]
                draft_std[:]=draft_std_first[:-1]
            if date=='20200305':
                draft[:]=draft_first[start[dd]:len(fb)+start[dd]]
                draft_m[:]=draft_m_first[start[dd]:len(fb)+start[dd]]
                draft_std[:]=draft_std_first[start[dd]:len(fb)+start[dd]]

    #plot
    if loc=='ridgeFR1':
        dist = [12,16,19,22,27,30]
        tot = [.85,6.05,7.1,6.1,4.1,4.05]
        cl = [.85,1.75,3,2.3,1.2,3.1]
        
    if loc=='ridgeFR2':
        
        if date=='20200110':
            dist = [24,34,39,45,47,56,63]
            tot = [1.05,2.87,3.5,4.3,2.85,3.55,1.05]
            cl = [1.05,2.87,1.55,1.3,1.7,2.8,1.05]
            
        if date=='20200212':
            dist = [41,51]
            tot = [5.6,3.2]
            cl = [2.2,2.45]   
            
    if loc=='ridgeFR3':
        
        dist = [10,12,15,20,25,9,11,14,21]
        tot = [4.05,5.15,5.75,5.6,5.3,3.7,3.7,5.3,5.4]
        cl = [2,2.3,3.7,2.85,4,1.45,2.75,3,3.7]
        
    if loc=='ridgeA1':
               
        dist = [20,25,35,35,40]
        tot = [6.75,5.5,7.95,7.05,6.45]
        cl = [3.05,4,2.5,2.55,2.8]
        
    for i in range(0,len(dist)):
        d = dist[i]
        dh1 = tot[i]
        dh2 = cl[i]

        if (dd==0) and (i==0):
            #total thickness
            ax.scatter(dh1,it1[d], marker='o',c='k', label='1.5kHz')
            ax.scatter(dh1,it2[d], marker='x',c='k')
            ax.scatter(dh1,it3[d], marker='o',c='b', label='5kHz')
            ax.scatter(dh1,it4[d], marker='x',c='b')
            ax.scatter(dh1,it5[d], marker='o',c='g', label='18kHz')
            ax.scatter(dh1,it6[d], marker='x',c='g')
            ax.scatter(dh1,it7[d], marker='o',c='r', label='60kHz')
            ax.scatter(dh1,it8[d], marker='x',c='r')
            ax.scatter(dh1,it9[d], marker='o',c='y', label='98kHz')
            ax.scatter(dh1,it10[d], marker='x',c='y')
            
            ax.scatter(dh1,ii[d], marker='o',c='none',ec='k',s=80, label='mean',lw=2)

            
            #consolidated layer
            bx.scatter(dh2,it1[d]-fb[d], marker='o',c='k', label='1.5kHz')
            bx.scatter(dh2,it2[d]-fb[d], marker='x',c='k')
            bx.scatter(dh2,it3[d]-fb[d], marker='o',c='b', label='5kHz')
            bx.scatter(dh2,it4[d]-fb[d], marker='x',c='b')
            bx.scatter(dh2,it5[d]-fb[d], marker='o',c='g', label='18kHz')
            bx.scatter(dh2,it6[d]-fb[d], marker='x',c='g')
            bx.scatter(dh2,it7[d]-fb[d], marker='o',c='r', label='60kHz')
            bx.scatter(dh2,it8[d]-fb[d], marker='x',c='r')
            bx.scatter(dh2,it9[d]-fb[d], marker='o',c='y', label='98kHz')
            bx.scatter(dh2,it10[d]-fb[d], marker='x',c='y')
            
            bx.scatter(dh2,cc[d]-fb[d], marker='o',c='none',ec='k',s=80, label='mean',lw=2)
        else:
            ax.scatter(dh1,it1[d], marker='o',c='k')
            ax.scatter(dh1,it2[d], marker='x',c='k')
            ax.scatter(dh1,it3[d], marker='o',c='b')
            ax.scatter(dh1,it4[d], marker='x',c='b')
            ax.scatter(dh1,it5[d], marker='o',c='g')
            ax.scatter(dh1,it6[d], marker='x',c='g')
            ax.scatter(dh1,it7[d], marker='o',c='r')
            ax.scatter(dh1,it8[d], marker='x',c='r')
            ax.scatter(dh1,it9[d], marker='o',c='y')
            ax.scatter(dh1,it10[d], marker='x',c='y')
            
            ax.scatter(dh1,ii[d], marker='o',c='none',ec='k',s=80,lw=2)

            bx.scatter(dh2,it1[d]-fb[d], marker='o',c='k')
            bx.scatter(dh2,it2[d]-fb[d], marker='x',c='k')
            bx.scatter(dh2,it3[d]-fb[d], marker='o',c='b')
            bx.scatter(dh2,it4[d]-fb[d], marker='x',c='b')
            bx.scatter(dh2,it5[d]-fb[d], marker='o',c='g')
            bx.scatter(dh2,it6[d]-fb[d], marker='x',c='g')
            bx.scatter(dh2,it7[d]-fb[d], marker='o',c='r')
            bx.scatter(dh2,it8[d]-fb[d], marker='x',c='r')
            bx.scatter(dh2,it9[d]-fb[d], marker='o',c='y')
            bx.scatter(dh2,it10[d]-fb[d], marker='x',c='y')
            
            bx.scatter(dh2,cc[d]-fb[d], marker='o',c='none',ec='k',s=80,lw=2)
            
        ##repeat the selection with the empty markers
        #ax.scatter(dh1,fb[d]-it1[d], marker='o',c='none',ec='k',s=50)
        #ax.scatter(dh1,fb[d]-it3[d], marker='o',c='none',ec='k',s=50)
        #ax.scatter(dh1,fb[d]-it5[d], marker='o',c='none',ec='k',s=50)
        
        #ax.scatter(dh1,fb[d]-ii[d], marker='o',c='k',ec='k',s=50)
        x_ii.append(dh1)
        y_ii.append(ii[d])

        #bx.scatter(fb[d]-dh2,fb[d]-it6[d], marker='o',c='none',ec='k',s=50)
        #bx.scatter(fb[d]-dh2,fb[d]-it8[d], marker='o',c='none',ec='k',s=50)
        #bx.scatter(fb[d]-dh2,fb[d]-it10[d], marker='o',c='none',ec='k',s=50)
        
        #bx.scatter(fb[d]-dh2,fb[d]-cc[d], marker='o',c='k',ec='k',s=50)
        x_cc.append(dh2)
        y_cc.append(cc[d])
        
#===================================================================

#correlation coefficients
for pp in [ax,bx]:
    if pp==ax:
        x=x_ii; y=y_ii
        posx=.5
        pos=[6.,5.5,5]
        
    if pp==bx:
        x=x_cc; y=y_cc
        posx=5
        pos=[2.5,2,1.5]
        
    model = np.polyfit(x, y, 1)
    print('coefficients: ', model)

    predict = np.poly1d(model)
    from sklearn.metrics import r2_score
    r2 = r2_score(y, predict(x))
    print('R2: ',r2)

    x_lin_reg = np.arange(0, 8,1)
    y_lin_reg = predict(x_lin_reg)
    
    # ---- Standard Errors of slope & intercept ----
    n = len(x)
    x_mean = np.mean(x)

    # Residuals and variance
    residuals = y - predict(x)
    res_var = np.sum(residuals**2) / (n - 2)

    # Standard error of slope and intercept
    Sxx = np.sum((x - x_mean)**2)
    se_slope = np.sqrt(res_var / Sxx)
    se_intercept = np.sqrt(res_var * (1/n + x_mean**2 / Sxx))

    print("Standard error (slope):", se_slope)
    print("Standard error (intercept):", se_intercept)

    # Standard error of prediction at each x
    se_pred = np.sqrt(
        res_var * (1/n + (x_lin_reg - x_mean)**2 / Sxx)
    )
    
    print("Standard error model:",se_pred)
    print("Standard error model (%):", se_pred/y_lin_reg)

    # Upper and lower bounds (±1 SE)
    y_upper = y_lin_reg + se_pred
    y_lower = y_lin_reg - se_pred
    
    pp.plot(x_lin_reg, y_lin_reg, 'k-')#, label='Linear fit')
    pp.fill_between(x_lin_reg, y_lower, y_upper, color='gray', alpha=0.3)#,label='±1 SE')

    #perfect model
    pp.plot([0,10],[0,10],'--',c='0.75')

    #print(linregress(x,y))
    from scipy.stats import linregress
    slope,intercept,rvalue,pvalue,stderr=linregress(x,y)
    #p-value : two-sided p-value for a hypothesis test whose null hypothesis is that the slope is zero
    if pvalue < 0.01:   #significant at 99%
        print('significant!')
    
    pp.text(posx, pos[0], '$R^2$= '+str(np.round(r2,2)), ha="left", va="center", size=20)
    pp.text(posx, pos[1], '$N$= '+str(np.round(len(x),2)), ha="left", va="center", size=20)
    pp.text(posx, pos[2], '$p$= '+str(np.round(pvalue,5)), ha="left", va="center", size=20) 

#===================================================================

ax.set_xlim(0,8)
ax.set_ylim(0,8)

bx.set_xlim(0,8)
bx.set_ylim(0,8)

#print(np.arange(-10,1,1))
#print(np.arange(10,-1,-1))
#ax.set_yticks(np.arange(-10,1,1),['10','9','8','7','6','5','4','3','2','1','0'])

ax.legend(fontsize=20, ncol=2, loc='upper left',fancybox=True,facecolor=fig1.get_facecolor(),framealpha=.6)

outname = 'ridge_scatter.png'
print(outname)
#plt.show()
fig1.savefig(outpath+outname,bbox_inches='tight', facecolor=fig1.get_facecolor(), edgecolor='none')        
