import numpy as np
from glob import glob
import yaml
import matplotlib.pyplot as plt
from sitem1d.transform import EMPEX

outpath = '../plots/'

#set up plot
plt.figure(figsize=(12, 5))
plt.xticks(np.arange(0.0, 5.1, 0.5))
plt.yticks(np.arange(0.0, 71000, 5000))
plt.xlim([0, 5])
plt.ylim([0, 70000])
plt.grid(lw=1)
plt.xlabel("Distance GEM-2 -> ice-ocean interface (m)", fontsize=20)
plt.ylabel("EM reading (ppm)", fontsize=20)
#plt.title("GEM-2 Thickness Cheatsheet (Inphase 18325Hz)", fontsize=20)


#ax = plt.gca()
#for target in ['xmajorticklabels', 'ymajorticklabels']:
    #xmtl = plt.getp(ax, target)
    #plt.setp(xmtl)
    #ax.tick_params(which="both", direction="out", width=0.5, length=8)

#values range
ppm = np.arange(100, 70000, 100)

#get a list of all empex files
inpath = '../data/MCS/GEM2_thickness/01-ice-thickness/empex-fit/'
fnames = sorted(glob(inpath+'gem2-556_calibration_*_PS122-[1-3]?*.yaml'))
#print(fnames)

colors = plt.cm.rainbow(np.linspace(0, 1, len(fnames)))

#read 18kHz coeficients
for i in range(0,len(fnames)):
    fn=fnames[i]
    
    date = fn.split('_')[3]
    print(date)
    
    # Read the yaml calibration file
    with open(fn, 'r') as f:
        yf = yaml.safe_load(f)
        
        c1,c2,c3 = yf['channel_data']['f18325Hz_hcp']['inphase']['coefs']

    coefs_18kHz_i = [c1, c2, c2]
    distance = EMPEX.single_exponential_inverse(ppm, coefs_18kHz_i)
    plt.plot(distance, ppm, lw=3, label=date, color=colors[i])


plt.legend(ncol=5)
plt.savefig(outpath+"gem2-18kHz-cheatsheet.png",bbox_inches='tight')
