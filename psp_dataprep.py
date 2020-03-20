#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 * \file psp_dataprep.py
 * \brief 
    Uses cdfopenV3.py to extract radio data from PSP
   	Stiches all the data into one big data file
    Adds the two dipoles to get Stokes I param
    Background subtracts the data
    Saves three .txt files. one for each: data, freq, time 
    default data extracted located at cwd/../../ExtractedData/YEAR/MONTH/
    
    
    NOTES:  User may manually choose the day to be extracted or 
            give the program a range of days and the software
            will extract all the data between those days.
            For more than one day extraction use  day = None
            
            If a day is missing or the data is faulty, it 
            must be flagged. 
            
            
    
 * \author L. A. Canizares
 * \version 2.0
 * \date 2019-11-13

"""



# # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#      Libraries                                      #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # 
from spacepy import pycdf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import numpy as np
from statistics import mode
import math
import os
#import cdfopenV2 as cdfo


class fnames:
    def __init__(fnames,band,year,month,day,dipoles):
        if dipoles == "V1V2":
            ch = "0"
        elif dipoles == "V3V4":
            ch = "1"
        else:
            print("ERROR: class fnames: ch is wrong")


        cwd = os.getcwd()
        fnames.band = band
        fnames.year = year
        fnames.month = month
        fnames.day = day
        fnames.dipoles = dipoles
        fnames.fname = "psp_fld_l2_rfs_"+fnames.band+"_"+fnames.year+fnames.month+fnames.day+"_v01.cdf"
        fnames.path_data = cwd+"/../../DATA/"+fnames.year+"/"+fnames.month+"/"+fnames.band+"/"+fnames.fname
        fnames.dataname = "psp_fld_l2_rfs_"+fnames.band+"_auto_averages_ch"+ch+"_"+fnames.dipoles
        fnames.epochname = "epoch_"+fnames.band+"_auto_averages_ch"+ch+"_"+fnames.dipoles
        fnames.freqname = "frequency_"+fnames.band+"_auto_averages_ch"+ch+"_"+fnames.dipoles





def data_from_CDF(date, myfile):
    cwd = os.getcwd()
    cdf = pycdf.CDF(myfile.path_data)
    # print(cdf)

    data = cdf.get(myfile.dataname)
    epoch = cdf.get(myfile.epochname)
    freqs = cdf.get(myfile.freqname)
    

    data = np.array(data)
    epoch = np.array(epoch)
    freqs = np.array(freqs)
    freqs = freqs[0,:]  
    
    # print(data.shape)
    # print(epoch.shape)
    # print(freqs.shape)
    cdf.close()
    return data, epoch, freqs    









if __name__=='__main__':
    starttime = dt.datetime.now()
    print(' ')
    print(' ')
    print(' Running psp_dataprep.py')
    print(' ')

    year = "2019"
    month = "04"
    day = "09"


    t0 = dt.datetime(int(year),int(month),int(day))

    
    
    # hfr
    my_fileh12 = fnames("hfr",year,month,day,"V1V2")
    my_fileh34 = fnames("hfr",year,month,day,"V3V4")

    # extract from cdf file
    datah12, epochh12, freqsh12 = data_from_CDF(t0, my_fileh12)
    datah34, epochh34, freqsh34 = data_from_CDF(t0, my_fileh34)
    
    # merge V1V2 and V3V4
    datah = np.add(datah12,datah34)     # stokesI
    freqh = freqsh12                    # same as in V3V4
    epochh = epochh12                   # same as in V3V4
    

    
    # lfr
    my_filel12 = fnames("lfr",year,month,day,"V1V2")
    my_filel34 = fnames("lfr",year,month,day,"V3V4")
    # extract from cdf file
    datal12, epochl12, freqsl12 = data_from_CDF(t0, my_filel12)
    datal34, epochl34, freqsl34 = data_from_CDF(t0, my_filel34)

    
    # merge V1V2 and V3V4
    datal = np.add(datal12,datal34)     # stokesI
    freql = freqsl12                    # same as in V3V4
    epochl = epochl12                   # same as in V3V4




    # epochtest = np.subtract(epochl,epochh)
    # for i in range(len(epochtest)):
    #     print(epochtest[i])


    # time resolution
    timediff = []
    for i in range(0,len(epochh)-1):
        diff = epochh[i+1]-epochh[i]
        #print(diff)
        timediff.append(diff)

    timeres = np.mean(timediff)
    print(f"Time res: {timeres}")



    # add gaps   


    


    



    endtime = dt.datetime.now()

    totalrunningtime = endtime - starttime
    print('End of program')
    print(' ')
    print(f"Start Time: {starttime}")
    print(f"End Time: {endtime}")
    print(f"Total running time: {totalrunningtime}")
    print(' ')
