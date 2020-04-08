import pyaudio
import wave
import os
import numpy as np
import time
import math
from tkinter import *

root = Tk()
c = Canvas(root, height = 700, width = 1024)
c.pack()
schet = 0

def readWave(fileName):
    types = {
        1: np.int8,
        2: np.int16,
        4: np.int32
    }
    wav = wave.open(fileName, mode="r")
    (nchannels, sampwidth, framerate, nframes, comptype, compname) = wav.getparams()
    content = wav.readframes(nframes)
    samples = np.fromstring(content, dtype=types[sampwidth])
    return dataSum(nchannels, nframes, samples)   

#count the summ of data from all channels
def dataSum(nchannels, nframes, samples):   
    data = []
    for frame in range(nframes):
        data.append(0)
        for channel in range(nchannels):
            data[frame] += samples[frame * nchannels + channel]
            
    return data

plotNum = 0
def plot(data, w, h):
    global plotNum
    plotNum += 1
    DPI = 72
    plt.figure(1, figsize = (float(w)/DPI, float(h)/DPI), dpi = DPI)

    axes = plt.subplot(2, 1, plotNum, axisbg="k")
    axes.plot(data, "g")
    plt.grid(True, color="w")
    plt.savefig("wave", dpi=DPI)
    

def getPeaks(data, framerate):
    data_f = np.fft.rfft(data)
    data_f[0]=0;
    data_f_abs = np.absolute(data_f)
    
    plotNum = 0    
    
    duration = len(data) / framerate
    maxIndex = np.argmax(data_f_abs)
    maxFreq = maxIndex / duration     
    
    PEAKS = []
    maxPeaks = 4 #How many peaks (in descending order from highest)
    minAmplitude = 0.1
    toZero = 0 #How many samples to annihilate from the right to the left
    maxAmplitude = np.max(data_f_abs)
    
    if maxAmplitude < 2000000:
        return 0
    
    #print(maxAmplitude)
    for i in range(maxPeaks):
        peakIndex = np.argmax(data_f_abs)
        peakValue = data_f_abs[peakIndex]
        
        if(peakValue < minAmplitude * maxAmplitude):
            break;
        
        PEAKS.append(peakIndex / duration)
        
        # delete from the right
        peakIndex1= peakIndex
        while (data_f_abs[peakIndex1 +1] <= data_f_abs[peakIndex1])and(peakIndex1 < len(data_f_abs)):
            data_f_abs[peakIndex1]=0            
            peakIndex1 += 1
        # delete from the left
        peakIndex1= peakIndex -1
        while (data_f_abs[peakIndex1 -1] <= data_f_abs[peakIndex1])and(peakIndex1 >= 0):
            data_f_abs[peakIndex1]=0            
            peakIndex1 -= 1
            
    PEAKSordered=[]
    for k in range(4):
        PEAKSordered.append(PEAKS[np.argmax(PEAKS)])
        PEAKS[np.argmax(PEAKS)] = 0
    Fbass = PEAKSordered[len(PEAKSordered)-2]-PEAKSordered[len(PEAKSordered)-1]
    if Fbass == 0:
        maxFreq = maxIndex / duration
    elif (round(Fbass) ==172) and (maxIndex / duration < 343):
        maxFreq = float(165)
    else:
        maxFreq = Fbass
            
    #plot(data_f_abs, 1024, 600)
    
    return maxFreq

def getNoteNum(freq):
    return 12 * math.log(freq / 27.5 , 2)

def getNoteName(freq):
    if freq == 0:
        return ''
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    noteNum = round(getNoteNum(freq))
    return notes[(noteNum - 3) % 12] + str( (noteNum - 3) // 12 + 1)

def play():
    schet = 1
    CHUNK = 4096 # Enough to define sounds starting from bass and above
    RATE = 44100
    CHANNELS = 2
    RECORD_SECONDS = 300    
    p = pyaudio.PyAudio()
    stream = p.open(format = pyaudio.paInt16,
                    channels = CHANNELS,
                    rate = RATE,
                    input = True,
                    frames_per_buffer = CHUNK)
    
    frames = []
    if schet == 1:
        c.create_rectangle(130, 100, 930, 300, fill = 'white', outline = 'light gray', width = 3, tag = "okno")
    c.update()
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        c.delete('text')
        content = stream.read(CHUNK)
        samples = np.fromstring(content, dtype=np.int16)
        data = dataSum(CHANNELS, CHUNK, samples)
        freq = getPeaks(data, 44100)
        c.create_text(540, 170, text=getNoteName(freq), font = "Arial 100", fill="darkred", tag= "text")
        c.update()
    stream.stop_stream()
    stream.close()
    p.terminate()
    c.create_text(540, 250, text='Time is up!', font = "Arial 24", fill="black", tag= "text")
    c.update()
    time.sleep(3)
    c.delete('okno', 'text')
    

but = Button(root, text='Play',width=15,height=2,fg='black',font='System 20', bg = 'light grey', command = play)
but.place(x=570,y=400)
root.mainloop()