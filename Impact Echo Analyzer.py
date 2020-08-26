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
import shutil
import time


lvm_folder = 'C:\Users\marcusl\Downloads\Training\Impact-Echo-Analyzer\Files Needing Categorization\lvm'
delam_folder = 'C:\Users\marcusl\Downloads\Training\Impact Echo Analysis\Delamination'
non_folder = 'C:\Users\marcusl\Downloads\Training\Impact Echo Analysis\No Delamination'

start = time.time()

class ImpactEcho:
    def __init__(self,root=lvm_folder,freq_offset=200):
        self.root = root
        self.delam_folder = os.path.join(self.root,'Delaminations')
        self.non_folder = os.path.join(self.root,'Non Delaminations')
        self.LVM_FILES = [files for files in os.listdir(self.root) if 
                     files.lower().endswith('.lvm')]
        self.FREQ_OFFSET = freq_offset
        self.FREQ_THRESHOLD=8000
        self.comments = []
        
        
    def ffTransform(self,data):
        
        n = len(data)  # length of the signal
    
        amp = np.fft.fft(data.Acceleration) / n  # fft computing and normalization
        amp = abs(amp[range(int(n / 2))])
        amp = amp / max(amp)
        
        return amp[self.FREQ_THRESHOLD:]
    
    def Analysis(self,FREQ_THRESHOLD=8000):
        start = time.time()
        self.FREQ_THRESHOLD = FREQ_THRESHOLD
        
        # Prepare data
        for i in range(len(self.LVM_FILES)):
            df = pd.read_csv(os.path.join(self.root,self.LVM_FILES[i]),
                                skiprows=22, delimiter='\t')
            df.rename(index={0:'X_Value', 1:'Acceleration'})
            amp = self.ffTransform(df)
            
            if np.argmax(amp)<=self.FREQ_THRESHOLD:
                self.comments.append([self.LVM_FILES[i],'good'])
            else:
                self.comments.append([self.LVM_FILES[i],'bad'])
        
        timed = round(time.time() - start,3)
        print 'Analysis took {timed} seconds.'.format(timed=timed)
        
    def moveFiles(self):
        # Analyze data
        self.Analysis()
        
        # Create folders
        try:
            os.mkdir(self.delam_folder)
        except:
            pass
        try:
            os.mkdir(self.non_folder)
        except:
            pass
        
        for i in range(len(self.comments)):
            src = os.path.join(self.root,self.comments[i][0])
            if self.comments[i][1]=='good':
                 dst = os.path.join(self.root,self.non_folder,
                                    self.comments[i][0])
                 shutil.move(src,dst)
            else:
                 dst = os.path.join(self.root,self.delam_folder,
                                    self.comments[i][0])
                 shutil.move(src,dst)
                 
    def undo(self):
        if os.path.isdir(self.delam_folder):
            for bad in os.listdir(self.delam_folder):
                src = os.path.join(self.delam_folder,bad)
                shutil.move(src,self.root)
                
            for good in os.listdir(self.non_folder):
                src = os.path.join(self.non_folder,good)
                shutil.move(src,self.root)
                
            os.rmdir(self.delam_folder)
            os.rmdir(self.non_folder)
 
    def Plot(self):
        #Perform FFT
        self.ffTransform()
        
        #Plot results
        plt.subplot(2,1,1)
        plt.plot(self.data.X_Value, self.data.Acceleration)
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.subplot(2,1,2)
        plt.plot(self.freq,self.amp)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Amplitude')
        plt.show()

test=os.path.join(lvm_folder,'test')
ie = ImpactEcho(test)
ie.moveFiles()
#ie.undo()
#ie.Plot()
