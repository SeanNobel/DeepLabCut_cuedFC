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
import yaml

#h5ファイルを読み、フレーム数と各フレームでの鼻・両耳の中心の座標を返す
class Read_h5:
    def __init__(self, filename):
        self.filename = filename

        with h5py.File(self.filename, 'r') as f:
            self.length = f['df_with_missing/table'].shape[0]

            self.dataset = np.empty((self.length, 2)) # Container of the center of all the bodyparts selected
            self.num_bodyparts = int(len(f['df_with_missing/table'][0][1]) / 3)
            self.isProbHigh = np.empty(self.num_bodyparts)
            self.x_coordinates = np.empty(self.num_bodyparts)
            self.y_coordinates = np.empty(self.num_bodyparts)
            self.numPointsHighProb = 0

            self.probability_low = 0 # Alert if low probability by DLC continued for frames

    def bodyparts_3(self):
        with h5py.File(self.filename, 'r') as f:
            for i in tqdm(range(self.length)):
                self.x = f['df_with_missing/table'][i][1]
                for j in range(self.num_bodyparts):
                    self.x_coordinates[j] = self.x[j*3]
                    self.y_coordinates[j] = self.x[j*3 + 1]
                    self.isProbHigh[j] = self.x[j*3 + 2] >= 0.5

                self.numPointsHighProb = np.sum(self.isProbHigh)

                if self.numPointsHighProb == 0:
                    self.probability_low += 1
                    self.dataset[i] = self.dataset[i-1]
                else:
                    self.probability_low = 0
                    self.dataset[i] = np.array([np.dot(self.x_coordinates, self.isProbHigh), \
                        np.dot(self.y_coordinates, self.isProbHigh)]) / self.numPointsHighProb
                """
                if self.x[5] >= 0.5 and self.x[8] >= 0.5:
                    self.dataset[i] = [(self.x[3] + self.x[6]) / 2, (self.x[4] + self.x[7]) / 2]
                    self.probability_low = 0
                elif self.x[5] >= 0.5 and self.x[8] < 0.5:
                    self.dataset[i] = [self.x[3], self.x[4]]
                    self.probability_low = 0
                elif self.x[5] < 0.5 and self.x[8] >= 0.5:
                    self.dataset[i] = [self.x[6], self.x[7]]
                    self.probability_low = 0
                else:
                    self.dataset[i] = self.dataset[i-1]
                    self.probability_low += 1
                """

                if self.probability_low == 4:
                    print("Low probability continued for more than 4 frames. Consider refining DLC network.\n")

        return 0


    def bodyparts_2(self):
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

    def bodypart_1(self):
        return 0

    def __call__(self):
        if self.num_bodyparts == 3:
            _ = self.bodyparts_3()
        elif self.num_bodyparts == 2:
            _ = self.bodyparts_2()
        elif self.num_bodyparts == 1:
            _ = self.bodypart_1()
        else:
            print("You can use data with bodyparts up to 3.")
            sys.exit()

        return self.length, self.dataset, self.num_bodyparts