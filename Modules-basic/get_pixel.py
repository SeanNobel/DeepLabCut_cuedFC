# -*- coding: utf-8 -*-
# This class was brought from https://whitecat-student.hatenablog.com/entry/2016/11/09/225631
import cv2

class mouseParam:
    def __init__(self, input_img_name):
        # psrameters for mouse inputs
        self.mouseEvent = {"x":None, "y":None, "event":None, "flags":None}
        #mouuse inputs configuration
        cv2.setMouseCallback(input_img_name, self.__CallBackFunc, None)

    def __CallBackFunc(self, eventType, x, y, flags, userdata):

        self.mouseEvent["x"] = x
        self.mouseEvent["y"] = y
        self.mouseEvent["event"] = eventType
        self.mouseEvent["flags"] = flags

    # returns mouse input parameters
    def getData(self):
        return self.mouseEvent

    # returns mouse event
    def getEvent(self):
        return self.mouseEvent["event"]

    # returns mouse flag
    def getFlags(self):
        return self.mouseEvent["flags"]

    # returns x coordinate
    def getX(self):
        return self.mouseEvent["x"]

    # returns y coordinate
    def getY(self):
        return self.mouseEvent["y"]

    # returns x and y coordinates
    def getPos(self):
        return (self.mouseEvent["x"], self.mouseEvent["y"])
