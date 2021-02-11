import os
import numpy as np
import cv2
import csv
from Modules.get_pixel import mouseParam

class EdgeCenterRatio(mouseParam):
    def __init__(self, h5files, videos, movement_measure_time):
        self.left_up_edges = []
        self.right_down_edges = []
        self.h5files = h5files
        self.videos = videos
        self.mm_time = movement_measure_time

        for i in range(len(self.h5files)):
            self.left_up_edges.append(self.getCoordinate(self.videos[i]))
            self.right_down_edges.append(self.getCoordinate(self.videos[i]))

    def getCoordinate(self, video_path):
        self.ret, self.frame = cv2.VideoCapture(video_path).read()

        window_name = "Left click on the indicator."

        cv2.imshow(window_name, self.frame)
        # set callback
        self.mouseData = mouseParam(window_name)

        while 1:
            cv2.waitKey(20)
            # display when left click happen
            if self.mouseData.getEvent() == cv2.EVENT_LBUTTONDOWN:
                self.coords = self.mouseData.getPos()
                #print(coordinates)
                break
            # end when right click happen
            elif self.mouseData.getEvent() == cv2.EVENT_RBUTTONDOWN:
                break

        cv2.destroyAllWindows()

        return self.coords

    def edgeCenterTime(self):
        section = np.array([], dtype=np.int64)

        edge = 0
        corner = 0
        center = 0

        for i in range(self.first_cs_start_frame - self.fps * self.mm_time, self.first_cs_start_frame):
            if(self.coordinates[i][0] < self.x_border1 and self.coordinates[i][1] < self.y_border1):
                appendX = 1
                corner += 1
            elif(self.x_border1 <= self.coordinates[i][0] <= self.x_border2 and self.coordinates[i][1] < self.y_border1):
                appendX = 2
                edge += 1
            elif(self.x_border2 < self.coordinates[i][0] and self.coordinates[i][1] < self.y_border1):
                appendX = 3
                corner += 1
            elif(self.coordinates[i][0] < self.x_border1 and self.y_border1 <= self.coordinates[i][1] <= self.y_border2):
                appendX = 4
                edge += 1
            elif(self.x_border1 <= self.coordinates[i][0] <= self.x_border2 and self.y_border1 <= self.coordinates[i][1] <= self.y_border2):
                appendX = 5
                center += 1
            elif(self.x_border2 < self.coordinates[i][0] and self.y_border1 <= self.coordinates[i][1] <= self.y_border2):
                appendX = 6
                edge += 1
            elif(self.coordinates[i][0] < self.x_border1 and self.y_border2 < self.coordinates[i][1]):
                appendX = 7
                corner += 1
            elif(self.x_border1 <= self.coordinates[i][0] <= self.x_border2 and self.y_border2 < self.coordinates[i][1]):
                appendX = 8
                edge += 1
            elif(self.x_border2 < self.coordinates[i][0] and self.y_border2 < self.coordinates[i][1]):
                appendX = 9
                corner += 1
            else:
                appendX = 0

            section = np.append(section, appendX)

        return section, edge / (edge + corner + center), corner / (edge + corner + center), \
            center / (edge + corner + center)

    def __call__(self, i, first_cs_start_frame, fps, coordinates, ec_ratio_dir):
        self.left_up_edge = self.left_up_edges[i]
        self.right_down_edge = self.right_down_edges[i]
        self.first_cs_start_frame = first_cs_start_frame
        self.fps = fps
        self.coordinates = coordinates

        self.x_border1 = self.left_up_edge[0] + (self.right_down_edge[0] - self.left_up_edge[0]) / 4
        self.x_border2 = self.left_up_edge[0] + (self.right_down_edge[0] - self.left_up_edge[0]) * 3 / 4
        self.y_border1 = self.left_up_edge[1] + (self.right_down_edge[1] - self.left_up_edge[1]) / 4
        self.y_border2 = self.left_up_edge[1] + (self.right_down_edge[1] - self.left_up_edge[1]) * 3 / 4

        self.section, self.edge_prob, self.corner_prob, self.center_prob = self.edgeCenterTime()
        with open(ec_ratio_dir + os.path.splitext(os.path.basename(self.h5files[i]))[0] + ".csv", 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["edge", self.edge_prob])
            writer.writerow(["corner", self.corner_prob])
            writer.writerow(["center", self.center_prob])

            #video_path = working_dir + "box1_videos/Mouse2-IS_male_FearCondition_20191129-132143.avi"