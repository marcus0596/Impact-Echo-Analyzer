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


lvm_folder = 'C:\Users\marcusl\Downloads\Training\Impact Echo Analysis\Files Needing Categorization\lvm'
delam_folder = 'C:\Users\marcusl\Downloads\Training\Impact Echo Analysis\Delamination'
non_folder = 'C:\Users\marcusl\Downloads\Training\Impact Echo Analysis\No Delamination'

start = time.time()

class ImpactEcho:
    def __init__(self,path=lvm_folder,freq_offset=200):
        self.path = path
        self.freq_offset = freq_offset
        
        # Prepare data
        self.data = pd.read_csv(path,skiprows=22, delimiter='\t')
        self.data.rename(index={0:'X_Value', 1:'Acceleration'})
        
        # Calculate the sampling frequency
        self.Fs=1 / (self.data.X_Value[1])
        
    def ffTransform(self):
        n = len(self.data)  # length of the signal
        k = np.arange(n)
        T = n / self.Fs
        freq = k / T  # two sides frequency range
        freq = freq[range(int(n / 2))]  # one side frequency range
    
        amp = np.fft.fft(self.data) / n  # fft computing and normalization
        amp = abs(amp[range(int(n / 2))])
        amp = amp / max(amp)
    
        return freq[self.freq_offset:], amp[self.freq_offset:]
    
    def Plotter(self):
        #Perform FFT
        freq,amp= self.ffTransform(self.data.Acceleration, self.Fs)
        
        #Plot results
        plt.subplot(2,1,1)
        plt.plot(data.X_Value, data.Acceleration)
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.subplot(2,1,2)
        plt.plot(freq[200:],amp[200:])
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Amplitude')
        plt.show()

print time.time() - start