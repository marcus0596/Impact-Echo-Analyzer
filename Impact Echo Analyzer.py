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

start = time.time()

class ImpactEcho:
    def __init__(self,root=lvm_folder,freq_offset=200,delam_threshold=5000):
        self.ROOT = root
        self.delam_folder = os.path.join(self.ROOT,'Delaminations')
        self.non_folder = os.path.join(self.ROOT,'Non Delaminations')
        self.LVM_FILES = [files for files in os.listdir(self.ROOT) if 
                     files.lower().endswith('.lvm')]
        self.FREQ_OFFSET = freq_offset
        self.DELAM_THRESHOLD = delam_threshold
        self.comments = pd.DataFrame(columns=['filename','comment'])
        
        
    def ffTransform(self,data):
        # length of the signal
        n = len(data)  
        
        # fft computing and normalization
        amp = np.fft.fft(data.Acceleration) / n  
        amp = abs(amp[range(int(n / 2))])
        amp = amp / max(amp)
        
        return amp[self.DELAM_THRESHOLD:]
    
    def Analysis(self):
        start = time.time()
        
        
        for i in range(len(self.LVM_FILES)):
            # Prepare data
            df = pd.read_csv(os.path.join(self.ROOT,self.LVM_FILES[i]),
                                skiprows=22, delimiter='\t')
            df.rename(index={0:'X_Value', 1:'Acceleration'})
            amp = self.ffTransform(df)
            
            # Determine if there's a delamination
            if np.argmax(amp)<=self.DELAM_THRESHOLD:
                self.comments = self.comments.append({'filename':self.LVM_FILES[i],
                                      'comment':'good'},ignore_index=True)
            else:
                self.comments = self.comments.append({'filename':self.LVM_FILES[i],
                                      'comment':'bad'},ignore_index=True)
        
        # Save csv of comments
        self.comments.to_csv(os.path.join(self.ROOT,'Impact Echo Comments.csv'),
                             index=False)
        
        
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
        
        # Move files to their respective folders
        for i in range(len(self.comments)):
            src = os.path.join(self.ROOT,self.comments[i][0])
            if self.comments[i][1]=='good':
                 dst = os.path.join(self.ROOT,self.non_folder,
                                    self.comments[i][0])
                 shutil.move(src,dst)
            else:
                 dst = os.path.join(self.ROOT,self.delam_folder,
                                    self.comments[i][0])
                 shutil.move(src,dst)
                 
    def undo(self):
        
        # Check folder existence, then move files to root and delete folder
        if os.path.isdir(self.delam_folder):
            for bad in os.listdir(self.delam_folder):
                src = os.path.join(self.delam_folder,bad)
                shutil.move(src,self.ROOT)
        
            os.rmdir(self.delam_folder)
        
        if os.path.isdir(self.non_folder):        
            for good in os.listdir(self.non_folder):
                src = os.path.join(self.non_folder,good)
                shutil.move(src,self.ROOT)
                
            os.rmdir(self.non_folder)
            
        comment_path = os.path.join(self.ROOT,'Impact Echo Comments.csv') 
        if os.path.isfile(comment_path):
            os.remove(comment_path)
 
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
ie = ImpactEcho(lvm_folder)
ie.Analysis()
#ie.moveFiles()
#ie.undo()
#ie.Plot()
