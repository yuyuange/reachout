#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 19:26:17 2022

@author: yuyuan
"""


import os
import cv2
import numpy as np
import pandas as pd


n_photo = 110870
path = os.path.dirname(__file__) 
img = cv2.imread(path+'/image/iss030e%d.JPG'%n_photo,-1)

xc_list = []
yc_list = []
xc = []
yc = []
count = 0
def on_EVENT_RBUTTONDOWN(event, x, y, flags, param):
    global xc,yc,count,img
    if event == cv2.EVENT_LBUTTONDOWN:
        img = cv2.imread(path+'/image/iss030e%d.JPG'%n_photo,-1)
        xy = "  %d,%d" % (x, y)
        cv2.circle(img, (x, y), 20, (255, 255, 255), thickness = 3)
        cv2.putText(img, xy, (x, y), cv2.FONT_HERSHEY_PLAIN,
                    3.0, (255,0,255), thickness = 5)
        cv2.imshow("image", img)
        
        xc = x
        yc = y
    if event == cv2.EVENT_RBUTTONDOWN:
        xc_list.append(xc)
        yc_list.append(yc)
        count+=1
        print('city_%d'%count)
cv2.namedWindow("image",cv2.WINDOW_NORMAL)
cv2.setMouseCallback("image", on_EVENT_RBUTTONDOWN)

while(1):
    cv2.imshow("image", img)
    if cv2.waitKey(0)&0xFF==27:
        break
    # else if cv2.waitKey(0)&0xFF==:
        
cv2.destroyAllWindows()
cv2.waitKey(1)

# position = pd.read_table("/Users/yuyuan/Desktop/aurora/030e51088.txt",header=None)
# lat = position[1]
# lon = position[2]
city_light = pd.read_csv(path+'/030e115216.csv')
lat = city_light['lat'].values
lon = city_light['lon'].values
u_cl = xc_list
v_cl = yc_list
city_light = pd.DataFrame({'lat':lat,'lon':lon,'u_cl':u_cl,'v_cl':v_cl})
city_light.to_csv(path+"/030e%d.csv"%n_photo)

# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10 13:58:57 2022
@author: 
"""

# img = cv2.imread(path+'/image/030e%d.JPG'%n_photo,-1)
# city_light = pd.read_csv(path+'/030e115216.csv')
# lat = city_light['lat'].values
# lon = city_light['lon'].values
# u_cl = city_light['u_cl'].values
# v_cl = city_light['v_cl'].values

# n_city =len(lat)
# for n in range(n_city):
#     cv2.circle(img,(int(u_cl[n]),int(v_cl[n])),50,(0,0,255),10)
#     xy = "  %d,%d,%d" % (u_cl[n],v_cl[n],n+1)
#     cv2.putText(img, xy, (u_cl[n],v_cl[n]), cv2.FONT_HERSHEY_PLAIN,
#                 3.0, (255,255,255), thickness = 5)
# cv2.imwrite(path+'/test/test%d.JPG'%n_photo,img)























