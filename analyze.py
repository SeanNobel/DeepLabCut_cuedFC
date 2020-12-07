# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import glob
import re
import pickle
import csv
import get_freezing_rate as frate
import detect_cs
from natsort import natsorted
import tkinter
from tkinter import filedialog, messagebox

def get_mice_in_groups(h5files, num_mice, groups):
    mice_in_groups = np.empty(num_mice, dtype=int)

    for i in range(num_mice):
        if(groups[0] in h5files[i]):
            mice_in_groups[i] = 0
        elif(groups[1] in h5files[i]):
            mice_in_groups[i] = 1
        elif(groups[2] in h5files[i]):
            mice_in_groups[i] = 2
        else:
            mice_in_groups[i] = 3

    return mice_in_groups

def Analyze():
    print("Running analysis...")
    # num_sessions = 2
    # num_cs = 6
    #Mouse1,2,3...がどのセッションに含まれるか（欠けてしまった個体はスキップ
    # session_mice_correspondence = np.array([1,1,1,1,2,2,2,2])
    # groups = ["IS_male", "RE_male", "IS_female", "RE_female"]
    #Mouse1,2,3...がどのgroupsか
    # mice_in_groups = np.array([2,2,2,3,2,2,2,3])

    # h5_files = natsorted(glob.glob(file_dir + '*.h5'))
    # num_mice = len(h5_files)
    #一部のマウスのデータが欠けてしまった場合に編集
    # mice = np.arange(num_mice) + 1

    # _mice_in_groups = get_mice_in_groups(h5_files, num_mice, groups)

    # print(mice_in_groups)
    # print(_mice_in_groups)

    if os.path.exists(cs_start_frames_data):
        with open(cs_start_frames_data, 'rb') as f:
            cs_start_frames = pickle.load(f)
    else:
        #session数 x cs数の行列が返ってくる
        cs_start_frames = detect_cs.detectCS(box1_videos, num_cs)
        with open(cs_start_frames_data, 'wb') as f:
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
        path = h5_files[i]
        print("Loading: " + path)
        #(freezing_frames_dirで渡したパスにフレームごとの0/1も格納される)
        rate_container = frate.getFreezingRate(fps, bodypartsToUse, path, num_cs, cs_start_frames[session_mice[i]-1], os.path.splitext(os.path.basename(path))[0], freezing_frames_dir, distance_dir, freezing_photometry_dir)
        #pickleに書き込み
        # with open(freezing_rate_dir+date+"_Mouse"+str(mice[i])+"_"+groups[mice_in_groups[i]]+".pkl", 'wb') as f:
        """
        with open(freezing_rate_dir+date+"_"+os.path.splitext(os.path.split(path)[1])[0]+".pkl", 'wb') as f:
            pickle.dump(rate_container, f)
        """
        #csvに書き込み
        # with open(freezing_rate_dir+"csv/"+date+"_Mouse"+str(mice[i])+"_"+groups[mice_in_groups[i]]+".csv", 'w') as f:
        with open(freezing_rate_dir+os.path.splitext(os.path.split(path)[1])[0]+".csv", 'w') as f:
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
    # tkinter.messagebox.showinfo('analyze', 'Select directory.')

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


if __name__ == '__main__':
    # fps = 20
    data_root = "D:/"
    working_dir = getWorkingDir() + "/"
    # date = "200824Ret"
    # file_dir = working_dir + "h5files/"
    # box1_videos_dir = working_dir + "box1_videos/"
    freezing_rate_dir = working_dir + "AnalyzedData/"
    cs_start_frames_data = freezing_rate_dir + "cs_start_frames.pkl"
    freezing_frames_dir = freezing_rate_dir + "freezingFrames/"
    distance_dir = freezing_rate_dir + "distance/"
    freezing_photometry_dir = freezing_rate_dir + "freezingForPhotometry/"

    if not os.path.exists(freezing_rate_dir):
        os.makedirs(freezing_frames_dir)
        os.makedirs(distance_dir)
        os.makedirs(freezing_photometry_dir)

    h5_files = natsorted(glob.glob(working_dir + '/*.h5'))
    print("Analyzing " + str(len(h5_files)) + " mice.")
    num_mice = len(h5_files)

    print("How many US-CS or CS?")
    num_cs = int(input())

    print("How many sessions?")
    num_sessions = int(input())

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
    for h5file in h5_files:
        print(os.path.split(h5file)[1])
        session_mice = np.append(session_mice, int(input()))
    print(session_mice)

    Analyze()
