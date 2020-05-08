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

def ridge_thick(path,fname):
    it1 = getColumn(path+fname,6, delimiter=',')
    it1 = np.array(it1,dtype=np.float)

    #highest frequency (inpahse) 93075Hz
    it2 = getColumn(path+fname,8, delimiter=',')
    it2 = np.array(it2,dtype=np.float)

    it3 = getColumn(path+fname,9, delimiter=',')
    it3 = np.array(it3,dtype=np.float)
    
    it4 = getColumn(path+fname,10, delimiter=',')
    it4 = np.array(it4,dtype=np.float)

    it5 = getColumn(path+fname,11, delimiter=',')
    it5 = np.array(it5,dtype=np.float)
    
    it6 = getColumn(path+fname,12, delimiter=',')
    it6 = np.array(it6,dtype=np.float)

    it7 = getColumn(path+fname,14, delimiter=',')
    it7 = np.array(it7,dtype=np.float)


    lat = getColumn(path+fname,3, delimiter=',')
    #lon = getColumn(path+fname,2, delimiter=',')
    lat = np.array(lat,dtype=np.float)
    #lon = np.array(lon,dtype=np.float)

    #make mean of values between the 0 values for lat, lon (beginning of each point)
    c=0
    m1=0; m2=0; m3=0; m4=0;m5=0; m6=0;m7=0
    fz=True
    mit1=[]; mit2=[]; mit3=[];mit4=[];mit5=[];mit6=[];mit7=[];
    for i in range(0,len(lat)):
        if lat[i] != 0:
            m1 = m1+it1[i]; m2 = m2+it2[i];m3 = m3+it3[i];m4 = m4+it4[i];m5 = m5+it5[i];m6 = m6+it6[i];m7 = m7+it7[i];
            c = c+1
            fz = True
        else:
            if (fz == True) and (c>0): 
                mm1 = m1/c; mm2 = m2/c; mm3 = m3/c; mm4 = m4/c; mm5 = m5/c; mm6 = m6/c; mm7 = m7/c; 
                mm2 = m2/c
                mit1.append(mm1); mit2.append(mm2); mit3.append(mm3); mit4.append(mm4); mit5.append(mm5); mit6.append(mm6); mit7.append(mm7); 
                fz = False
            c=0
            m1=0; m2=0; m3=0; m4=0;m5=0; m6=0;m7=0
            continue
    return(mit1,mit2,mit3,mit4,mit5,mit6,mit7)
