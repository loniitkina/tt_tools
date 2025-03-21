import numpy as np
from glob import glob
from tt_func import getColumn, running_stats
from scipy.signal import savgol_filter
from datetime import datetime
import matplotlib.pyplot as plt

#key findings
#EM method can detect total ridge thickness and consolidated layer thickness.
#Simple calibration works
#Best low in-phase channels are best for total thickness (best penetration) and high quadratures are best for the consolidated layer
#Snow is important for the consolidation (in winter consitions with supercooled ocean)
#but in April, ocean heat fluxes start to erode the ridges
#The footprint depends on the layer detection depth and it is larger for the total thickness than for the consolidated layer thickness. This is visible in cracks/leads on Fort Ridge (they should have no consolidation layer, except if they have platelet ice layer).
#Methods works well for shallow ridges up to about 6m (Fort Ridge). Large Ridges like Alli's ridge have a large footprint and give poor results (detection limit of this short antenna).

#Method: the reason why this works is because some freq are more sensitive to small changes in conductivity than others (e.g. non-consolidated ridges are more saline/more conductive, consolidted ridges are more fresh, more brine got rejected). This has been used in AA for platelet ice detection.
#Results
#average of 5 and 18kHz in-phase for total thickness
#average of 18, 65 and 95kHz quadrature channels for consolidate layer thickness

#Fort Ridge - consolidated ridge: 
#double ridge - thin FYI ice on both sides, most deformation happened on N side, FYI got pushed under (similarly thick, but denser/heavier?)
#One DTC is in a crack (logbook says western, but there is a crack in the sonar data at the estern side of the ridge sail), SIMBA is just over the crest (19m), then another DTC, then there is a secondary ridge and finally refrozen lead/crack
#There are blocks of ice on the top of the ridge, but typically MP snow dpeth can be measurend in the snow between the blocks. On FR1 we corrected the snow depth to zero, because the GEM-2 measurement was taken on top of the blocks.
#min and max freq (inphase) give min and max thickness inside the footprint
#steep gradients are smoothed
#possible that ridge keel accumulated some frazil ice on the rubbly side in February? Check if supported by increase MB draft...
#quadratures of highest frequnecies give lowest values - consolidated layer? They coincide roughly wiht the wetness in drill holes and are stable over time. Do the conincide with the IMB data?
#macroporosity (voids) does not matter for GEM-2. It is mainly sensitive to microporosity (soft and wet ice). Macroporosity is also hard to measure by drilling - irrelgular shapes and distribution of voids - hard to sample.
#FR3 works nicer with original calibration
#FR1 February measurements between 20 and 30 meters are very low and very likely influenced by the buoy installations that increase the conductivity (have large metal parts and batteries). Also metallic installations at start/end (ADCP). Especially DTCs have powerfull impact. SIMBAs not always visible.
#FR1 had secondary ridge detected (unconsolidated layer) in the first transect. This becomes completely consolidated in February. The big ridge re-activated in mid-March. 
#FR2 has some consolidation on the flanks, where there is less snow
#the lead on FR1 is not seen in the ALS data, likely snowed in by the end of January


#Alli's Ridge - unconsolidated ridge
#looks like thickner, stronger/heavier SYI got pushed under thinner, weaker lead ice
#There is an old consolidated ridge on the Nloop side of the transect - this has only been noticed after all the field work has been done.
#transect done in the 'dips' of the crest. The tallest crest parts were not crossable. These higher parts cause large snow drifts.
#consolidation continues until April
#consolidated layer coincides with wet and soft depth in drill holes? Do they conincide with the IMB data?
#metalic instruments have influence on A1
#large difference in drill hole depth at SIMBA installation location shows how large the spatial variability is.
#A3 has largest amount of snow and no consolidation, A1 has smallest amount of snow and fastest consolidation
#discrepancy for the crest drill hole in A1 and hole in the keel on A2. Local holes in keel are possible - high spatial variability. Consolidated layer is consistent.


#All ridges:
#locations of DTC and SIMBA are visible in GEM-2 data - should be masked (FR1, A1)
#possible accumulations of platellet ice detected?
#what is the precision of the estimates: 1 meter?
#melt onset in April

#WARNING: check that the FB in the drill holes is leveled and roughly corresponds to zero level - adjust ALS surface elevation!
#WARNING: check that the snow depth at the drill holes ~corresponds to the MP snow depth


#Colocation procedure
#1. take ALS coordinates as truth
#2. fine tune transect position to correspond photo, elevation, crest location
#3. adjust ROV MB to get the best match with the drill hole draft
#3b adjust ALS elevation according to freeboard
#4. select the right channels for both ridges based on draft from ROV and drill hole data

#TO DO NEXT: 
#add snow transects: some plot of mean snow depth in the ridges compared to level ice/transect paper/level ice in Nloop?
#large draft footprints should be close to GEM total thickness - do they correspond to 4x thickness?
#use 2 SD to show the 90% percentils. Also check if the distributions are normal. Box plots? Maybe do this for FR2, our best matched transect.
#correlation of total thickness from transects and ROV-ALS for Nloop and roads
#make bulk statistics on consolidation, sail height and sail to keel ratio for all these detailed profiles


#check the IMB data for consolidation and keel melt (Salganik and some temperature profiles - when are the temperatures at freezing T)
#optional: how do the hydrostatic equilibrium and ALS-snow match in Nloop? And how do they match in the ridges? What footprint do we need to use, so that they match > spatial resolution, sampling guidance
#optional: for the matched ROV-MB and ALS topography: ridge statistics: ratio between sail and keel: width, volume, is EM giving the right volume?
#optional: how consolidated are the other ridges in the Nloop from leg 1 to leg3.
#address the difference between point and pulk ridge transects and give recommendations: stronger smoothing, but otherwise fine (not always practical on steep sails, hard to repeat precicely as they are often done without the tape and the pulk is less controlable on this surface with extreme horizontal spatial variability). GPS coordinates sub 1m precision and MP and GEM-2 are high to translate to point measurements as they can be done along the tape. However they are done in much shorter time (maybe 10 times!) and can be good 'better then nothing option'.
#scatter plot of snow deposition rate and ridge consolidation rate in 2 meter footprint?
#outlook: modeling of heat fluxes in snow-covered consolidating winter ridges (references to IMB and snow pit data)



#MOSAiC
inpath = '../data/ridges/'
inpath_table = '../data/MCS/GEM2_thickness/09-ridges-recal/'
outpath = '../plots_ridges/'
#outpath = '../plots_ridges_test/'

#elevation from ALS 
als_elev=True
#als_elev=False

#loc = 'ridgeFR1'
##dates = ['20200108','20200119','20200221']#,'20200305'] #GEM-2 was not used on 20200119
#dates = ['20200108','20200221']
#start = [0,1]
#elev_bias = [0.3,0.2,]  #manual adjustment to have freeboard measurements for drill holes at about zero elevation
#title = 'Fort Ridge Installation Transect '
#startx = [8,8]
#endx = [45,45]

#loc = 'ridgeFR2'    #coring
#dates = ['20200110','20200212','20200221'] #GEM-2 was not used on 20200221
#dates = ['20200110','20200212','20200305']  #Looks like Robert did the coring transect by mistake
#start = [0,0,6]
#elev_bias = [0.2,0.2,0.2]  #manual adjustment to have freeboard measurements for drill holes at about zero elevation
#title = 'Fort Ridge Coring Transect '
#startx = [28,28,28]
#endx = [69,69,69]

loc = 'ridgeFR3'
dates = ['20200131']
start = [0]
elev_bias = [0.2]
title = 'Fort Ridge Optics Transect '
startx = [10]
endx = [30]

loc = 'ridgeA1'    #central
dates = ['20200117','20200131','20200228','20200410','20200628']
#dates = ['20200117','20200131','20200228','20200628']
start = [0,-4,-8,0,0]   #some transect lines were extended X meters over the Nloop/road
elev_bias = [.5,-.5,-.5,-.5,-.5]   #not important as we dont have draft data here
title = "Alli's Ridge Central Transect "
startx = [0,0,0,0,0]
endx = [43,43,43,43,43]

loc = 'ridgeA2'    #north
dates = ['20200212','20200228','20200410','20200628']
#dates = ['20200212','20200228','20200628']
start = [0,-3,10,13]
elev_bias = [.5,0,0,0]
title = "Alli's Ridge North Transect "
startx = [13,13,13,13]
endx = [51,51,51,51]

loc = 'ridgeA3'    #south
dates = ['20200212','20200228','20200410','20200628']
#dates = ['20200212','20200228','20200628']
start = [0,-4,3,3]
elev_bias = [.5,0,0,0]
title = "Alli's Ridge South Transect "
startx = [3,3,3,3]
endx = [47,47,47,47]


#loc = 'ridgeD'  #David's Ridge
#dates = ['20200410','20200416','20200424','20200430','20200507']
#start = [0,0,0,0,0]
#title = "David's Ridge Transect "
#startx = [0,0,0,0,0]
#endx = [22,22,22,22,22]


#loc = 'ridgeE'  #ECO Ridge (lead?)
#dates = ['20200424']
#datel = ['2020/04/24']
#title = "ECO Ridge Transect "

pulk_transects =['20200305','20200410','20200416','20200424','20200430','20200507']

#nice dates for the legend
dt = [ datetime.strptime(x, '%Y%m%d') for x in dates ]
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
datel = [ datetime.strftime(x, '%b, %d %Y') for x in dt ]
#print(datel)

colors = plt.cm.Blues(np.linspace(0, 1, 5))    

fb_list=[]
fb_hs_list=[]
draft_list=[]
draft_m_list=[]
draft_std_list=[]
si_list=[]
ii_list=[]
ic_list=[]
x_list=[]
listlen=[]
modes_list=[]
si_mo_list=[]

for dd in range(0,len(dates)):
    date = dates[dd]
    print(date)

    outname = 'profile_'+date+'_'+loc+'gridded_lf.png'
    
    ##fname = glob(inpath_table+'*/magna+gem2*'+date+'*'+loc+'.csv')[0]
    try:
        #print(inpath_table+date+'/mosaic-*-gem2-*'+loc+'.csv')
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
    
    #pulk (leg 3) and point transects
    #if date in pulk_transects:
        #it3 = getColumn(fname,8);it3 = np.array(it3,dtype=np.float)#5kHz_hcp_i
        #it5 = getColumn(fname,9);it5 = np.array(it5,dtype=np.float)#18kHz_hcp_i
        #it10 = getColumn(fname,10);it10 = np.array(it10,dtype=np.float)#f93075Hz_hcp_q
            
        ##select the channel for the total thickness
        #ii=it3
        
        ##or take mean of both (mask nans)
        #ii = np.empty((2,len(it3)))
        #ii[0,:]=it3
        #ii[1,:]=it5
        #ii = np.mean(np.ma.masked_invalid(ii),axis=0)

        
        ##select the channel for the consolidated layer thickness
        #cc=np.ma.masked_invalid(it10)
        
        
        
    #else:
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
    
    ##select the channel for the total thickness
    ##ii=it5 #18kHz - like for level ice, transect paper
    ##ii=it3 #stable channel that works good for all profiles (expect FR3)
    #ii=it3
    
    ##or take mean of both (mask nans)
    #ii = np.empty((3,len(it3)))
    #ii[0,:]=it3
    #ii[1,:]=it5
    #ii[2,:]=it1
    #ii = np.mean(np.ma.masked_invalid(ii),axis=0)
    
    ##select the channel for the consolidated layer thickness
    ##or mean of all high quadrature channels
    #cc = np.empty((3,len(it3)))
    #cc[0,:]=it6
    #cc[1,:]=it8
    #cc[2,:]=it10
    #cc = np.mean(np.ma.masked_invalid(cc),axis=0)
    
    #ice thickness
    ii = np.empty((3,len(it3)))
    ii[0,:]=np.nan_to_num(it3, nan=-9999)
    ii[1,:]=np.nan_to_num(it5, nan=-9999)
    ii[2,:]=np.nan_to_num(it1, nan=-9999)
    ii = np.mean(np.ma.array(ii,mask=ii<0),axis=0)
            
    #consolidated layer thickness
    cc = np.empty((3,len(it3)))
    cc[0,:]=np.nan_to_num(it6, nan=-9999)
    cc[1,:]=np.nan_to_num(it8, nan=-9999)
    cc[2,:]=np.nan_to_num(it10, nan=-9999)
    cc = np.mean(np.ma.array(cc,mask=cc<0),axis=0)
    
    #find mode of thickness = level ice thickness
    irbins = np.arange(0,10,.06)
    ii_pos = np.ma.array(ii,mask=ii==0);ii_pos=ii_pos.compressed()  #take only non-zero (not detected as negative) values
    hist = np.histogram(ii_pos,bins=irbins)
    srt = np.argsort(hist[0])                           #indexes that would sort the array
    mm = srt[-1]                                        #same as: np.argmax(hist[0])
    mm1 = np.argmax(hist[0])
    mo = (hist[1][mm] + hist[1][mm+1])/2 
    print('mode: ',mo)
    #some ridges have very little ice, use max 1.7m thickness to contrain to level ice 
    #long transcts never have modal thickness over 1.7m
    mo_limit=1.7
    if loc=='ridgeA1':
        mo_limit=3
    if loc=='ridgeA2':
        mo_limit=4.5
    if loc=='ridgeA3':
        mo_limit=3    
    if mo > mo_limit:
        mo = np.mean(np.ma.array(ii_pos,mask=ii_pos>mo_limit))
        print('mode: ',mo)
    
    modes_list.append(mo)
    
    #snow depth on level ice 
    mask=ii>mo+.1
    si_mo = np.mean(np.ma.array(si,mask=mask))
    si_mo_list.append(si_mo)
    
    #plot
    fig1 = plt.figure(figsize=(20,10))
    
    fig1.patch.set_facecolor('0.5')
    fig1.patch.set_facecolor('1')
    
    ax = fig1.add_subplot(111)
    ax.set_xlabel('Distance along transect (m)', fontsize=25)
    ax.set_title(title+datel[dd], fontsize=30, loc='left')
    ax.set_ylabel('Distance from water surface (m)', fontsize=25)
    ax.tick_params(axis="x", labelsize=24)
    ax.tick_params(axis="y", labelsize=24)
    ax.set_facecolor('0.8')

    #surface elevation - determine just for the first of the repeated transects
    if date==dates[0]:
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
    ax.plot(x,fb,label='ice surface Jan, 21 2020',c='k',ls=':')
    ax.fill_between(x, fb, fb+si,alpha=1, color=colors[1], label='snow')
    ax.fill_between(x, fb, fb-cc,alpha=1, color=colors[2], label='consolidated ice')
    ax.fill_between(x, fb, fb-ii,alpha=.3, color=colors[-1], label='max ice')
    if loc=='ridgeFR1' or loc=='ridgeFR2' or loc=='ridgeFR3':
        ax.plot(x,draft,label='draft Jan, 28 2020',c='purple',ls=':',lw=1)
        ax.errorbar(x,draft_m,draft_std,label='mean draft Jan, 28 2020',c='purple',ls=':',lw=3)
    
    #if point transects (not pulk - leg 3)
    #if date not in pulk_transects:
    ax.plot(x, fb-it1,'--w', label='1.5kHz')
    ax.plot(x, fb-it2,'w',ls=':')
    ax.plot(x, fb-it3,'b',ls='--', label='5kHz')
    ax.plot(x, fb-it4,'b',ls=':')
    ax.plot(x, fb-it5,'g',ls='--', label='18kHz')
    ax.plot(x, fb-it6,'g',ls=':')
    ax.plot(x, fb-it7,'r',ls='--', label='60kHz')
    ax.plot(x, fb-it8,'r',ls=':')
    ax.plot(x, fb-it9,'y',ls='--', label='98kHz')
    ax.plot(x, fb-it10,'y',ls=':')
        
    #else:
        #ax.plot(x, fb-it3,'b',ls='--', label='5kHz i')
        #ax.plot(x, fb-it5,'g',ls='--', label='18kHz i')
        #ax.plot(x, fb-it10,'--k', label='98kHz q')

    ax.set_ylim(-12,3)
    
    ax.legend(fontsize=25, ncol=3, loc='lower left',fancybox=True,facecolor=fig1.get_facecolor(),framealpha=.6)
    print(outname)
    #plt.show()
    fig1.savefig(outpath+outname,bbox_inches='tight', facecolor=fig1.get_facecolor(), edgecolor='none')
    

    #save all these data and try to overlay them in a multi-profile plot
    fb_list.append(fb)
    fb_hs_list.append(fb_hs)
    ii_list.append(ii)
    ic_list.append(cc)
    si_list.append(si)
    x_list.append(x)
    listlen.append(len(x))
    
    if loc=='ridgeFR1' or loc=='ridgeFR2' or loc=='ridgeFR3':
        draft_list.append(draft)
        draft_m_list.append(draft_m)
        draft_std_list.append(draft_std)

fig2 = plt.figure(figsize=(20,10))
ax = fig2.add_subplot(111)
ax.set_xlabel('Distance along transect (m)', fontsize=20)
ax.set_title(title, fontsize=25)
ax.set_ylabel('Distance from water surface (m)', fontsize=20)
ax.tick_params(axis="x", labelsize=14)
ax.tick_params(axis="y", labelsize=14)
ax.set_facecolor('0.8')

mean_si_list=[]
mean_cc_list=[]
mean_ii_list=[]
mean_fb_list=[]
mean_fb_hs_list=[]
max_fb_list=[]
max_fb_hs_list=[]

model_si_list=[]
model_ic_list=[]
model_ii_list=[]
model_fb_list=[]
model_x_list=[]

for i in range(0,len(dates)):
    #print(dates[i])

    ax.plot(x_list[i], fb_list[i]-ii_list[i],c=colors[i],label=datel[i])
    ax.plot(x_list[i], fb_list[i]-ic_list[i],c=colors[i],ls='--')
    ax.plot(x_list[i], fb_list[i]+si_list[i],c=colors[i])
    ax.plot(x_list[i],fb_list[i],c=colors[i],ls=':')
    
    #extract just the ridge (no level ice included)
    si = np.argmin(abs(x_list[i]-startx[i]))
    ei = np.argmin(abs(x_list[i]-endx[i]))
    
    #save for modeling input
    model_x_list.append(x_list[i][si:ei])
    model_si_list.append(si_list[i][si:ei])
    model_ic_list.append(ic_list[i][si:ei])
    model_ii_list.append(ii_list[i][si:ei])
    model_fb_list.append(fb_list[i][si:ei])
    
    
    #get means 
    si_mean = np.mean(si_list[i][si:ei]); mean_si_list.append(si_mean)
    cc_mean = np.mean(ic_list[i][si:ei]); mean_cc_list.append(cc_mean)
    ii_mean = np.mean(ii_list[i][si:ei]); mean_ii_list.append(ii_mean)
    fb_mean = np.mean(fb_list[i][si:ei]); mean_fb_list.append(fb_mean)
    fb_hs_mean = np.mean(fb_hs_list[i][si:ei]); mean_fb_hs_list.append(fb_hs_mean)
    fb_max = np.max(fb_list[i][si:ei]); max_fb_list.append(fb_max)
    fb_hs_max = np.max(fb_hs_list[i][si:ei]); max_fb_hs_list.append(fb_hs_max)
    
    #print(si_mean,cc_mean,ii_mean,fb_mean,fb_hs_mean)
    #print(cc_mean/ii_mean)
    
    

ax.plot(x_list[0],fb_hs_list[0],label='hydrostatic ice surface',c='w',ls=':') 
ax.plot(x_list[0],fb_list[0],label='ice surface Jan, 21 2020',c=colors[-1],ls=':')    
ax.fill_between(x_list[0], fb_list[0], fb_list[0]+si_list[0],alpha=1, color=colors[1], label='snow')
ax.fill_between(x_list[0], fb_list[0], fb_list[0]-ic_list[0],alpha=1, color=colors[2], label='consolidated ice')
ax.fill_between(x_list[0], fb_list[0], fb_list[0]-ii_list[0],alpha=.3, color=colors[-1], label='max ice')
if loc=='ridgeFR1' or loc=='ridgeFR2' or loc=='ridgeFR3':
    #ax.plot(x_list[0],draft_list[0],label='draft',c='g',ls=':')
    #ax.errorbar(x_list[0],draft_list[0],draft_std_list[0],label='draft',c='purple',ls=':')
    ax.plot(x_list[0],draft_list[0],label='draft Jan, 28 2020',c='purple',ls=':',lw=1)
    ax.errorbar(x_list[0],draft_m_list[0],draft_std_list[0],label='mean draft Jan, 28 2020',c='purple',ls=':',lw=3)

    
ax.set_ylim(-12,3)
    
#adding drill holes on the ridge
if loc=='ridgeFR1':
    #ridge crest is at 19 m
    d=12
    dh1=.85
    #[x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1]
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1], 'o', c= 'b', ls=':', label='drill hole Jan, 8 2020')
    #freeboard
    ax.plot(x_list[0][d], fb_list[0][d]-.09, 'x', c= 'r')
    ##soft
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.7,fb_list[0][d]-.85], c= 'c', ls='-',lw=3)
    
    d=17    #DTC25
    d=16    #corrected to fit the DTC signal annomaly
    dh1=6.05
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1], 'o', c= 'b', ls=':')
    #freeboard
    ax.plot(x_list[0][d], fb_list[0][d]-.32, 'x', c= 'r',label='freeboard')
    #wet
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.75,fb_list[0][d]-dh1], 'x', c= 'b', ls=':',lw=7,label='soft and wet')
    ##voids
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.65,fb_list[0][d]-1.75], c= 'salmon', ls='-',lw=5,label='void')
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.1,fb_list[0][d]-2.15], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.35,fb_list[0][d]-2.4], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3.25,fb_list[0][d]-3.3], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-4.15,fb_list[0][d]-4.2], c= 'salmon', ls='-',lw=5)
    ##soft
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.3,fb_list[0][d]-1.6], c= 'c', ls='-',lw=3,label='soft')
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.45,fb_list[0][d]-3.15], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3.3,fb_list[0][d]-4.15], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-4.45,fb_list[0][d]-6.], c= 'c', ls='-',lw=3)
    
    d=19    #crest
    dh1=7.1
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1], 'o', c= 'b', ls=':')
    #wet
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3.75,fb_list[0][d]-dh1], 'x', c= 'b', ls=':',lw=7)
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3,fb_list[0][d]-dh1], 'x', c= 'b', ls=':',lw=7)
    ##voids
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-0.35,fb_list[0][d]-0.5], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-0.55,fb_list[0][d]-0.6], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.55,fb_list[0][d]-2.8], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3.75,fb_list[0][d]-4.0], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-4.1,fb_list[0][d]-4.5], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-5,fb_list[0][d]-5.05], c= 'salmon', ls='-',lw=5)
    ##soft
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1,fb_list[0][d]-1.1], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.05,fb_list[0][d]-2.55], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3.,fb_list[0][d]-3.15], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3.35,fb_list[0][d]-3.75], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-5.05,fb_list[0][d]-7.1], c= 'c', ls='-',lw=3)
    
    d=22    #SIMBA
    dh1=6.1
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1], 'o', c= 'b', ls=':')
    #wet
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.3,fb_list[0][d]-dh1], 'x', c= 'b', ls=':',lw=7)
    ##voids
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-0.4,fb_list[0][d]-0.5], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1,fb_list[0][d]-1.15], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.7,fb_list[0][d]-2.8], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-4.2,fb_list[0][d]-4.25], c= 'salmon', ls='-',lw=5)
    ##soft
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.3,fb_list[0][d]-2.7], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3,fb_list[0][d]-3.25], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-5,fb_list[0][d]-6], c= 'c', ls='-',lw=3)
    
    d=27    #DTC24
    dh1=4.1
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1], 'o', c= 'b', ls=':')
    #freeboard
    ax.plot(x_list[0][d], fb_list[0][d]-.19, 'x', c= 'r')
    #wet
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.2,fb_list[0][d]-dh1], 'x', c= 'b', ls=':',lw=7)
    ##voids
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-0.4,fb_list[0][d]-0.5], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.35,fb_list[0][d]-3.8], c= 'salmon', ls='-',lw=5)
    ##soft
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.2,fb_list[0][d]-1.8], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.2,fb_list[0][d]-2.35], c= 'c', ls='-',lw=3)
    
    d=30
    dh1=4.05
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1], 'o', c= 'b', ls=':')
    #wet
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3.1,fb_list[0][d]-dh1], 'x', c= 'b', ls=':',lw=7)
    ##voids
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.65,fb_list[0][d]-1.67], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3,fb_list[0][d]-3.1], c= 'salmon', ls='-',lw=5)
    ##soft
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.25,fb_list[0][d]-.35], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.25,fb_list[0][d]-1.65], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3.1,fb_list[0][d]-4.05], c= 'c', ls='-',lw=3)

if loc=='ridgeFR2':
    #ridge crest is at 44 m
    d=24
    dh1=1.05
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1], 'o', c= 'b', ls=':', label='drill hole Jan, 17 2020')
    #freeboard
    ax.plot(x_list[0][d], fb_list[0][d]-.055, 'x', c= 'r')
    
    d=34
    dh1=2.87
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1], 'o', c= 'b', ls=':')
    #freeboard
    ax.plot(x_list[0][d], fb_list[0][d]-.29, 'x', c= 'r')
    
    d=39
    dh1=3.5
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1], 'o', c= 'b', ls=':')
    #wet
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.55,fb_list[0][d]-dh1], 'x', c= 'b', ls=':',lw=7, label='soft and wet')
    ##void
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.25,fb_list[0][d]-1.55], c= 'salmon', ls='-',lw=5, label='void')
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.85,fb_list[0][d]-2.3], c= 'salmon', ls='-',lw=5)
    ##soft
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.55,fb_list[0][d]-1.85], c= 'c', ls='-',lw=3, label='soft')
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.3,fb_list[0][d]-3.5], c= 'c', ls='-',lw=3)
    
    d=45        #ridge crest is at 44 m
    dh1=4.3
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1], 'o', c= 'b', ls=':')
    #wet
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.3,fb_list[0][d]-dh1], 'x', c= 'b', ls=':',lw=7)
    ##void
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.1,fb_list[0][d]-.23], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.43,fb_list[0][d]-.85], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1,fb_list[0][d]-1.05], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.17,fb_list[0][d]-1.3], c= 'salmon', ls='-',lw=5)
    ##soft
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.3,fb_list[0][d]-4.3], c= 'c', ls='-',lw=3)
    
    d=47
    dh1=2.85
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1], 'o', c= 'b', ls=':')
    #wet
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.7,fb_list[0][d]-dh1], 'x', c= 'b', ls=':',lw=7)
    ##void
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.7,fb_list[0][d]-1.75], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.45,fb_list[0][d]-2.55], c= 'salmon', ls='-',lw=5)
    ##soft
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.75,fb_list[0][d]-1.7], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.75,fb_list[0][d]-2.45], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.55,fb_list[0][d]-2.85], c= 'c', ls='-',lw=3)
    
    d=56
    dh1=3.55
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1], 'o', c= 'b', ls=':')
    #wet
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.8,fb_list[0][d]-dh1], 'x', c= 'b', ls=':',lw=7)
    ##soft
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.2,fb_list[0][d]-2.8], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.8,fb_list[0][d]-3.55], c= 'c', ls='-',lw=3)
    
    d=63
    dh1=1.05
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1], 'o', c= 'b', ls=':')
    #freeboard
    ax.plot(x_list[0][d], fb_list[0][d]-.13, 'x', c= 'r')
    ##void
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.1,fb_list[0][d]-.18], c= 'salmon', ls='-',lw=5)
    ##soft
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.55,fb_list[0][d]-1.05], c= 'c', ls='-',lw=3)

    d=41
    dh1=5.6
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1], 'o', c= 'r', ls=':', label='drill hole Feb, 12 2020')
    #freeboard
    ax.plot(x_list[0][d], fb_list[0][d]-.45, 'x', c= 'r')
    #wet and or soft
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3,fb_list[0][d]-dh1], 'x', c= 'b', ls=':',lw=7)
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.2,fb_list[0][d]-dh1], 'x', c= 'b', ls=':',lw=7)
    ##void
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.26,fb_list[0][d]-.3], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.4,fb_list[0][d]-.45], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.72,fb_list[0][d]-.75], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.42,fb_list[0][d]-4.5], c= 'salmon', ls='-',lw=5)
    ##soft
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.22,fb_list[0][d]-.26], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.3,fb_list[0][d]-.4], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.45,fb_list[0][d]-.51], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.68,fb_list[0][d]-.72], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.75,fb_list[0][d]-1], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.25,fb_list[0][d]-2.42], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-4.5,fb_list[0][d]-5.6], c= 'c', ls='-',lw=3)
    
    d=51
    dh1=3.2
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1], 'o', c= 'r', ls=':')
    #freeboard
    ax.plot(x_list[0][d], fb_list[0][d]-.13, 'x', c= 'r')
    #wet
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.45,fb_list[0][d]-dh1], 'x', c= 'b', ls=':',lw=7)
    ##void
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.2,fb_list[0][d]-.25], c= 'salmon', ls='-',lw=5)
    ##soft
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.26,fb_list[0][d]-2], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.27,fb_list[0][d]-3.2], c= 'c', ls='-',lw=3)
    
if loc=='ridgeFR3':
    #ridge crest at 15m
    d=10
    dh1=4.05
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1], 'o', c= 'b', ls=':', label='drill hole Jan, 24 2020')
    #wet
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.,fb_list[0][d]-dh1], 'x', c= 'b', ls=':',lw=7, label='soft and wet')
    ##voids
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2,fb_list[0][d]-2.5], c= 'salmon', ls='-',lw=5, label='void')
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3.25,fb_list[0][d]-3.32], c= 'salmon', ls='-',lw=5)
    ##soft
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1,fb_list[0][d]-2], c= 'c', ls='-',lw=3, label='soft')
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.5,fb_list[0][d]-3.25], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3.32,fb_list[0][d]-4.05], c= 'c', ls='-',lw=3)
    
    d=12
    dh1=5.15
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1], 'o', c= 'b', ls=':')
    #wet
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.3,fb_list[0][d]-dh1], 'x', c= 'b', ls=':',lw=7)
    ##voids
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.45,fb_list[0][d]-.5], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3.5,fb_list[0][d]-3.57], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3.65,fb_list[0][d]-3.75], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3.85,fb_list[0][d]-3.9], c= 'salmon', ls='-',lw=5)
    ##soft
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.2,fb_list[0][d]-2.3], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.3,fb_list[0][d]-3.5], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3.57,fb_list[0][d]-3.65], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3.74,fb_list[0][d]-3.85], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3.9,fb_list[0][d]-4.3], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-4.75,fb_list[0][d]-5.15], c= 'c', ls='-',lw=3)
    
    d=15        #ridge crest
    dh1=5.75
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1], 'o', c= 'b', ls=':')
    #wet
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3.7,fb_list[0][d]-dh1], 'x', c= 'b', ls=':',lw=7)
    ##voids
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.22,fb_list[0][d]-.41], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.25,fb_list[0][d]-1.28], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.6,fb_list[0][d]-2.61], c= 'salmon', ls='-',lw=5)
    ##soft
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.41,fb_list[0][d]-1.25], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.28,fb_list[0][d]-1.35], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2,fb_list[0][d]-2.6], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.62,fb_list[0][d]-5.75], c= 'c', ls='-',lw=3)
    
    d=20
    dh1=5.6
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1], 'o', c= 'b', ls=':')
    #wet
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.85,fb_list[0][d]-dh1], 'x', c= 'b', ls=':',lw=7)
    ##voids
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-5.3,fb_list[0][d]-5.35], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-5.5,fb_list[0][d]-5.55], c= 'salmon', ls='-',lw=5)
    ##soft
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.75,fb_list[0][d]-4.4], c= 'c', ls='-',lw=3)
    
    d=25
    dh1=5.3
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1], 'o', c= 'b', ls=':')
    #wet
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-4,fb_list[0][d]-dh1], 'x', c= 'b', ls=':',lw=7)
    ##voids
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.3,fb_list[0][d]-.35], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.9,fb_list[0][d]-.98], c= 'salmon', ls='-',lw=5)
    ##soft
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.35,fb_list[0][d]-.9], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-4,fb_list[0][d]-5.3], c= 'c', ls='-',lw=3)

    d=9
    dh1=3.7
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1], 'o', c= 'r', ls=':', label='drill hole Jan, 31 2020')
    #wet
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.45,fb_list[0][d]-dh1], 'x', c= 'b', ls=':',lw=7)
    ##voids
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.9,fb_list[0][d]-2.3], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3.2,fb_list[0][d]-3.4], c= 'salmon', ls='-',lw=5)
    ##soft
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.45,fb_list[0][d]-1.8], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.3,fb_list[0][d]-2.55], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3.65,fb_list[0][d]-3.7], c= 'c', ls='-',lw=3)
    
    d=11
    dh1=3.7
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1], 'o', c= 'r', ls=':')
    #wet
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.75,fb_list[0][d]-dh1], 'x', c= 'b', ls=':',lw=7)
    ##voids
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.5,fb_list[0][d]-.55], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.2,fb_list[0][d]-2.35], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.75,fb_list[0][d]-2.77], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3.1,fb_list[0][d]-3.4], c= 'salmon', ls='-',lw=5)
    ##soft
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.15,fb_list[0][d]-2.2], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.35,fb_list[0][d]-2.4], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3.4,fb_list[0][d]-3.7], c= 'c', ls='-',lw=3)
        
    d=14
    dh1=5.3
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1], 'o', c= 'r', ls=':')
    #wet
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.85,fb_list[0][d]-dh1], 'x', c= 'b', ls=':',lw=7)
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3,fb_list[0][d]-dh1], 'x', c= 'b', ls=':',lw=7)
    ##voids
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.5,fb_list[0][d]-.52], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.75,fb_list[0][d]-.85], c= 'salmon', ls='-',lw=5)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.1,fb_list[0][d]-1.15], c= 'salmon', ls='-',lw=5)
    ##soft
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-.65,fb_list[0][d]-.7], c= 'c', ls='-',lw=3)
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-1.9,fb_list[0][d]-5.3], c= 'c', ls='-',lw=3)
    
    d=21
    dh1=5.4
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d],fb_list[0][d]-dh1], 'o', c= 'r', ls=':')
    #wet
    ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-3.7,fb_list[0][d]-dh1], 'x', c= 'b', ls=':',lw=7)
    ##soft
    #ax.plot([x_list[0][d],x_list[0][d]], [fb_list[0][d]-2.5,fb_list[0][d]-5.45], c= 'c', ls='-',lw=3)
    
if loc=='ridgeA1':
    #the initial list is too short, extend
    x = np.arange(0.,51.)
    fb = np.zeros_like(x); fb[:len(fb_list[0])]=fb_list[0]
    
    d=20
    dh1=6.75
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'b', ls=':', label='drill hole Jan, 17 2020')
    #wet
    ax.plot([x[d],x[d]], [fb[d]-3.05,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7, label='soft and wet')
    #freeboard (this has to be wrong!!! - could it be 9cm?)
    #ax.plot(x[d], fb[d]-.9, 'x', c= 'r')
    ax.plot(x[d], fb[d]-.09, 'x', c= 'r')

    d=25    #crest
    dh1=5.5
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'b', ls=':')
    #wet
    ax.plot([x[d],x[d]], [fb[d]-4,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7) 
    #freeboard
    ax.plot(x[d], fb[d]-1.25, 'x', c= 'r')

    d=35
    dh1=7.95
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'b', ls=':')
    #wet
    ax.plot([x[d],x[d]], [fb[d]-2.5,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
    #freeboard
    ax.plot(x[d], fb[d]-.7, 'x', c= 'r')
    
    d=35    #at 35m, but needs an offset to be visible on the plot
    dh1=7.05
    ax.plot([x[d]+.5,x[d]+.5], [fb[d],fb[d]-dh1], 'o', c= 'r', ls=':', label='drill hole Feb, 5 2020')
    #wet
    ax.plot([x[d]+.5,x[d]+.5], [fb[d]-2.55,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
    #freeboard
    ax.plot(x[d]+.5, fb[d]-.7, 'x', c= 'r')
    
    d=40;
    dh1=6.45
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'r', ls=':')
    #wet
    ax.plot([x[d],x[d]], [fb[d]-2.8,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
    #freeboard
    ax.plot(x[d], fb[d]-.5, 'x', c= 'r')
    
    d=45   #DTC21
    dh1=5.35
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'r', ls=':')
    #wet
    ax.plot([x[d],x[d]], [fb[d]-2.8,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
    #freeboard
    ax.plot(x[d], fb[d]-.2, 'x', c= 'r')
    
    d=47;#print(x_list[1][d])
    dh1=1.1
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'r', ls=':')
    #freeboard
    ax.plot(x[d], fb[d]-.13, 'x', c= 'r')
    
    d=50;#print(x[d])   #should be at 50m
    dh1=0.95
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'r', ls=':')
    #freeboard
    ax.plot(x[d], fb[d]-.09, 'x', c= 'r')
    
    #summer drillings
    #negative x direction it towards Nloop
    d=25    #crest (needs an offset to be visible on the plot)
    dh1=5.
    ax.plot([x[d]+.5,x[d]+.5], [fb[d],fb[d]-dh1], 'o', c= 'm', ls=':', label='drill hole Jul, 15 2020')
    #freeboard
    ax.plot(x[d]+.5, fb[d]-1.2, 'x', c= 'm')
    
    d=27    #2.5m off the crest
    dh1=5.25
    ax.plot([x[d]+.5,x[d]+.5], [fb[d],fb[d]-dh1], 'o', c= 'm', ls=':')
    #wet
    ax.plot([x[d]+.5,x[d]+.5], [fb[d]-5.4,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
    #freeboard
    ax.plot(x[d]+.5, fb[d]-1.1, 'x', c= 'm')
        
    d=22    #2.5m off the crest towards Nloop
    dh1=5.5
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'm', ls=':')
    #freeboard
    ax.plot(x[d], fb[d]-.8, 'x', c= 'm')  
    
    d=25    #crest (needs an offset to be visible on the plot)
    dh1=4.5
    ax.plot([x[d]-.5,x[d]-.5], [fb[d],fb[d]-dh1], 'o', c= 'lime', ls=':', label='drill hole Jul, 26 2020')
    #freeboard
    ax.plot(x[d]-.5, fb[d]-2.3, 'x', c= 'lime')    
    
    d=27    #2.5m off the crest
    dh1=3.6
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'lime', ls=':')
    #freeboard
    ax.plot(x[d], fb[d]-1., 'x', c= 'lime')
    
    d=30    
    dh1=6.6
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'lime', ls=':')
    #wet
    ax.plot([x[d],x[d]], [fb[d]-3.35,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
    #freeboard
    ax.plot(x[d], fb[d]-.7, 'x', c= 'lime')
    
    d=32    #7.5m off the crest
    dh1=6.8
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'lime', ls=':')
    #freeboard
    ax.plot(x[d], fb[d]-.7, 'x', c= 'lime')
    
    d=35    #10m off the crest, offset
    dh1=5.9
    ax.plot([x[d]-.5,x[d]-.5], [fb[d],fb[d]-dh1], 'o', c= 'lime', ls=':')
    #freeboard
    ax.plot(x[d]-.5, fb[d]-.5, 'x', c= 'lime')
    
    d=37    #12.5m off the crest
    dh1=5.45
    ax.plot([x[d]+.5,x[d]+.5], [fb[d],fb[d]-dh1], 'o', c= 'lime', ls=':')
    #freeboard
    ax.plot(x[d]+.5, fb[d]-.35, 'x', c= 'lime')
    
    d=40    #15m off the crest, offset
    dh1=5.1
    ax.plot([x[d]-.5,x[d]-.5], [fb[d],fb[d]-dh1], 'o', c= 'lime', ls=':')
    #wet
    ax.plot([x[d]-.5,x[d]-.5], [fb[d]-4.2,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
    #freeboard
    ax.plot(x[d]-.5, fb[d]-.15, 'x', c= 'lime')
    
if loc=='ridgeA2':   
    #Northern line, crest at 32m
    #negative x direction it towards Nloop
    #positive y: +10: North (closer to the skidoo passage)
    
    d=20
    dh1=3.75
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'm', ls=':', label='drill hole Jul, 9 2020')
    #freeboard
    ax.plot(x[d], fb[d]-1.25, 'x', c= 'm')
    
    d=23
    dh1=6.3
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'm', ls=':')
    #wet
    ax.plot([x[d],x[d]], [fb[d]-3.5,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
    #freeboard
    ax.plot(x[d], fb[d]-.9, 'x', c= 'm')
    
    d=25
    dh1=5.8
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'm', ls=':')
    #freeboard
    ax.plot(x[d], fb[d]-.7, 'x', c= 'm')
    
    d=18
    dh1=5
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'm', ls=':')
    #wet
    ax.plot([x[d],x[d]], [fb[d]-4.25,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
    #freeboard
    ax.plot(x[d], fb[d]-.35, 'x', c= 'm')
    
    d=15
    dh1=5.3
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'm', ls=':')
    #freeboard
    ax.plot(x[d], fb[d]-.4, 'x', c= 'm')
    
    d=20
    dh1=4
    ax.plot([x[d]+.5,x[d]+.5], [fb[d],fb[d]-dh1], 'o', c= 'lime', ls=':', label='drill hole Jul, 15 2020')
    #freeboard
    ax.plot(x[d]+.5, fb[d]-1, 'x', c= 'lime')
    
    d=17
    dh1=4.7
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'lime', ls=':')
    #freeboard
    ax.plot(x[d], fb[d]-.6, 'x', c= 'lime')
    
    d=22
    dh1=4.8
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'lime', ls=':')
    #wet
    ax.plot([x[d],x[d]], [fb[d]-3,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)   #summer unconsolidated layer is likely fresh (snow water) and it is not detected, but maybe it indicates winter voids???
    #freeboard
    ax.plot(x[d], fb[d]-1.1, 'x', c= 'lime')
    
    d=23
    dh1=6.2
    ax.plot([x[d]-.5,x[d]-.5], [fb[d],fb[d]-dh1], 'o', c= 'lime', ls=':')
    #wet
    ax.plot([x[d]-.5,x[d]-.5], [fb[d]-4.1,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
    #freeboard
    ax.plot(x[d]-.5, fb[d]-1.1, 'x', c= 'lime')
    
    d=23
    dh1=5.8
    ax.plot([x[d]+.5,x[d]+.5], [fb[d],fb[d]-dh1], 'o', c= 'lime', ls=':')
    #wet
    ax.plot([x[d]+.5,x[d]+.5], [fb[d]-4.2,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
    #freeboard
    ax.plot(x[d]+.5, fb[d]-.9, 'x', c= 'lime')
    
    d=25
    dh1=5.8
    ax.plot([x[d]+.5,x[d]+.5], [fb[d],fb[d]-dh1], 'o', c= 'lime', ls=':')
    #freeboard
    ax.plot(x[d]+.5, fb[d]-.9, 'x', c= 'lime')
    
if loc=='ridgeA3':   
    #Southern line, crest at 33m
    #negative x direction it towards Nloop
    #negative y: -10: South
    
    d=30
    dh1=6
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'lime', ls=':', label='drill hole Jul, 26 2020')
    #freeboard
    ax.plot(x[d], fb[d]-2, 'x', c= 'lime')
    
    d=32
    dh1=4.8
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'lime', ls=':')
    #wet
    ax.plot([x[d],x[d]], [fb[d]-1.8,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
    #freeboard
    ax.plot(x[d], fb[d]-1, 'x', c= 'lime')
    
    d=35
    dh1=5.5
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'lime', ls=':')
    #wet
    ax.plot([x[d],x[d]], [fb[d]-4.1,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
    #freeboard
    ax.plot(x[d], fb[d]-1.6, 'x', c= 'lime')
    
    d=37
    dh1=5.5
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'lime', ls=':')
    #wet
    ax.plot([x[d],x[d]], [fb[d]-4.4,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
    #freeboard
    ax.plot(x[d], fb[d]-1.7, 'x', c= 'lime')
    
    d=40
    dh1=3.1
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'lime', ls=':')
    #freeboard
    ax.plot(x[d], fb[d]-.6, 'x', c= 'lime')
    
    d=28
    dh1=5.4
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'lime', ls=':')
    #wet
    ax.plot([x[d],x[d]], [fb[d]-.9,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
    #freeboard
    ax.plot(x[d], fb[d]-.65, 'x', c= 'lime')
    
    d=25
    dh1=4.9
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'lime', ls=':')
    #wet
    ax.plot([x[d],x[d]], [fb[d]-.5,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
    #freeboard
    ax.plot(x[d], fb[d]-.4, 'x', c= 'lime')
    
    d=22
    dh1=5.2
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'lime', ls=':')
    #freeboard
    ax.plot(x[d], fb[d]-.4, 'x', c= 'lime')
    
    d=20
    dh1=4.95
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'lime', ls=':')
    #freeboard
    ax.plot(x[d], fb[d]-.15, 'x', c= 'lime')
    
    d=18
    dh1=5.2
    ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'lime', ls=':')
    #freeboard
    ax.plot(x[d], fb[d]-.3, 'x', c= 'lime')
    
    

ax.legend(fontsize=20, ncol=3,loc='lower left',fancybox=True,facecolor=colors[-1],framealpha=.1)
outname = loc+'_profile.png'
plt.show()
fig2.savefig(outpath+outname,bbox_inches='tight')




#write output file for modeling
inpath_table = '../data/ridges_multif/'

dt = [ datetime.strptime(x, '%Y%m%d') for x in dates ]
    
header = b'date,distances\n'
distances = model_x_list[0]
#print(len(distances))

variable = [model_si_list,model_ic_list,model_ii_list,model_fb_list]
varname = ['snow','consolidatedlayer','totalthickness','freeboard']



for vv in range(0,len(varname)):
    
    #print(varname[vv])
    
    model_list = variable[vv]
    
    #print(model_list)

    model_array = np.zeros((len(dates)+1,len(distances)+1))
    #print(model_array.shape)
    model_array[0,1:] = distances
    model_array[1:,0] = dates
    
    for ddd in range(0,len(dates)):
        model_array[ddd+1,1:] = model_list[ddd]
        
    file_name = inpath_table+loc+'_cc_'+varname[vv]+'.csv'

    with open(file_name, 'wb') as f:
        #header
        f.write(header)
        #np.savetxt(f, distances, fmt="%s", delimiter=",")
        np.savetxt(f, model_array, fmt="%s", delimiter=",")



#save the data in file
inpath_table = '../data/ridges_multif/'
file_name = inpath_table+loc+'_cc.csv'
print(file_name)

dt = [ datetime.strptime(x, '%Y%m%d') for x in dates ]

tt = [dt,mean_si_list,mean_ii_list,mean_cc_list,modes_list,si_mo_list,mean_fb_list,mean_fb_hs_list,max_fb_list,max_fb_hs_list]
table = list(zip(*tt))

with open(file_name, 'wb') as f:
    #header
    f.write(b'date,mean ridge snow depth,mean ridge ice thickness,mean consolidated layer thickness,level ice thickness,snow on level ice,mean als ice fb, mean hs ice freeboard,max ALS fb, max HS FB\n')
    np.savetxt(f, table, fmt="%s", delimiter=",")
