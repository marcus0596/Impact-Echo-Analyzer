# -*- coding: utf-8 -*-
"""
 Marcus Lowry
 August 27, 2020
 Python 3.8
 
 Importing data from Impact Echo tests and plotting the response
 Sort Impact Echo .lvm files into delam/ non-delam folders
 
 To Do:
 Be able to select range with mouse
 Display max value on graph 
"""

import wx
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
import os
import shutil
import time

class MyApp(wx.App):
    def __init__(self):
        super().__init__(clearSigInt=True)
        
        # Create window
        frame = Main(parent=None,title="Impact Echo Analysis",
                     pos=(100,100),size=(600,600))
        frame.Show()
        self.SetTopWindow(frame)
        
        
class Main(wx.Frame):
    
    def __init__(self,parent,title,pos,size):
        super().__init__(parent=parent,title=title,pos=pos,size=size)
        
        # Top half and bottom half of window
        splitter = wx.SplitterWindow(self)
        top = Plotter(splitter)
        bottom = UserInput(splitter, top)
        splitter.SplitHorizontally(top,bottom)
        splitter.SetMinimumPaneSize(300)
        
        top.draw([0],[0],'Time')
        

class Plotter(wx.Panel):
    def __init__(self,parent):
        super().__init__(parent=parent)
        self.freq = []
        self.amp = []
        
        # matplotlib has nice functionally with wxPython
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)  
        self.canvas = FigureCanvas(self,-1,self.figure)
            
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas,-1,wx.EXPAND|wx.ALL)
        self.SetSizer(sizer)
        
        self.figure.tight_layout(pad=4.0)

    def draw(self,x,y,domain):
        self.axes.clear()
        if domain == 'Time':
            self.axes.set_xlabel("Time")
            self.axes.set_ylabel("Acceleration")
        else:
            self.axes.set_xlabel("Frequency")
            self.axes.set_ylabel("Amplitude")
            
        self.axes.plot(x,y)
        self.canvas.draw()
        
        
        
class UserInput(wx.Panel):

    def __init__(self,parent,top):
        super().__init__(parent=parent)
        self.graph = top
        self.maxVal_amp = 0
        self.maxVal_freq = 0
        self.files = []
        self.root = r''
        self.file_index = 0
        self.domain = 'Time'
        
        # Folder Selection
        self.folder_Label = wx.TextCtrl(self,-1,'')
        self.folder_Label.SetEditable(False)
        self.folderButton = wx.Button(parent=self, label = "Select File")
        self.folderButton.Bind(event=wx.EVT_BUTTON, 
                               handler=self.onSubmitFolder)
        
        # Domain Range Selection
        self.min_X_Label = wx.StaticText(self, -1, "Min X ")
        self.min_X = wx.TextCtrl(self, -1, "0")
        self.max_X_Label = wx.StaticText(self, -1, "Max X")
        self.max_X = wx.TextCtrl(self, -1, "50000")
        self.buttonRange = wx.Button(self, 1, "Set Range")
        self.buttonRange.Bind(wx.EVT_BUTTON, self.onSubmitRange)
        
        # Showing max value on screen
        self.peak = wx.StaticText(self, -1, 
                          "Peak amplitude is \n{amp} dB at {freq} Hz"
                          .format(amp=round(self.maxVal_amp,2), 
                          freq=round(self.maxVal_freq,2)),style=wx.TE_READONLY)
        
        # Time/ Frequency Domain Selection
        self.inputDomain_Time = wx.CheckBox(parent=self,
                                            label='Time Domain')
        self.inputDomain_Freq = wx.CheckBox(parent=self,
                                            label='Frequency Domain')
        # Default to time domain
        self.inputDomain_Time.SetValue(True)
        
        self.Bind(wx.EVT_CHECKBOX, self.onChecked)
        
        # Zoom
        self.buttonZoom = wx.Button(self,1,"Zoom")
        self.buttonZoom.Bind(wx.EVT_BUTTON, self.onZoom)
        
        # Reset zoom
        self.buttonResetZoom = wx.Button(self,1,'Reset')
        self.buttonResetZoom.Bind(wx.EVT_BUTTON, self.onResetZoom)
        self.buttonResetZoom.Hide()
        
        # File selection
        self.file_select_Label = wx.StaticText(self,wx.ID_ANY,'File #')
        self.file_select = wx.SpinCtrl(self,value='1')
        self.file_select.Bind(event=wx.EVT_SPINCTRL,
                               handler=self.onSubmitFile)
        
        # Analyze folder
        self.buttonAnalyze = wx.Button(self,1,"Analyze\nFolder")
        self.buttonAnalyze.Bind(wx.EVT_BUTTON, self.onAnalyze)
    
        # Undo
        self.buttonUndo = wx.Button(self,1,"Undo\nAnalysis")
        self.buttonUndo.Bind(wx.EVT_BUTTON, self.onUndo)
        
        # File Label
        self.file_Label = wx.StaticText(self,wx.ID_ANY,'')
        
        # Proportional sizing
        folderSizer = wx.BoxSizer(wx.HORIZONTAL)
        folderSizer.AddStretchSpacer(1)
        folderSizer.Add(self.folder_Label,2,wx.EXPAND|wx.ALL,5)
        folderSizer.AddStretchSpacer(1)
        
        leftSizer = wx.BoxSizer(wx.VERTICAL)
        leftSizer.Add(self.min_X_Label,0,wx.ALIGN_CENTRE|wx.ALL,0)
        leftSizer.Add(self.min_X,0,wx.ALIGN_RIGHT|wx.ALL,5)
        leftSizer.Add(self.max_X_Label,0,wx.ALIGN_CENTRE|wx.ALL,0)
        leftSizer.Add(self.max_X,0,wx.ALIGN_RIGHT|wx.ALL,5)
        leftSizer.Add(self.buttonRange,0,wx.ALIGN_CENTRE|wx.ALL,5)
        leftSizer.Add(self.peak,0,wx.ALIGN_CENTRE|wx.ALL,5)
        
        midSizer = wx.BoxSizer(wx.VERTICAL)
        midSizer.Add(self.folderButton,0,wx.ALIGN_CENTRE|wx.ALL,5)
        midSizer.AddSpacer(5)
        midSizer.Add(self.inputDomain_Time,0,wx.ALIGN_LEFT|wx.ALL,5)
        midSizer.Add(self.inputDomain_Freq,0,wx.ALIGN_LEFT|wx.ALL,5)
        midSizer.Add(self.buttonZoom,0,wx.ALIGN_CENTRE|wx.ALL,5)
        midSizer.Add(self.buttonResetZoom,0,wx.ALIGN_CENTRE|wx.ALL,5)
        
        rightSizer = wx.BoxSizer(wx.VERTICAL)
        rightSizer.Add(self.file_select_Label,0,wx.ALIGN_LEFT|wx.ALL,5)
        rightSizer.AddSpacer(8)
        rightSizer.Add(self.file_select,0,wx.ALIGN_LEFT|wx.ALL,5)
        rightSizer.Add(self.buttonAnalyze,0,wx.ALIGN_CENTRE|wx.ALL,5)
        rightSizer.Add(self.buttonUndo,0,wx.ALIGN_CENTRE|wx.ALL,5)
        rightSizer.Add(self.file_Label,0,wx.ALIGN_LEFT|wx.ALL,5)
       
        inputSizer = wx.BoxSizer(wx.HORIZONTAL)
        inputSizer.Add(leftSizer,0,wx.ALIGN_TOP|wx.ALL,5)
        inputSizer.Add(midSizer,0,wx.ALIGN_TOP|wx.ALL,5)
        inputSizer.Add(rightSizer,0,wx.ALIGN_TOP|wx.ALL,5)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(folderSizer,0,wx.EXPAND)
        mainSizer.Add(inputSizer,0,wx.ALIGN_CENTRE)
        mainSizer.Layout()
        self.SetSizer(mainSizer)
        
             
    def onSubmitFolder(self,event):
        self.folderSelect()
        
        # Show data
        if self.inputDomain_Time.GetValue() == True:
            self.graph.draw(self.file.X_Value,self.file.Acceleration,'Time')
        else:    
            self.ffTransform()
            self.graph.draw(self.freq, self.amp,'Freq')
    
    def folderSelect(self):
        with wx.FileDialog(self,"Open Impact Echo File",
                           wildcard="LVM files (*.lvm)|*.lvm",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind
            
            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            self.root = os.path.dirname(pathname)
            
            # Displaying file path on screen
            self.folder_Label.SetValue(pathname)
            
            # Reading in data
            self.FILE_NAMES = [file for file in os.listdir(self.root) if
                                file.lower().endswith('.lvm')]
            
            self.files = []
            if self.folder_Label.GetValue() != '':
                i = 0
                for file in self.FILE_NAMES:
                    self.files.append(os.path.join(self.root,file))
                    # Drawing chosen pic to screen
                    if pathname.endswith(file):
                        self.file_index = i
                        self.file_select.SetValue(i+1)
                        path = self.files[i]
                        self.file = pd.read_csv(path, sep='\t', header=22, 
                                 usecols=['X_Value', 'Acceleration'])
                        self.graph.draw(self.file.X_Value,
                                        self.file.Acceleration,'Time')
                        self.file_Label.SetLabel(file)
                        
                    i += 1
            
            self.file_select_Label.SetLabel('File #\n{num} of {max}'.format(
                                 num=self.file_index+1,max=len(self.files)))        
            self.file_Label.SetLabel(self.FILE_NAMES[self.file_index])
            
            self.file_select.SetRange(0,len(self.files)+1)
            self.file_select.SetValue(self.file_index+1)
            
            
    def onSubmitFile(self,event):
        if len(self.files) > 0:
            # Loop value
            if self.file_select.GetValue() == len(self.files):
                self.file_select.SetValue(1)
            elif self.file_select.GetValue() == 0:
                self.file_select.SetValue(self.file_index)
            
            # Iterate through files
            self.file_index = self.file_select.GetValue()-1
            path = self.files[self.file_index]
            self.file = pd.read_csv(path, sep='\t', header=22, 
                     usecols=['X_Value', 'Acceleration'])
            
            if self.domain == 'Time':
                self.graph.draw(self.file.X_Value,self.file.Acceleration,'Time')
            else:
                self.graph.draw(self.file.X_Value,self.file.Acceleration,'Freq')
                
            self.file_select_Label.SetLabel('File #\n{num} of {max}'.format(
                                     num=self.file_index+1,max=len(self.files)))
            self.file_Label.SetLabel(self.FILE_NAMES[self.file_index])
        else:
            # Lock value until file is chosen
            self.file_select.SetValue(1)
    
    def onAnalyze(self,event):
        pass
    
    def onZoom(self,event):
        self.buttonResetZoom.Show()
        
        try:
            x = self.graph.figure.ginput(n=2)
            print(x)
            if x[0]<x[1]:
                self.graph.draw(self.file.X_Value[x[0]:x[1]],self.file.Acceleration)
            else:
                self.graph.draw(self.file.X_Value[x[1]:x[0]],self.file.Acceleration)
        except: 
            pass
        
        self.GetSizer().Layout()
        self.GetParent().Layout()
    
    def onResetZoom(self,event):
        pass
    
    def onUndo(self,event):
        pass
        
    def onChecked(self, event):
        
        cb = event.GetEventObject()
        # Alternating checkboxes
        if cb.GetLabel() == 'Time Domain':
            self.inputDomain_Freq.SetValue(False)
            self.inputDomain_Time.SetValue(True)
            self.domain = 'Time'
            self.graph.draw(self.file.X_Value,self.file.Acceleration,'Time')
        else:
            self.inputDomain_Freq.SetValue(True)
            self.inputDomain_Time.SetValue(False)
            self.domain = 'Freq'
            self.ffTransform()
            self.graph.draw(self.freq, self.amp,'Freq')
        
    def ffTransform(self):
        # calculate signal frequency
        Fs = 1 / self.file.X_Value[1]
        # number of samples
        n = len(self.file)
        # time between samples
        Ts = n / Fs
        
        # frequency range (with both sides)
        freq = np.arange(n) / Ts
        # one side frequency range
        self.freq = np.array(freq[range(int(n / 2))])
        
        # fft computing and normalization of amplitude values
        amp = np.fft.fft(self.file.Acceleration) / n  
        amp = abs(amp[range(int(n / 2))])
        self.amp = np.array(amp / max(amp))

    def domainRange(self):
        
        if self.inputDomain_Time.GetValue() == True:
            return
        
        # Getting bounds range
        min_X = int(self.min_X.GetValue())
        max_X = int(self.max_X.GetValue())
        
        # Getting x values closest to range inclusive
        idx_min = (np.abs(self.freq - min_X)).argmin()
        idx_max = (np.abs(self.freq - max_X)).argmin()
        
        # Index of max amplitude inside frequency range
        maxval_Index = self.amp[idx_min:idx_max].argmax()
        
        # Declaring max values inside frequency range
        self.maxVal_freq = round(self.freq[maxval_Index])
        self.maxVal_amp = round(self.amp[maxval_Index],2)
        
        # Showing max value on screen
        self.peak.SetLabel("Peak amplitude is \n{amp} dB at {freq} Hz"
                          .format(amp=self.maxVal_amp, 
                          freq=self.maxVal_freq))
        
    def onSubmitRange(self,event):
        self.domainRange()
        
   
# if this file is ran (not imported)
if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
    app.ExitMainLoop()
    
    del app
#    raise Exception('exit')
    

