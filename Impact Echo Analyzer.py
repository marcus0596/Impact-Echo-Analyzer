# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 12:42:06 2020

@author: marcusl

Sort Impact Echo .lvm files into delam/ non-delam folders
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import time


lvm_folder = 'C:\Users\marcusl\Downloads\Training\Impact-Echo-Analyzer\Files Needing Categorization\lvm'
delam_folder = 'C:\Users\marcusl\Downloads\Training\Impact Echo Analysis\Delamination'
non_folder = 'C:\Users\marcusl\Downloads\Training\Impact Echo Analysis\No Delamination'

start = time.time()

class ImpactEcho:
    def __init__(self,PATH=lvm_folder,FREQ_OFFSET=200):
        self.PATH = PATH
        self.LVM_FILES = [files for files in os.listdir(self.PATH) if 
                     files.lower().endswith('.lvm')]
        self.FREQ_OFFSET = FREQ_OFFSET
        
        # Prepare data
        self.data = pd.read_csv(os.path.join(self.PATH,self.LVM_FILES[0]),
                                skiprows=22, delimiter='\t')
        self.data.rename(index={0:'X_Value', 1:'Acceleration'})
        
    def ffTransform(self):
        
        # Calculate the sampling frequency
        Fs=1 / (self.data.X_Value[1])
        
        n = len(self.data)  # length of the signal
        k = np.arange(n)
        T = n / Fs
        self.freq = k / T  # two sides frequency range
        self.freq = self.freq[range(int(n / 2))]  # one side frequency range
    
        self.amp = np.fft.fft(self.data[['Acceleration']]) / n  # fft computing and normalization
        self.amp = abs(self.amp[range(int(n / 2))])
        self.amp = self.amp / max(self.amp)
    
    def Plot(self):
        #Perform FFT
        self.ffTransform()
        
        #Plot results
        plt.subplot(2,1,1)
        plt.plot(self.data.X_Value, self.data.Acceleration)
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.subplot(2,1,2)
        plt.plot(self.freq[200:],self.amp[200:])
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Amplitude')
        plt.show()
        
    def Analysis(self):
        
        
        comments = []
        pass

ie = ImpactEcho()
ie.Plot()

print time.time() - start