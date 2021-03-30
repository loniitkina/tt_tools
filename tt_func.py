import numpy as np
import csv

def getColumn(filename, column, delimiter=',', skipinitialspace=False, skipheader=True, magnaprobe=False):
    results = csv.reader(open(filename),delimiter=delimiter,skipinitialspace=skipinitialspace)
    if skipheader==True:
        next(results, None)
    if magnaprobe==True: #has 4 headers
        next(results, None)
        next(results, None)
        next(results, None)
    return [result[column] for result in results]

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
                elif (fz == False) and (c1==1): 
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

    
    

