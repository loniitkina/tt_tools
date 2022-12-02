import numpy as np
import matplotlib.pyplot as plt
from tt_func import getColumn, proj_sat, logfit


outpath='../plots_tsx/3x3km_revision/'

fig1 = plt.figure(figsize=(10,10))
ax = fig1.add_subplot(111)

#open file
window_name='1x1'  #used in paper - gives largest sample
#window_name='4x4'
#window_name='7x7'
#window_name='9x9'
#windows = ['1x1','4x4','7x7','9x9']

#colors
lfyi = [255/255,255/255,0/255,255/255]
dmyi = [200/255,0/255,0/255,255/255]
vdmyi = [200/255,111/255,111/255,255/255]

inpath = '../data/TSX_Wenkai/classified_geotiffs_new/'

#for window_name in windows:
fname = inpath+'scatter_data_'+window_name+'.csv'

x_data = getColumn(fname,0, delimiter=',')
x_data = np.array(x_data,dtype=np.float)     

y_data = getColumn(fname,1, delimiter=',')
y_data = np.array(y_data,dtype=np.float)

#all data
#ax.scatter(x_data,y_data,c='.5',alpha=.5)

x_model,y_model,RMSE,Rsquared = logfit(x_data,y_data)

ax.plot(x_model, y_model, '--k', lw=5 ,label='log-fit')

##add some text
#ax.text(2.5, -16, '$R^2$: '+str(np.round(Rsquared,2)), ha="center", va="center", size=20)
#ax.text(2.5, -17, 'RMSE: '+str(np.round(RMSE,2)), ha="center", va="center", size=20)


#Make averages over these 3 classes and fit the line. Do log-log plot.
#From paper
#4. Level FYI (LFYI): smooth FYI areas having intermediate HH intensities, between leads and DYI ($-25$ dB and $-15$ dB).
#5. Dark MYI (DMYI): MYI with relatively low HH intensities (between $-15$ dB and $-10$ dB). The majority of MYI areas are in this class, which is assumed to be MYI with less deformation. In this study, second-year ice (SYI) is grouped into the MYI category.
#6. Bright MYI or deformed FYI (BMYI/DefFYI): thick ice (FYI or MYI) surfaces having relatively high HH intensities ($\geq-10$ dB).

level = x_data>.2
level_x = np.mean(np.ma.array(x_data,mask=level))
level_y = np.mean(np.ma.array(y_data,mask=level))   #this should fall in -25 to -15
print(level_y)

ax.scatter(np.ma.array(x_data,mask=level).compressed(),np.ma.array(y_data,mask=level).compressed(),c=lfyi,alpha=.3,label='LFYI')
ax.plot(level_x,level_y,'*',ms=15,markeredgewidth=1,markeredgecolor='k',c=lfyi)

rubble = (x_data<.2) | (x_data>.5)
rubble_x = np.mean(np.ma.array(x_data,mask=rubble))
rubble_y = np.mean(np.ma.array(y_data,mask=rubble))   #this should fall in -15 to -10
print(rubble_y)
ax.scatter(np.ma.array(x_data,mask=rubble).compressed(),np.ma.array(y_data,mask=rubble).compressed(),c=dmyi,alpha=.3,label='DMYI')
ax.plot(rubble_x,rubble_y,'*',ms=15,markeredgewidth=1,markeredgecolor='k',c=dmyi)

ridge = x_data<.5
ridge_x = np.mean(np.ma.array(x_data,mask=ridge))
ridge_y = np.mean(np.ma.array(y_data,mask=ridge))   #this should be around -10
print(ridge_y)

ax.scatter(np.ma.array(x_data,mask=ridge).compressed(),np.ma.array(y_data,mask=ridge).compressed(),c=vdmyi,alpha=.3,label='BMYI/DefFYI')
ax.plot(ridge_x,ridge_y,'*',ms=15,markeredgewidth=1,markeredgecolor='k',c=vdmyi)

#dummy for legend
ax.plot(-1,0,'*',ms=15,markeredgecolor='k',c='w',label='class means')

#x_model,y_model,RMSE,Rsquared = logfit([level_x,rubble_x,ridge_x],[level_y,rubble_y,ridge_y])
#ax.plot(x_model, y_model,label='means')

#log-log plot
#ax.set_xscale('log')
#ax.set_yscale('log')

ax.set_xlabel('Roughness (m)',fontsize=20) # X axis data label
ax.set_ylabel('Intensity (dB)',fontsize=20) # Y axis data label

ax.set_xlim(0,3)
ax.set_ylim(-23,-5)

ax.legend(fontsize=20)
fig1.savefig(outpath+'power_'+window_name,bbox_inches='tight')
#fig1.savefig(outpath+'power_all',bbox_inches='tight')

plt.close(fig1)    

