# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import h5py
from tqdm import tqdm
import pickle
import csv
import matplotlib.pyplot as plt

class GetFreezingRate:
    def __init__(self, fps, cs_length, bodyparts2use, filename, num_cs, cs_starting_frame, filename_base):
        self.fps = fps
        self.cs_length = cs_length
        self.bp2use_arr = bodyparts2use
        self.bodyparts_all = len(bodyparts2use)
        self.bodyparts2use = np.sum(bodyparts2use)
        self.filename = os.path.dirname(filename) + "/" + os.path.splitext(os.path.basename(filename))[0] + ".h5"
        print("Loading h5 file: " + str(self.filename))
        # self.num_cs = num_cs
        self.cs_starting_frame = cs_starting_frame
        self.filename_base = filename_base

    #Read h5 and return coordinates of bodyparts across frames
    def read_h5(self):
        with h5py.File(self.filename, 'r') as f:
            length = f['df_with_missing/table'].shape[0]
            bodyparts = int(len(f['df_with_missing/table'][0][1]) / 3)

            dataset = np.empty((length, self.bodyparts2use * 2))

            delete_arr = np.arange(self.bodyparts_all * 3)
            for i in range(self.bodyparts_all):
                if self.bp2use_arr[i] == 1:
                    delete_arr[i*3] = -1
                    delete_arr[i*3+1] = -1

            delete_arr = np.delete(delete_arr, np.where(delete_arr==-1))

            for i in tqdm(range(length)):
                x = f['df_with_missing/table'][i][1]

                x = np.delete(x, delete_arr)

                dataset[i] = x

            return length, dataset, bodyparts

    def detect_freezing_with_snout_ears(self, length, _dataset):
        LPfilter = 10
        frames2look = 5
        threshold = 100
        snout_weight = 7
        bodypartsToUse = self.bodyparts2use * 2

        freezing = np.empty(length)
        distance_container = np.zeros(length)
        dataset = np.empty((length, bodypartsToUse))

        for i in range(length):
            dataset[i] = _dataset[i][:bodypartsToUse]

        for i in range(length-frames2look):
            if dataset[i][0]+dataset[i][1] == 0:
                #snoutが見えていなかったらFreezingではない
                freezing[i] = 0
            else:
                x = np.zeros(bodypartsToUse)
                for j in range(frames2look):
                    x += abs(dataset[i] - dataset[i+j])
                #snoutの重みを上げる
                x[0] *= snout_weight
                x[1] *= snout_weight
                distance = np.sum(x)
                #distance可視化のため
                distance_container[i] += distance

                if distance < threshold:
                    freezing[i] = 1
                else:
                    freezing[i] = 0

        #ローパスフィルター（一瞬だけのfreezingを消す
        for i in range(length - LPfilter):
            if freezing[i+1] - freezing[i] == 1:
                x = 0
                for j in range(LPfilter):
                    x += freezing[i+1+j]
                if x < LPfilter:
                    freezing[i+1] = 0

        return freezing, distance_container


    #Extract only CS-on frames in 0/1 array
    def extract_cs(self, freezing_frames, start_frame):
        end_frame = start_frame + self.cs_length * self.fps
        return freezing_frames[start_frame:end_frame]

    def __call__(self, freezing_frames_dir, distance_dir, each_frames_dir):
        #ベースライン用
        base_start = self.cs_starting_frame[0] - self.cs_length * self.fps
        print("CS starting frames: " + str(self.cs_starting_frame))

        self.cs_starting_frame.insert(0, base_start)
        cs_and_base = len(self.cs_starting_frame)

        freezing_rate = np.empty(cs_and_base)

        video_length, coordinates, bodyparts = self.read_h5()

        # print("There are " + str(bodyparts) + " bodyparts, and using " + str(self.bodyparts2use))

        freezing_frames, distance_container = self.detect_freezing_with_snout_ears(video_length, coordinates)

    	#freezing frames -> 1, not-freezing frames -> 0
        with open(freezing_frames_dir + self.filename_base + '.pkl', 'wb') as f:
            pickle.dump(freezing_frames, f)

        with open(distance_dir + self.filename_base + '.pkl', 'wb') as f:
            pickle.dump(distance_container, f)

        with open(each_frames_dir + self.filename_base + '.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(freezing_frames)

        for i in range(cs_and_base):
            freezing_frames_in_cs = self.extract_cs(freezing_frames, self.cs_starting_frame[i])
            #print(freezing_frames_in_cs)
            freezing_rate[i] = np.sum(freezing_frames_in_cs) / len(freezing_frames_in_cs)

        del self.cs_starting_frame[0]

        return freezing_rate
