# -*- coding: utf-8 -*-
import numpy as np
import cv2
import pickle
from tqdm import tqdm
import glob
from natsort import natsorted
import os
import tkinter
from tkinter import filedialog, messagebox
import yaml

def CreateVideo():
    # mouse_id = mouse_and_session[0]
    # session = mouse_and_session[1]

    #input_path = working_dir+"videos/Mouse"+str(mouse_id)+"_labeled.mp4"
    output_path = create_dir + "/" + os.path.split(video_path)[1]
    # output_path = working_dir+"freezingFrames/videos/Mouse"+str(mouse_id)+"-withFreezing.avi"
    data_path = work_dir + "/AnalyzedData/freezingFrames/" + os.path.splitext(os.path.basename(h5file))[0] + ".pkl"
    distance_path = work_dir + "/AnalyzedData/distance/" + os.path.splitext(os.path.basename(h5file))[0] + ".pkl"
    cs_start_path = work_dir + "/AnalyzedData/cs_start_frames.pkl"

    #マウス移動距離データ読み込み
    with open(distance_path, 'rb') as f:
        distance = pickle.load(f)

    #CSが始まるフレームのデータ読み込み
    with open(cs_start_path, 'rb') as f:
        cs_starts = pickle.load(f)[session-1]

    video = cv2.VideoCapture(video_path)

    frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if not video.isOpened():
        print("Video not read")

    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc('M','J','P','G'), fps, (width, height))

    f = open(data_path, "rb")
    freezing_time = pickle.load(f)

    #CS中のフレームのみ書き出し
    font = cv2.FONT_HERSHEY_SIMPLEX
    x = 0
    cs = -1 # CSカウント用
    accumFreezing = np.zeros(num_cs)
    for i in tqdm(range(frames)):
        ret, frame = video.read()

        if i in cs_starts:
            x = fps * 20 + 15
            cs += 1
        x -= 1

        if ret:
            if x > 0:
                #cv2.putText(frame, "movement:"+str(int(distance[i])), (365,470), font, 1, (255,255,255), 2, cv2.LINE_AA)
                for j in range(num_cs):
                    if j % 2 == 0:
                        cv2.putText(frame, str(round(accumFreezing[j]*100.0/(20.0*fps), 1)) + "%", (10, (j+2)*10), font, 0.7, (0,0,255), 1, cv2.LINE_AA)
                    else:
                        cv2.putText(frame, str(round(accumFreezing[j]*100.0/(20.0*fps), 1)) + "%", (78, ((j+1)*10)), font, 0.7, (0,0,255), 1, cv2.LINE_AA)
                frame = cv2.rectangle(frame, (620,470-int(distance[i])), (630,470), (0,0,255), -1)
                if freezing_time[i] == 1:
                    frame = cv2.putText(frame, "Freezing.", (200, 40), font, 1.5, (0,0,255), 4, cv2.LINE_AA)
                    #累積FreezingRate表示
                    if x > 15:
                        accumFreezing[cs] += 1
                    out.write(frame)
                else:
                    out.write(frame)
            else:
                pass
        else:
            break

    video.release()
    out.release()

    cv2.destroyAllWindows()

    return 0

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
data_root = "D:/"
video_path, work_dir = getVideoToCreate()
create_dir = work_dir + "/CreatedVideos"

if not os.path.exists(create_dir):
    os.makedirs(create_dir)

h5file = getH5File()

print("Which session is that video in ? (1,2,...)")
session = int(input())

_ = CreateVideo()
