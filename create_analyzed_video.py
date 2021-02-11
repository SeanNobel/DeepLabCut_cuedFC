# -*- coding: utf-8 -*-
import numpy as np
import cv2
import pickle
from tqdm import tqdm
import glob
from natsort import natsorted
import os
import sys
import tkinter
from tkinter import filedialog, messagebox
import yaml

class CreateVideo:
    def __init__(self, output_path, data_path, distance_path, cs_start_path, session, video_path, fps, num_cs, afterFrames, cs_length):
        self.output_path = output_path
        self.data_path = data_path
        self.distance_path = distance_path
        self.cs_start_path = cs_start_path
        self.session = session
        self.video_path = video_path
        self.fps = fps
        self.num_cs = num_cs

        #load distance data of mice movement
        with open(self.distance_path, 'rb') as f:
            self.distance = pickle.load(f)

        #load data of cs starting frames
        with open(self.cs_start_path, 'rb') as f:
            self.cs_starts = pickle.load(f)[self.session - 1]

        self.video = cv2.VideoCapture(self.video_path)

        self.frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if not self.video.isOpened():
            print("Video not read")
            sys.exit()

        self.out = cv2.VideoWriter(self.output_path, cv2.VideoWriter_fourcc('M','J','P','G'), self.fps, (self.width, self.height))

        with open(self.data_path, 'rb') as f:
            self.freezing_time = pickle.load(f)

    def create(self):
        font = cv2.FONT_HERSHEY_SIMPLEX
        self.x = 0
        self.cs = -1 # for counting CS number
        self.accumFreezing = np.zeros(self.num_cs)

        for i in tqdm(range(self.frames)):
            ret, frame = self.video.read()

            if i in self.cs_starts:
                self.x = self.fps * 20 + afterFrames
                self.cs += 1
            self.x -= 1

            if ret:
                if self.x > 0:
                    for j in range(self.num_cs):
                        if j % 2 == 0:
                            cv2.putText(frame, str(round(self.accumFreezing[j] * 100 / (cs_length * self.fps), 1)) + "%", (10, (j+2) * 10), font, 0.7, (0,0,255), 1, cv2.LINE_AA)
                        else:
                            cv2.putText(frame, str(round(self.accumFreezing[j] * 100 / (cs_length * self.fps), 1)) + "%", (78, (j+1) * 10), font, 0.7, (0,0,255), 1, cv2.LINE_AA)
                    # frame = cv2.rectangle(frame, (620,470-int(distance[i])), (630,470), (0,0,255), -1)
                    if self.freezing_time[i] == 1:
                        frame = cv2.putText(frame, "Freezing.", (200, 40), font, 1.5, (0,0,255), 4, cv2.LINE_AA)
                        #累積FreezingRate表示
                        if self.x > afterFrames:
                            self.accumFreezing[self.cs] += 1
                        self.out.write(frame)
                    else:
                        self.out.write(frame)
            else:
                break

        self.video.release()
        self.out.release()

        cv2.destroyAllWindows()

        return 0

    def __call__(self):
        _ = self.create() # Writes video only during CS and previous x seconds


def getVideoToCreate():
    root = tkinter.Tk()
    root.withdraw()
    fTyp = [("", "*.avi")]

    videopath = tkinter.filedialog.askopenfilename(filetypes=fTyp, initialdir=data_root)
    dirpath = os.path.split(videopath)[0]

    return videopath, dirpath

def getH5File():
    root = tkinter.Tk()
    root.withdraw()
    fTyp = [("", "*.h5")]

    tkinter.messagebox.showinfo('Create analyzed videos', 'Select h5 file for the video.')
    h5filepath = tkinter.filedialog.askopenfilename(filetypes=fTyp, initialdir=work_dir)

    return h5filepath



with open('config.yaml', 'r') as yml:
    config = yaml.load(yml, Loader=yaml.FullLoader)

fps = config['video_fps']
num_cs = config['num_cs']
afterFrames = config['afterFrames']
cs_length = config['cs_length']

data_root = config['paths']['data_root']
video_path, work_dir = getVideoToCreate()
create_dir = work_dir + config['paths']['created_video']

if not os.path.exists(create_dir):
    os.makedirs(create_dir)

isMP4 = input("Are you creating video from mp4? [y/n] >> ") == 'y'
if isMP4:
    print("Creating video from mp4.")
else:
    print("Creating video from avi.")

h5file = getH5File()

if isMP4:
    output_path = create_dir + "/" + os.path.splitext(os.path.split(video_path)[1])[0] + ".avi"
else:
    output_path = create_dir + "/" + os.path.split(video_path)[1]
data_path = work_dir + "/AnalyzedData/freezingFrames/" + os.path.splitext(os.path.basename(h5file))[0] + ".pkl"
distance_path = work_dir + "/AnalyzedData/distance/" + os.path.splitext(os.path.basename(h5file))[0] + ".pkl"
cs_start_path = work_dir + "/AnalyzedData/cs_start_frames.pkl"

print("Which session is that video in ? (1,2,...)")
session = int(input())

videoCreator = CreateVideo(output_path, data_path, distance_path, cs_start_path, session, video_path, fps, num_cs, afterFrames, cs_length)

videoCreator()
