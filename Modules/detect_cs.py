# -*- coding: utf-8 -*-
import os
import cv2
import numpy as np
import tqdm
import glob
from natsort import natsorted
from Modules_basic.get_pixel import mouseParam

class GetCS_Starts:
    def __init__(self, videos, num_cs, light_threshold):
        self.videos = videos
        self.num_cs = num_cs
        self.cs_start_frames_sessions = []
        self.light_coordinates = []
        self.init_brightness = []
        self.alpha = 20 # frames
        self.light_threshold = light_threshold

    def getLightLocation(self, video_path):
        video = cv2.VideoCapture(video_path)
        ret, frame = cv2.VideoCapture(video_path).read()

        window_name = "Left click on the indicator."

        cv2.imshow(window_name, frame)
        # setting up callback
        mouseData = mouseParam(window_name)

        while True:
            cv2.waitKey(20)
            # displays when left click happened
            if mouseData.getEvent() == cv2.EVENT_LBUTTONDOWN:
                coordinates = mouseData.getPos()
                break
            # end when right click happened
            elif mouseData.getEvent() == cv2.EVENT_RBUTTONDOWN:
                break

        cv2.destroyAllWindows()

        return coordinates, frame[coordinates[1]][coordinates[0]][0]


    def __call__(self, fps, cs_length):
        # print(self.videos)

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
            print("Inititial brightness: "+str(brightness))
            # Stop detecting CS for fps*csSeconds+alpha once CS started
            dont_detect = 0
            # To avoid detecting CS more than num_cs (in case opened doors before stopping recording and let the light in)
            numcs = self.num_cs

            cs_start_frames = []
            for j in range(frames):
                if numcs == 0:
                    break
                else:
                    pass

                ret, frame = video.read()

                if ret:
                    if frame[self.light_coordinates[i][1]][self.light_coordinates[i][0]][0] > self.light_threshold and dont_detect <= 0:
                        cs_start_frames.append(j)
                        print("Frame: "+str(j)+" brightness: "+str(frame[self.light_coordinates[i][1]][self.light_coordinates[i][0]][0]))

                        dont_detect = fps * cs_length + self.alpha
                        numcs -= 1
                    else:
                        pass
                    dont_detect -= 1

            print("Successfully detected " + str(len(cs_start_frames)) + " CSs.")

            if len(cs_start_frames) != self.num_cs:
                print("Couldn't detect "+str(self.num_cs)+" CSs! Try again with another coordinates, or alter the threshold.")
                return 0
            else:
                pass

            self.cs_start_frames_sessions.append(cs_start_frames)

        return self.cs_start_frames_sessions
