# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import glob
import re
import pickle
import csv
from Modules_basic import get_freezing_rate as frate
from Modules_basic import detect_cs
from natsort import natsorted
import tkinter
from tkinter import filedialog, messagebox
import yaml
import pandas as pd
import codecs
import chardet


def Analyze():
    print("Running analysis...")

    if os.path.exists(cs_start_frames_path):
        with open(cs_start_frames_path, 'rb') as f:
            cs_start_frames = pickle.load(f)
    else:
        #session数 x cs数の行列が返ってくる
        cs_start_frames = detect_cs.detectCS(box1_videos, num_cs)
        with open(cs_start_frames_path, 'wb') as f:
            pickle.dump(cs_start_frames, f)

    #session数,cs数が合っているか確認する
    if cs_start_frames == 0:
        return 0
    elif len(cs_start_frames) != num_sessions:
        print("Example videos number mismatch!")
        return 0

    #with open('EarlyWeaning/191001Ext-CSstarts.pkl', 'wb') as f:
    #    pickle.dump(cs_start_frames, f)

    rate_container = np.empty((num_mice, num_cs+1)) #base用の+1


    for i in range(num_mice):
        path = csv_files[i]
        print("Loading: " + path)
        #(freezing_frames_dirで渡したパスにフレームごとの0/1も格納される)
        rate_container = frate.getFreezingRate(fps, bodypartsToUse, path, num_cs, cs_start_frames[session_mice[i]-1], os.path.splitext(os.path.basename(path))[0], freezing_frames_dir, distance_dir, freezing_photometry_dir)
        #pickleに書き込み
        # with open(analyzed_data_dir+date+"_Mouse"+str(mice[i])+"_"+groups[mice_in_groups[i]]+".pkl", 'wb') as f:
        """
        with open(analyzed_data_dir+date+"_"+os.path.splitext(os.path.split(path)[1])[0]+".pkl", 'wb') as f:
            pickle.dump(rate_container, f)
        """
        #csvに書き込み
        # with open(analyzed_data_dir+"csv/"+date+"_Mouse"+str(mice[i])+"_"+groups[mice_in_groups[i]]+".csv", 'w') as f:
        with open(analyzed_data_dir+os.path.splitext(os.path.split(path)[1])[0]+".csv", 'w') as f:
            writer = csv.writer(f)
            writer.writerow(rate_container)

    """
    for i in range(num_mice):
        plt.plot(np.arange(num_cs)+1, data_container[i])

    plt.show()
    """
    return 0

def getWorkingDir():
    root = tkinter.Tk()
    root.withdraw()
    fTyp = [("", "*")]
    tkinter.messagebox.showinfo('getWorkingDir()', 'Select the directory where videos and h5 files exist.')

    return tkinter.filedialog.askdirectory(initialdir = data_root)

def getBox1Video(i):
    root = tkinter.Tk()
    root.withdraw()
    fTyp = [("", "*.avi")]
    tkinter.messagebox.showinfo('getBox1Video', "Select a representative video for session " + str(i+1))

    return tkinter.filedialog.askopenfilename(filetypes=fTyp, initialdir=working_dir)

def getNumCS():
    types = ['FC (5US-CS)', 'Ext (40CS)', 'Test (6CS)']
    root = tkinter.Tk()

    var = tkinter.IntVar(master=root, value=1)

    l = tkinter.Label(master=root, bg="Lightblue", width="10", textvariable=var)
    l.pack()

    for i in range(3):
        r = tkinter.Radiobutton(master=root, text=types[i], value=i+1, var=var)
        r.pack()

    # ここは書いてる途中

    root.mainloop()

    return value

def readBodyparts():
    with codecs.open(csv_files[0], 'r', 'utf-8', 'ignore') as file:
        df = pd.read_table(file, delimiter=",")
        print(df)



with open('config.yaml', 'r') as yml:
    config = yaml.load(yml, Loader=yaml.FullLoader)

data_root = config['paths']['data_root']
working_dir = getWorkingDir() + "/"
analyzed_data_dir = working_dir + "AnalyzedData/"
cs_start_frames_path = analyzed_data_dir + "cs_start_frames.pkl"
freezing_frames_dir = analyzed_data_dir + "freezingFrames/"
distance_dir = analyzed_data_dir + "distance/"
each_frames_dir = analyzed_data_dir + "eachFrames/"

if not os.path.exists(analyzed_data_dir):
    os.makedirs(freezing_frames_dir)
    os.makedirs(distance_dir)
    os.makedirs(each_frames_dir)

csv_files = natsorted(glob.glob(working_dir + '/*.csv'))
num_mice = len(csv_files)
if num_mice == 0:
    print("There is no h5 file. You may have chosen a wrong directory.")
    sys.exit()
print("Analyzing " + str(num_mice) + " mice.")

num_cs = config['num_cs']
num_sessions = config['num_sessions']

bodyparts_in_DLC = readBodyparts()
print("How many bodyparts to use?")
bodypartsToUse = int(input())

# print("How many bodyparts in DLC?")
# num_bodyparts = int(input())

print("FPS, 15 or 20?")
fps = int(input())

box1_videos = np.array([])
for i in range(num_sessions):
    box1_video = getBox1Video(i)
    box1_videos = np.append(box1_videos, box1_video)

print(box1_videos)

# print("Enter in which session each mouse is included. (1,2,...)")
tkinter.messagebox.showinfo('main', "Enter in which session each mouse is included. (1,2,...)")
session_mice = np.array([], dtype=np.int64)
for csv in csv_files:
    print(os.path.split(csv)[1])
    session_mice = np.append(session_mice, int(input()))
print(session_mice)

Analyze()
