# -*- coding: utf-8 -*-
import os
import cv2
import numpy as np
import tqdm
import glob
from natsort import natsorted

# This class was brought from https://whitecat-student.hatenablog.com/entry/2016/11/09/225631
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

class GetCS_Starts:
    def __init__(self, videos, num_cs):
        self.videos = videos
        self.num_cs = num_cs
        self.cs_start_frames_sessions = []
        self.light_coordinates = []
        self.init_brightness = []

    def getLightLocation(self, video_path):
        video = cv2.VideoCapture(video_path)
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
                coordinates = mouseData.getPos()
                #print(coordinates)
                break
            #右クリックがあったら終了
            elif mouseData.getEvent() == cv2.EVENT_RBUTTONDOWN:
                break

        cv2.destroyAllWindows()

        return coordinates, frame[coordinates[1]][coordinates[0]][0]


    def __call__(self):
        print(self.videos)

        for i in range(len(self.videos)):

            video_path = self.videos[i]
            _light_coordinates, _init_brightness = self.getLightLocation(video_path)

            self.light_coordinates.append(_light_coordinates)
            self.init_brightness.append(_init_brightness)

        for i in range(len(self.videos)):
            video_path = self.videos[i]

            video = cv2.VideoCapture(video_path)

            frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

            brightness = self.init_brightness[i]
            print("init: "+str(brightness))
            #CSがいったん始まったらfps*20秒+αフレームの間はCSを検出しないようにするためのもの
            x = 0
            #num_cs以上はCSを検出しない（StopRecordingしないで扉を開けてしまったときのため
            y = self.num_cs

            cs_start_frames = []
            for j in range(frames):
                if y == 0:
                    break
                else:
                    pass

                ret, frame = video.read()

                if ret:
                    if frame[self.light_coordinates[i][1]][self.light_coordinates[i][0]][0] > brightness + 100 and x <= 0:
                        cs_start_frames.append(j)
                        print("Frame: "+str(j)+" brightness: "+str(frame[self.light_coordinates[i][1]][self.light_coordinates[i][0]][0]))
                        #CSがいったん始まったらfps*20秒+αフレームの間はCSを検出しないようにするため
                        x = 20 * 20 + 10
                        y -= 1
                    else:
                        pass
                    x -= 1

            print("CS: "+str(len(cs_start_frames)))

            if len(cs_start_frames) != self.num_cs:
                print("Couldn't detect "+str(self.num_cs)+" CSs! Try again with another coordinates, or alter the threshold.")
                return 0
            else:
                pass

            self.cs_start_frames_sessions.append(cs_start_frames)

        return self.cs_start_frames_sessions
