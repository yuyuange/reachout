#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 23:20:11 2023
lens distortion correction
@author: yuyuan
"""


import rawpy
import rawpy.enhance
import imageio
import os
import glob
#remove dead pixels
# paths = ('/Users/yuyuan/Desktop/mywork/cl_raw/iss053e051093.NEF','/Users/yuyuan/Desktop/mywork/cl_raw/iss053e051089.NEF','/Users/yuyuan/Desktop/mywork/cl_raw/iss053e051090.NEF','/Users/yuyuan/Desktop/mywork/cl_raw/iss053e051091.NEF','/Users/yuyuan/Desktop/mywork/cl_raw/iss053e051092.NEF')
path = os.path.dirname(__file__) +'/image_raw/'
id_file = path+'*.NEF'
paths = tuple()
for file in glob.glob(id_file):
    print(file)
    paths = paths.__add__((file,))


bad_pixels = rawpy.enhance.find_bad_pixels(paths)
bit = rawpy.Params(output_bps=16)

for path in paths:
    with rawpy.imread(path) as raw:
        image = raw.raw_image_visible
        rawpy.enhance.repair_bad_pixels(raw, bad_pixels,method='median')
        rgb = raw.postprocess(bit)
    # imageio.imsave(path[:-4] + '.tiff',rgb)
    imageio.imsave(path + '.tiff',rgb)

    os.system('exiftool -TagsFromFile '+path+' '+path+'.tiff')
  

#os.system('exiftool -TagsFromFile /Users/yuyuan/Desktop/mywork/cl_raw/iss053e051088.NEF /Users/yuyuan/Desktop/mywork/cl_raw/iss053e051088.NEF.tiff')
# openpath = '/Users/yuyuan/Desktop/mywork/cl_raw/iss053e051088.NEF'
# # image = rawpy.imread('/Users/yuyuan/Desktop/mywork/cl_raw/iss053e051088.NEF')
# with rawpy.imread(openpath) as raw:
#     image1 = raw.raw_image_visible;

