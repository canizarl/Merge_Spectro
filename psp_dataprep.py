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
    """
    This class stores the location of the directories where data is, as well as the names of the datasets to be extracted
    from CDF file. 

    
    band: Either hfr or lfr for high band or low band
    year: year of the observation
    month: month of the observation
    day: day of the observation 
    dipoles: Antenna pair V1V2 or V3V4

    fname - file name
    path_data - path to the data (for now change here but in the future this will be an option)
    dataname - name of dataset in the CDF file
    epochname - name of epoch dataset in the CDF file
    freqname - name of frequency dataset in the CDF file

    """
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


class data_spectro:
    """
    Data class. Data extracted from CDF file will be stored in this class format. 
    With:
    data : 2D matrix of the dynamic spectra
    epoch: 1D array of the time datapoints
    freq: 1D array of the frequency channels used for each data point. 
    """
    def __init__(data_spectro, data, epoch, freq):
        data_spectro.data=data
        data_spectro.epoch=epoch
        data_spectro.freq=freq



def data_from_CDF(date, myfile):
    """ data_from_CDF
     outputs dynamic spectra data from PSP CDF datafile. 
     inputs:
        date: datetime.datetime class. Date of the observation. 
        myfile: fnames class defined in psp_dataprep. Location of all directories 

    output:
        data: 2D numpy matrix of dynamic spectra
        epoch: 1D numpy array of the date and times of each datapoint
        freqs: 1D numpy array of the frequency channels 

    """

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


def add_gaps(data):

    # epochtest = np.subtract(epochl,epochh)
    # for i in range(len(epochtest)):
    #     print(epochtest[i])


    # use the year month and day of the first item in epoch list to get the date of observation
    t0 = data.epoch[0]
    if developer == 1:
        print(f"t0: {t0}")

    # date of observation
    year = t0.year
    month = t0.month
    day = t0.day
     
    # generic begining and end of the day 
    day_start = dt.datetime(year, month, day, 0, 0, 0)
    day_end = day_start + dt.timedelta(days=1)

    if developer == 1:
        print(f"day_start : {day_start}")
        print(f"day_end : {day_end}")
        print(f"day/month/year : {day}/{month}/{year}")


    # check beginning of the day. if Day doesnt start at midnight, add. 
    if data.epoch[0] > day_start:
        if developer ==1:
            if verbose ==1:
                print(data.epoch)
        data.epoch = np.insert(data.epoch,0, values=day_start,axis=0)
        data.data = np.insert(data.data, 0, values=0, axis=0)
        print("Begining of day added")
        



    #check end of the day. if day doesnt end at midnight of next day, add. 
    if data.epoch[-1]<day_end:
        data.epoch = np.insert(data.epoch,len(data.epoch), values=day_end,axis=0)
        data.data = np.insert(data.data, data.data.shape[0], values=0, axis=0)
        print("End of day added")    


    # time resolution
    timediff = []
    for i in range(0,len(data.epoch)-1):
        diff = data.epoch[i+1]-data.epoch[i]
        #print(diff)
        buffer = diff.total_seconds()
        timediff.append(float(buffer))

    timeres = np.mean(timediff)
    print(f"Time res: {timeres}")
    cadence=mode(timediff)
    if developer ==1:
        print(f"cadence type: {type(cadence)}")
    thres = cadence*2
    thres=float(thres)

    inseconds = []
    for each in timediff:
        inseconds.append(float (abs(each)))

    if developer == 1:
        if verbose == 1:
            print(inseconds)
        print(f"inseconds type {type(inseconds[1])}")
        print(f"thres type {type(thres)}")
        print(f"timediff type {type(timediff[i])}")

    

    # Find gaps and measure their lengths    
    gap_indices = []
    gap_lengths = []
    for i in range(0,len(inseconds)):
        if inseconds[i]>thres:
            gap_indices.append(i)
            gap_lengths.append(round(inseconds[i]/cadence))


    # Add gaps
    cadence_dt=dt.timedelta(seconds=cadence)
    index_offset = 0
    for j in range(0,len(gap_indices)):
        for i in range(0, gap_lengths[j]):
            current_gap_index = gap_indices[j]+i+index_offset
            print(current_gap_index)
            data.epoch = np.insert(data.epoch,current_gap_index, values=data.epoch[current_gap_index-1]+cadence_dt,axis=0)
            data.data = np.insert(data.data, current_gap_index, values=0, axis=0)
        index_offset = index_offset + gap_lengths[j]
        
            





    if developer == 1:
        print(f"Length gap_indices: {len(gap_indices)}")
        print(f"gap_indices: {gap_indices}")
        print(f"gap_lengths: {gap_lengths}")



    if developer == 1:
        plt.figure(2)
        plt.plot(inseconds[:], 'r-')
        plt.plot(inseconds[:], 'r*')
        c = 0
        for i in range(0, len(inseconds)):
            if c < len(gap_indices):
                if i == gap_indices[c]:
                    plt.plot(gap_indices[c],inseconds[i],'b*')    
                    c= c+1
            else:
                break
        plt.show()

    return data
            











if __name__=='__main__':
    developer = 1
    verbose = 0
    starttime = dt.datetime.now()
    print(' ')
    print(' ')
    print(' Running psp_dataprep.py')
    print(' ')

    year = "2019"
    month = "04"
    day = "20" #"18"

    add_gaps_option= 1


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

    lsd = data_spectro(datal,epochl,freql)      #lowband spectral data
    hsd = data_spectro(datah,epochh,freqh)      #highband spectral data

    

    # add gaps 
    if add_gaps_option == 1:
        print("add_gaps not implemented yet")
        lsd = add_gaps(lsd)
        hsd = add_gaps(hsd)

    
    



    
    
    
    
    if developer == 1:
        # quick plot for now. 
        v_min = np.percentile(hsd.data, 1)
        v_max = np.percentile(hsd.data, 99)
        plt.figure(1)
        plt.imshow(hsd.data.T, aspect='auto', vmin=v_min, vmax=v_max)
        plt.show()
        




    endtime = dt.datetime.now()

    totalrunningtime = endtime - starttime
    print('End of program')
    print(' ')
    print(f"Start Time: {starttime}")
    print(f"End Time: {endtime}")
    print(f"Total running time: {totalrunningtime}")
    print(' ')
