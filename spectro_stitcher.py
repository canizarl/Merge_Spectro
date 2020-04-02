import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
from psp_dataprep import data_spectro
import os


class mydate:
    def __init__(mydate,year,month,day):
        mydate.year = year
        mydate.month = month
        mydate.day = day




def load_PSP_data(date,band):
    '''
    Loads data from txt files
    

    Parameters
    ----------
    fnames : list of three strings 
        fname[0]: path and filename to data text file
        fname[1]: path and filename to frequencies text file
        fname[2]: path and filename to time text file
        NOT YET IMPLEMENTED

    Returns
    -------
    data : 2D numpy array of floating points
        Dynamic spectra data
    freq : 1D numpy array of floating points
        Frequencies of the dynamic spectra data
    time : 1D numpy array of floating points
        Time values of the dynamic spectra

    '''

    yearS = date.year
    monthS = date.month
    dayS = date.day 
    cwd = os.getcwd()
    
    directory_extracted =  cwd+"/ExtractedData" 
    directory_year = directory_extracted + "/"+yearS
    directory_month = directory_year + "/"+monthS
    directory = directory_month + "/"+dayS

    fname_data = directory+"/PSP_" + yearS + "_" + monthS + "_" + dayS+"_data_"+band+".txt"
    fname_freq = directory+"/PSP_" + yearS + "_" + monthS + "_" + dayS+"_freq_"+band+".txt"
    fname_time = directory+"/PSP_" + yearS + "_" + monthS + "_" + dayS+"_time_"+band+".txt"

    
    data = np.loadtxt(fname_data, delimiter=",")
    freq = np.loadtxt(fname_freq, delimiter=",")
    time = np.loadtxt(fname_time, delimiter=",")     

    epoch = []
    for i in range(0, len(time)):
        epoch.append(datetime.fromtimestamp(time[i]))

    my_spectro = data_spectro(data,epoch,freq)  
    return my_spectro







if __name__=='__main__':

    day = "26"
    month = "04"
    year = "2019"

    date_open = mydate(year,month,day)

    

    ## import data
    #import PSP h data
    h_data = load_PSP_data(date_open,"h")


    #import PSP l data
    l_data = load_PSP_data(date_open,"l")

    #import lofar data





    # pick a time 



    #plots
    

    
    




    



