#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 15:22:45 2024

@author: yuyuan
"""

import os
from astropy.io import fits
import cv2 as cv



series = '030'
n_photo = 110871


pa = os.path.dirname(__file__) 
# path = pa+"/"+series+"/image/%d.JPG"%n_photo
#
for i in range(10):
    n_photo1 = n_photo +i
    path = pa+"/"+series+"/image/iss"+series+"e%d.JPG"%n_photo1
    img = cv.imread(path,-1) 
    img1 = img[700:2844,:,:]
    img = img[700:1300,:,:]
    cv.imwrite(pa+"/"+series+'/astro/%d.JPG'%n_photo1, img)
    cv.imwrite(pa+"/"+series+'/astro/030e%d.JPG'%n_photo1, img1)
    

