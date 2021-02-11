# -*- coding: utf-8 -*-
import os
import numpy as np
import h5py
import sys
from tqdm import tqdm
import pickle
import glob
import natsort
import cv2
import math
import matplotlib.pyplot as plt
import csv
import tkinter
from tkinter import filedialog, messagebox
from Modules.get_pixel import mouseParam
from Modules.read_h5file import Read_h5
from Modules.edge_center_ratio import EdgeCenterRatio
import yaml


def body_center_video():
    if not video.isOpened():
        print("Video not read.")
        return 0
    if not frames == int(video.get(cv2.CAP_PROP_FRAME_COUNT)):
        print("Video and h5 file have different frames.")
        return 0

    # width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    # height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # fps = video.get(cv2.CAP_PROP_FPS)

    out = cv2.VideoWriter(output_video_name, cv2.VideoWriter_fourcc('M','J','P','G'), fps, (width, height))

    # accum_distance = 0
    iForSection = 0

    print("Writing video...")
    for i in tqdm(range(frames)):
    # for i in tqdm(range(5000)):
        ret, frame = video.read()

        # accum_distance += distance_travelled[i]

        if ret:
            # 点プロット
            frame = cv2.circle(frame, (int(coordinates[i][0]), int(coordinates[i][1])), 3, (0,255,255), -1)
            # frame = cv2.circle(frame, (int(coord_snout[i][0]), int(coord_snout[i][1])), 2, (255,0,0), -1)
            # frame = cv2.circle(frame, (int(coord_rightear[i][0]), int(coord_rightear[i][1])), 2, (0,255,0), -1)
            # frame = cv2.circle(frame, (int(coord_leftear[i][0]), int(coord_leftear[i][1])), 2, (0,0,255), -1)
            # 線プロット
            if i > 0:
                for j in range(1,i):
                    frame = cv2.line(frame, (int(coordinates[j-1][0]), int(coordinates[j-1][1])), (int(coordinates[j][0]), int(coordinates[j][1])), (0,120,120), 1)
            # cv2.putText(frame, str(accum_distance), (10,10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 1, cv2.LINE_AA)
            # cv2.putText(frame, str(round(coord_snout[i][0], 1)) + " " + str(round(coord_snout[i][1], 1)), (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 1, cv2.LINE_AA)
            # cv2.putText(frame, str(round(coord_rightear[i][0], 1)) + " " + str(round(coord_rightear[i][1], 1)), (10,50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 1, cv2.LINE_AA)
            # cv2.putText(frame, str(round(coord_leftear[i][0], 1)) + " " + str(round(coord_leftear[i][1], 1)), (10,70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 1, cv2.LINE_AA)
            # cv2.putText(frame, str(round(prob[i][0], 1)) + " " + str(round(prob[i][1], 1)) + " " + str(round(prob[i][2], 1)), (10,90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 1, cv2.LINE_AA)
            if this_first_cs_start_frame - fps*60 <= i < this_first_cs_start_frame and ec_ratio_isEnabled:
                # print(section[iForSection])

                if section[iForSection] == 1:
                    frame = cv2.rectangle(frame, (int(left_up_edge[0]),int(left_up_edge[1])), (int(x_border1),int(y_border1)), (0,100,0), 3)
                elif section[iForSection] == 2:
                    frame = cv2.rectangle(frame, (int(x_border1),int(left_up_edge[1])), (int(x_border2),int(y_border1)), (0,100,0), 3)
                elif section[iForSection] == 3:
                    frame = cv2.rectangle(frame, (int(x_border2),int(left_up_edge[1])), (int(right_down_edge[0]),int(y_border1)), (0,100,0), 3)
                elif section[iForSection] == 4:
                    frame = cv2.rectangle(frame, (int(left_up_edge[0]),int(y_border1)), (int(x_border1),int(y_border2)), (0,100,0), 3)
                elif section[iForSection] == 5:
                    frame = cv2.rectangle(frame, (int(x_border1),int(y_border1)), (int(x_border2),int(y_border2)), (0,100,0), 3)
                elif section[iForSection] == 6:
                    frame = cv2.rectangle(frame, (int(x_border2),int(y_border1)), (int(right_down_edge[0]),int(y_border2)), (0,100,0), 3)
                elif section[iForSection] == 7:
                    frame = cv2.rectangle(frame, (int(left_up_edge[0]),int(y_border2)), (int(x_border1),int(right_down_edge[1])), (0,100,0), 3)
                elif section[iForSection] == 8:
                    frame = cv2.rectangle(frame, (int(x_border1),int(y_border2)), (int(x_border2),int(right_down_edge[1])), (0,100,0), 3)
                elif section[iForSection] == 9:
                    frame = cv2.rectangle(frame, (int(x_border2),int(y_border2)), (int(right_down_edge[0]),int(right_down_edge[1])), (0,100,0), 3)

                iForSection += 1


        out.write(frame)

    video.release()
    out.release()
    cv2.destroyAllWindows()

    return 0


def draw_graph():
    x = np.arange(frames) / fps

    plt.plot(x, accum_distance_travelled)
    plt.show()

    return 0


def get_cs_start_frames():
    with open(cs_start_frames_path, 'rb') as f:
        cs_start_frames = pickle.load(f)

    return cs_start_frames


def get_sensitivity():
    accum_distance_travelled = 0

    for cs in this_cs_start_frames:
        for i in range(cs, cs + fps*2):
            this_distance = math.sqrt(pow(coordinates[i+1][0]-coordinates[i][0], 2) + pow(coordinates[i+1][1]-coordinates[i][1], 2))
            accum_distance_travelled += this_distance

    return accum_distance_travelled


def get_activity():
    accum_distance_travelled = 0

    for i in range(this_first_cs_start_frame - fps*60, this_first_cs_start_frame):
        this_distance = math.sqrt(pow(coordinates[i+1][0]-coordinates[i][0], 2) + pow(coordinates[i+1][1]-coordinates[i][1], 2))
        accum_distance_travelled += this_distance

    return accum_distance_travelled


def coordinates_correction(coord):
    for i in range(len(coord) - 3):
        # 次のフレームとの距離があまりにも離れていたら、次のフレームを今のフレームと2フレーム先との中点にする
        dist_1_after = math.sqrt(pow(coord[i+1][0]-coord[i][0], 2) + pow(coord[i+1][1]-coord[i][1], 2))
        if dist_1_after > 100:
            # 次のフレームを今のフレームと2フレーム先との中点にする
            # coord[i+1][0] = (coord[i][0] + coord[i+2][0]) / 2
            # coord[i+1][1] = (coord[i][1] + coord[i+2][1]) / 2

            dist_2_after = math.sqrt(pow(coord[i+2][0]-coord[i][0], 2) + pow(coord[i+2][1]-coord[i][1], 2))
            dist_3_after = math.sqrt(pow(coord[i+3][0]-coord[i][0], 2) + pow(coord[i+3][1]-coord[i][1], 2))
            if dist_2_after * 5 < dist_1_after:
                coord[i+1][0] = (coord[i][0] + coord[i+2][0]) / 2
                coord[i+1][1] = (coord[i][1] + coord[i+2][1]) / 2
            elif dist_3_after * 5 < dist_1_after:
                coord[i+1][0] = (coord[i][0] + coord[i+3][0]) / 2
                coord[i+1][1] = (coord[i][1] + coord[i+3][1]) / 2

    return coord


def px_to_cm():
    return 0

def getWorkingDir():
    root = tkinter.Tk()
    root.withdraw()
    fTyp = [("", "*.avi")]
    # tkinter.messagebox.showinfo('videos', 'Select video for the h5file.')

    return tkinter.filedialog.askdirectory(initialdir=data_root)

def getVideoPath():
    root = tkinter.Tk()
    root.withdraw()
    fTyp = [("", "*.avi")]

    return tkinter.filedialog.askopenfilename(filetypes=fTyp, initialdir=working_dir)



print("Notice: this program only works with DLC data with 3 bodyparts or less.")

with open('config.yaml', 'r') as yml:
    config = yaml.load(yml, Loader=yaml.FullLoader)


data_root = config['paths']['data_root']
working_dir = getWorkingDir() + "/"
analyzed_dir = working_dir + config['paths']['analyzed_data']
ec_ratio_dir = analyzed_dir + config['paths']['ec_ratio']
cs_start_frames_path = analyzed_dir + config['paths']['cs_start_frames']

ec_ratio_isEnabled = config['ec_ratio']

if not os.path.exists(ec_ratio_dir):
    os.makedirs(ec_ratio_dir)

movement_measure_time = config['movement_measure_time']

h5files = natsort.natsorted(glob.glob(working_dir + "*.h5"))
print("Analyzing " + str(len(h5files)) + " mice.")
num_mice = len(h5files)


mice_in_sessions = np.array([], dtype=np.int64)
videos = np.array([], dtype=np.str)
print("Enter in which session each mouse is included.")
for h5file in h5files:
    print(os.path.split(h5file)[1])
    mice_in_sessions = np.append(mice_in_sessions, int(input()))

print("Select the video for each h5 file.")
for h5file in h5files:
    print(os.path.split(h5file)[1])
    videos = np.append(videos, getVideoPath())

print(videos)


sensitivities = []
activities = []


cs_start_frames = get_cs_start_frames()
print("Sessions: " + str(len(cs_start_frames)))
print(cs_start_frames)


# Initialize EC ratio calculator
EC_ratio = EdgeCenterRatio(h5files, videos, movement_measure_time)

for i in range(len(h5files)):
    video = cv2.VideoCapture(videos[i])
    fps = int(video.get(cv2.CAP_PROP_FPS))
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    output_video_name = working_dir + "AnalyzedData/" + os.path.splitext(os.path.basename(h5files[i]))[0] + ".avi"

    H5Reader = Read_h5(h5files[i])
    frames, coordinates, bodyparts = H5Reader()

    if coordinates == 0: sys.exit()

    # coordinatesが一瞬だけ飛んだりするのを補正する
    # coordinates = coordinates_correction(coordinates)

    this_cs_start_frames = cs_start_frames[mice_in_sessions[i]-1]
    this_first_cs_start_frame = this_cs_start_frames[0]

    sensitivity = get_sensitivity()
    sensitivities.append(sensitivity)

    activity = get_activity()
    activities.append(activity)

    if ec_ratio_isEnabled: _ = EC_ratio(i, this_first_cs_start_frame, fps, coordinates, ec_ratio_dir)

    if i == -1: # <-書き直す
        _ = body_center_video()


print(sensitivities)
print(activities)

with open(working_dir+"AnalyzedData/activity&sensitivity.csv", 'w') as f:
    writer = csv.writer(f)
    writer.writerow(sensitivities)
    writer.writerow(activities)
