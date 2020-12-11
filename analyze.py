# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import glob
import re
import pickle
import csv
from natsort import natsorted
import tkinter
from tkinter import filedialog, messagebox
import yaml
from Modules_basic.get_freezing_rate import GetFreezingRate
from Modules_basic.detect_cs import GetCS_Starts


def Analyze():
    if os.path.exists(cs_start_frames_path):
        with open(cs_start_frames_path, 'rb') as f:
            cs_start_frames = pickle.load(f)
    else:
        # Returns a matrix of session_num x cs_num
        csTimingGetter = GetCS_Starts(session_representative_videos, num_cs)
        cs_start_frames = csTimingGetter()
        with open(cs_start_frames_path, 'wb') as f:
            pickle.dump(cs_start_frames, f)

    # Confirms if session_num and cs_num are correct
    if cs_start_frames == 0:
        return 0
    elif len(cs_start_frames) != num_sessions:
        print("Example videos number mismatch!")
        return 0


    rate_container = np.empty((num_mice, num_cs+1)) # +1 for baseline


    for i in range(num_mice):
        path = csv_files[i]
        print("Loading: " + path)
        #(freezing_frames_dirで渡したパスにフレームごとの0/1も格納される)
        FreezingRateGetter = GetFreezingRate(fps, cs_length, bodyparts2use, path, num_cs, cs_start_frames[session_mice[i]-1], \
            os.path.splitext(os.path.basename(path))[0])
        rate_container = FreezingRateGetter(freezing_frames_dir, distance_dir, each_frames_dir)

        with open(analyzed_data_dir + os.path.splitext(os.path.split(path)[1])[0] + ".csv", 'w') as f:
            writer = csv.writer(f)
            writer.writerow(rate_container)

    return 0

def getWorkingDir():
    root = tkinter.Tk()
    root.withdraw()
    fTyp = [("", "*")]
    tkinter.messagebox.showinfo('getWorkingDir()', 'Select the directory where videos and csv files exist.')

    return tkinter.filedialog.askdirectory(initialdir = data_root)

def getRepresentativeVideo(i):
    root = tkinter.Tk()
    root.withdraw()
    fTyp = [("", "*.avi")]
    tkinter.messagebox.showinfo("Select a representative video for session " + str(i+1), \
        "Each session is considered to have the same timing of CS for all mice in that session. If not, contact @nobel_sean")

    return tkinter.filedialog.askopenfilename(filetypes=fTyp, initialdir=working_dir)


class BodyPartsReader:
    def __init__(self, first_csv_file):
        self.path = first_csv_file

    def csv_read_row(self):
        with open(self.path) as f:
            reader = csv.reader(f)
            for row in reader:
                if reader.line_num == 2: return row
        return 0

    def __call__(self):
        l = self.csv_read_row()

        l = l[1:]
        l = sorted(set(l), key=l.index)

        return l


class GetBodypartsToUse:
    def __init__(self, bp_array):
        self.bodyparts = bp_array
        self.bodyparts2use = []

    def bodyparts_to_use(self):
        for i in range(len(self.bodyparts)):
            inp = input("Use " + bodyparts[i] + "? [y/n] >> ") == 'y'

            if inp:
                self.bodyparts2use.append(self.bodyparts[i])
                self.bodyparts[i] = 1
            else:
                self.bodyparts[i] = 0

        print("Using " + str(self.bodyparts2use))

    def __call__(self):
        self.bodyparts_to_use()

        return self.bodyparts



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
    print("There is no csv file. You may have chosen a wrong directory.")
    sys.exit()
print("Analyzing " + str(num_mice) + " mice.")

num_cs = config['num_cs']
num_sessions = config['sessions']
fps = config['video_fps']
cs_length = config['cs_length']

bpReader = BodyPartsReader(csv_files[0])
bodyparts = bpReader()
print(str(len(bodyparts)) + " boodyparts were analyzed in DeepLabCut.")

bp2useReader = GetBodypartsToUse(bodyparts)
bodyparts2use = bp2useReader()
print(bodyparts2use)

session_representative_videos = np.array([])
for i in range(num_sessions):
    session_representative_video = getRepresentativeVideo(i)
    session_representative_videos = np.append(session_representative_videos, session_representative_video)

print("Session representative videos >> ")
print(session_representative_videos)

tkinter.messagebox.showinfo('main', "Enter in which session each mouse is included. (1,2,...)")
session_mice = np.array([], dtype=np.int64)
for c in csv_files:
    print(os.path.split(c)[1])
    session_mice = np.append(session_mice, int(input()))

print("Running analysis...")
_ = Analyze()
