# -*- coding: utf-8 -*-
import numpy as np
import h5py
import sys
from tqdm import tqdm
import pickle
import csv
import matplotlib.pyplot as plt

#Read h5 and return coordinates of bodyparts across frames
def read_h5(filename, bodypartsToUse):
    with h5py.File(filename, 'r') as f:
        length = f['df_with_missing/table'].shape[0]
        bodyparts = int(len(f['df_with_missing/table'][0][1]) / 3)

        dataset = np.empty((length, bodypartsToUse*2))

        for i in tqdm(range(length)):
            x = f['df_with_missing/table'][i][1]
            #probabilityが0.5以下ならその部位の座標は(0,0)
            """
            # tail_tip
            if x[11] < 0.5:
                x[9] = 0
                x[10] = 0
            # snout
            if x[2] < 0.5:
                x[0] = 0
                x[1] = 0
            """
            if bodypartsToUse == 4:
                delete_arr = [2,5,8,9,10,11,12,13,14,15,16,17,20,21,22,23,26,29]
            elif bodypartsToUse == 2:
                delete_arr = [2,5,8,11,14,17,20,23,26,29] # bodypartsが10以上ある場合は要修正
            else:
                print("2 or 4 bodyparts are available for now. Please contact Nobe.")
                kill()

            x = np.delete(x, delete_arr)
            #もともとbodyparts３つのh5ファイルに対しては
            #x = np.delete(x, [2,5,8])
            dataset[i] = x

        return length, dataset, bodyparts

def detect_freezing_with_snout_ears(length, _dataset, bodypartsToUse):
    LPfilter = 10
    frames2look = 5
    threshold = 100
    snout_weight = 7
    bodypartsToUse *= 2

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
    """
    #distance可視化
    plt.xlim(0,500)
    plt.ylim(0,1000)
    plt.plot(np.arange(length), distance_container, linewidth=0.7)
    plt.show()
    #freezing可視化
    plt.xlim(0,10000)
    plt.ylim(-0.1,1.1)
    plt.plot(np.arange(length), freezing, linewidth=0.3)
    plt.show()
    """

    return freezing, distance_container

#Reads bodyparts coordinates and returns freezing frames with 1 or 0
"""
def detect_freezing(length, dataset, num_bodyparts):#datasetは各体部位のx座標,y座標,その確率
    LPfilter = 10
    frames2look = 5
    threshold = 100
    snout_weight = 7

    freezing = np.empty(length)
    distance_container = np.zeros(length)

    for i in range(length-frames2look):
        if dataset[i][0]+dataset[i][1] == 0:
            #snoutが見えていなかったらFreezingではない
            freezing[i] = 0
        else:
            x = np.empty(num_bodyparts*2)
            for j in range(frames2look):
                x = abs(dataset[i] - dataset[i+j])
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

    #ローパスフィルター
    for i in range(length - LPfilter):
        if freezing[i+1] - freezing[i] == 1:
            x = 0
            for j in range(LPfilter):
                x += freezing[i+1+j]
            if x < LPfilter:
                freezing[i+1] = 0

    #distance可視化
    plt.xlim(0,10000)
    plt.ylim(0,2000)
    plt.plot(np.arange(length), distance_container, linewidth=0.3)
    plt.show()
    #freezing可視化
    plt.xlim(0,10000)
    plt.ylim(-0.1,1.1)
    plt.plot(np.arange(length), freezing, linewidth=0.3)
    plt.show()

    return freezing, distance_container
"""

#Extract only CS-on frames in 0/1 array
def extract_cs(freezing_frames, start_frame, fps):
    end_frame = start_frame + 20 * fps
    return freezing_frames[start_frame:end_frame]

def getFreezingRate(fps, bodypartsToUse, filename, num_cs, cs_starting_frame, filename_base, freezing_frames_dir, distance_dir, freezing_photometry_dir):
    #ベースライン用
    base_start = cs_starting_frame[0] - 20*15
    cs_starting_frame.insert(0, base_start)
    cs_and_base = len(cs_starting_frame)
    print(cs_starting_frame)
    print(cs_and_base)

    freezing_rate = np.empty(cs_and_base)

    video_length, coordinates, bodyparts = read_h5(filename, bodypartsToUse)

    print("There are " + str(bodyparts) + " bodyparts, and using " + str(bodypartsToUse))

    freezing_frames, distance_container = detect_freezing_with_snout_ears(video_length, coordinates, bodypartsToUse)

	#freezingしているフレームの情報を0/1で出力（video_with_indicatior用）
    with open(freezing_frames_dir + filename_base + '.pkl', 'wb') as f:
        pickle.dump(freezing_frames, f)

    with open(distance_dir + filename_base + '.pkl', 'wb') as f:
        pickle.dump(distance_container, f)

    with open(freezing_photometry_dir + filename_base + '.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(freezing_frames)

    for i in range(cs_and_base):
        freezing_frames_in_cs = extract_cs(freezing_frames, cs_starting_frame[i], fps)
        #print(freezing_frames_in_cs)
        freezing_rate[i] = np.sum(freezing_frames_in_cs) / len(freezing_frames_in_cs)

    del cs_starting_frame[0]

    return freezing_rate

def main():
    pass

if __name__ == '__main__':
    main()
