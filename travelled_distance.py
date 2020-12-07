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

#h5ファイルを読み、フレーム数と各フレームでの鼻・両耳の中心の座標を返す
def read_h5_3points(filename):
    with h5py.File(filename, 'r') as f:
        length = f['df_with_missing/table'].shape[0]

        dataset = np.empty((length, 2)) #鼻,両耳の中心を格納する
        # dataset_snout = np.empty((length, 2))
        # dataset_rightear = np.empty((length, 2))
        # dataset_leftear = np.empty((length, 2))
        probabilities = np.empty((length, 2))

        probability_low = 0 # posture detectionが悪くて前のフレームを使うのが続いたら警告を出す

        for i in tqdm(range(length)):
            x = f['df_with_missing/table'][i][1]

            # snout_rightear_dist = math.sqrt(pow(x[0]-x[3], 2) + pow(x[1]-x[4], 2))
            # snout_leftear_dist = math.sqrt(pow(x[0]-x[6], 2) + pow(x[1]-x[7], 2))
            ears_dist = math.sqrt(pow(x[3]-x[6], 2) + pow(x[4]-x[7], 2))

            # 一つの距離が他の二つよりも３倍以上離れていたら
            """
            isSnoutOut = x[0] < 50 or width - 50 < x[0]
            isRightOut = x[3] < 50 or width - 50 < x[3]
            isLeftOut = x[6] < 50 or width - 50 < x[6]

            if isSnoutOut and isRightOut and isLeftOut:
                dataset[i] = dataset[i-1]
            elif isSnoutOut and isRightOut:
                dataset[i] = [x[6], x[7]]
            elif isSnoutOut and isLeftOut:
                dataset[i] = [x[3], x[4]]
            elif isRightOut and isLeftOut:
                dataset[i] = [x[0], x[1]]
            elif isSnoutOut:
                dataset[i] = [(x[3] + x[6]) / 2, (x[4] + x[7]) / 2]
            elif isRightOut:
                dataset[i] = [(x[0] + x[6]) / 2, (x[1] + x[7]) / 2]
            elif isLeftOut:
                dataset[i] = [(x[0] + x[3]) / 2, (x[1] + x[4]) / 2]
            else:
                dataset[i] = [(x[0] + x[3] + x[6]) / 3, (x[1] + x[4] + x[7]) / 3]
            """
            """
            if ears_dist > 100:
                if x[5] > x[8]: #右耳のprobabilityの方が高い
                    dataset[i] = [x[3],x[4]]
                elif x[5] < x[8]: #左耳のprobabilityの方が高い
                    dataset[i] = [x[6],x[7]]
                else:
                    dataset[i] = [(x[3]+x[6])/2, (x[4]+x[7])/2]
            else:
            """
            if x[5] >= 0.5 and x[8] >= 0.5:
                dataset[i] = [(x[3]+x[6])/2, (x[4]+x[7])/2]
                probability_low = 0
            elif x[5] >= 0.5 and x[8] < 0.5:
                dataset[i] = [x[3],x[4]]
                probability_low = 0
            elif x[5] < 0.5 and x[8] >= 0.5:
                dataset[i] = [x[6],x[7]]
                probability_low = 0
            else:
                dataset[i] = dataset[i-1]
                probability_low += 1

            if probability_low > 3:
                print("Point stopped moving.")
                # return 0

            # dataset_snout[i] = [x[0], x[1]]
            # dataset_rightear[i] = [x[3], x[4]]
            # dataset_leftear[i] = [x[6], x[7]]
            # probabilities[i] = [x[2], x[5], x[8]]

    return length, dataset
    # return length, dataset, dataset_snout, dataset_rightear, dataset_leftear, probabilities

#h5ファイルを読み、フレーム数と各フレームでの鼻・両耳の中心の座標を返す
def read_h5_2points(filename):
    with h5py.File(filename, 'r') as f:
        length = f['df_with_missing/table'].shape[0]

        dataset = np.empty((length, 2)) #鼻,両耳の中心を格納する
        probabilities = np.empty((length, 2))

        probability_low = 0 # posture detectionが悪くて前のフレームを使うのが続いたら警告を出す

        for i in tqdm(range(length)):
            x = f['df_with_missing/table'][i][1]

            ears_dist = math.sqrt(pow(x[0]-x[3], 2) + pow(x[1]-x[4], 2))

            if x[2] >= 0.5 and x[5] >= 0.5:
                dataset[i] = [(x[0]+x[3])/2, (x[1]+x[4])/2]
                probability_low = 0
            elif x[2] >= 0.5 and x[5] < 0.5:
                dataset[i] = [x[0],x[1]]
                probability_low = 0
            elif x[2] < 0.5 and x[5] >= 0.5:
                dataset[i] = [x[3],x[4]]
                probability_low = 0
            else:
                dataset[i] = dataset[i-1]
                probability_low += 1

            if probability_low > 3:
                print("Point stopped moving.")

    return length, dataset


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

    accum_distance = 0
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
            if this_first_cs_start_frame - fps*60 <= i < this_first_cs_start_frame:
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

class mouseParam:
    def __init__(self, input_img_name):
        #マウス入力用のパラメータ
        self.mouseEvent = {"x":None, "y":None, "event":None, "flags":None}
        #マウス入力の設定
        cv2.setMouseCallback(input_img_name, self.__CallBackFunc, None)

    #コールバック関数
    def __CallBackFunc(self, eventType, x, y, flags, userdata):

        self.mouseEvent["x"] = x
        self.mouseEvent["y"] = y
        self.mouseEvent["event"] = eventType
        self.mouseEvent["flags"] = flags

    #マウス入力用のパラメータを返すための関数
    def getData(self):
        return self.mouseEvent

    #マウスイベントを返す関数
    def getEvent(self):
        return self.mouseEvent["event"]

    #マウスフラグを返す関数
    def getFlags(self):
        return self.mouseEvent["flags"]

    #xの座標を返す関数
    def getX(self):
        return self.mouseEvent["x"]

    #yの座標を返す関数
    def getY(self):
        return self.mouseEvent["y"]

    #xとyの座標を返す関数
    def getPos(self):
        return (self.mouseEvent["x"], self.mouseEvent["y"])

def getCoordinate(video_path):
    # video = cv2.VideoCapture(video_path)
    ret, frame = cv2.VideoCapture(video_path).read()

    #表示するウィンドウ名
    window_name = "Left click on the indicator."
    #画像の表示
    cv2.imshow(window_name, frame)
    #コールバックの設定
    mouseData = mouseParam(window_name)

    while 1:
        cv2.waitKey(20)
        #左クリックがあったら表示
        if mouseData.getEvent() == cv2.EVENT_LBUTTONDOWN:
            coords = mouseData.getPos()
            #print(coordinates)
            break
        #右クリックがあったら終了
        elif mouseData.getEvent() == cv2.EVENT_RBUTTONDOWN:
            break

    cv2.destroyAllWindows()

    return coords

def edgeCenterTime():
    section = np.array([], dtype=np.int64)

    edge = 0
    corner = 0
    center = 0

    for i in range(this_first_cs_start_frame - fps*60, this_first_cs_start_frame):
        if(coordinates[i][0] < x_border1 and coordinates[i][1] < y_border1):
            appendX = 1
            corner += 1
        elif(x_border1 <= coordinates[i][0] <= x_border2 and coordinates[i][1] < y_border1):
            appendX = 2
            edge += 1
        elif(x_border2 < coordinates[i][0] and coordinates[i][1] < y_border1):
            appendX = 3
            corner += 1
        elif(coordinates[i][0] < x_border1 and y_border1 <= coordinates[i][1] <= y_border2):
            appendX = 4
            edge += 1
        elif(x_border1 <= coordinates[i][0] <= x_border2 and y_border1 <= coordinates[i][1] <= y_border2):
            appendX = 5
            center += 1
        elif(x_border2 < coordinates[i][0] and y_border1 <= coordinates[i][1] <= y_border2):
            appendX = 6
            edge += 1
        elif(coordinates[i][0] < x_border1 and y_border2 < coordinates[i][1]):
            appendX = 7
            corner += 1
        elif(x_border1 <= coordinates[i][0] <= x_border2 and y_border2 < coordinates[i][1]):
            appendX = 8
            edge += 1
        elif(x_border2 < coordinates[i][0] and y_border2 < coordinates[i][1]):
            appendX = 9
            corner += 1
        else:
            appendX = 0

        section = np.append(section, appendX)

        # print(len(section))
        # print(section)

    return section, edge/(edge+corner+center), corner/(edge+corner+center), center/(edge+corner+center)


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


if __name__ == '__main__':
    data_root = "D:/"
    working_dir = getWorkingDir() + "/"
    # h5files_dir = working_dir + "h5files"
    edge_center_dir = working_dir + "AnalyzedData/edge_center_ratio/"
    cs_start_frames_path = working_dir + "AnalyzedData/cs_start_frames.pkl"
    if not os.path.exists(edge_center_dir):
        os.makedirs(edge_center_dir)

    h5files = natsort.natsorted(glob.glob(working_dir + "*.h5"))
    print("Analyzing " + str(len(h5files)) + " mice.")
    num_mice = len(h5files)

    print("How many bodyparts? (Only 2 or 3 are available for now.)")
    bodyparts = int(input())

    # tkinter.messagebox.showinfo('Distance & edge/center ratio', 'Enter in which session each mouse is includued. (1,2,...)')
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

    #video_path = working_dir + "box1_videos/Mouse9-IS_male_FearCondition_20191129-143941.avi"
    #test_video_name = working_dir + "test2.avi"

    """
    px_to_cm = px_to_cm() #長さ4の配列 各箱で1px何cmか
    mice_in_boxes = []
    """

    sensitivities = []
    activities = []

    """
    print("h5 files: " + str(h5files))
    if not len(mice_in_sessions) == len(h5files):
        print("h5files and mice number mismatch.")
    """

    cs_start_frames = get_cs_start_frames()
    print("Sessions: " + str(len(cs_start_frames)))
    print(cs_start_frames)

    left_up_edges = []
    # right_up_edges = []
    # left_down_edges = []
    right_down_edges = []


    for i in range(len(h5files)):
        left_up_edges.append(getCoordinate(videos[i]))
        # right_up_edges.append(getCoordinate(videos[i]))
        # left_down_edges.append(getCoordinate(videos[i]))
        right_down_edges.append(getCoordinate(videos[i]))

    # print(len(left_up_edges))

    # for i in range(9, len(mice_in_sessions)): #Mouse10IS♀だけでテスト中...
    for i in range(len(h5files)):
        video = cv2.VideoCapture(videos[i])
        fps = int(video.get(cv2.CAP_PROP_FPS))
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

        output_video_name = working_dir + "AnalyzedData/" + os.path.splitext(os.path.basename(h5files[i]))[0] + ".avi"

        # frames, coordinates, coord_snout, coord_rightear, coord_leftear, prob = read_h5(h5files[i])
        if bodyparts == 3:
            frames, coordinates = read_h5_3points(h5files[i])
        elif bodyparts == 2:
            frames, coordinates = read_h5_2points(h5files[i])
        else:
            print("Only 2 or 3 are available for now.")
            kill()

        # if coordinates == 0: sys.exit()

        # coordinatesが一瞬だけ飛んだりするのを補正する
        # coordinates = coordinates_correction(coordinates)

        this_cs_start_frames = cs_start_frames[mice_in_sessions[i]-1]
        this_first_cs_start_frame = this_cs_start_frames[0]

        sensitivity = get_sensitivity()
        sensitivities.append(sensitivity)

        activity = get_activity()
        activities.append(activity)

        left_up_edge = left_up_edges[i]
        right_down_edge = right_down_edges[i]
        x_border1 = left_up_edge[0] + (right_down_edge[0]-left_up_edge[0]) / 4
        x_border2 = left_up_edge[0] + (right_down_edge[0]-left_up_edge[0]) * 3 / 4
        y_border1 = left_up_edge[1] + (right_down_edge[1]-left_up_edge[1]) / 4
        y_border2 = left_up_edge[1] + (right_down_edge[1]-left_up_edge[1]) * 3 / 4

        section, edge_prob, corner_prob, center_prob = edgeCenterTime()
        with open(edge_center_dir + os.path.splitext(os.path.basename(h5files[i]))[0] + ".csv", 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["edge", edge_prob])
            writer.writerow(["corner", corner_prob])
            writer.writerow(["center", center_prob])

            #video_path = working_dir + "box1_videos/Mouse2-IS_male_FearCondition_20191129-132143.avi"

        if i == 0:
            _ = body_center_video()


    print(sensitivities)
    print(activities)

    with open(working_dir+"AnalyzedData/activity&sensitivity.csv", 'w') as f:
        writer = csv.writer(f)
        writer.writerow(sensitivities)
        writer.writerow(activities)
