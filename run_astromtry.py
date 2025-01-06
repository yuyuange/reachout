#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 15:00:36 2023
##astromerty
need to be run in env astro
@author: yuyuan
"""
import os
from astropy.io import fits
# import cv2 as cv



series = '030'
n_photo = 110875


pa = os.path.dirname(__file__) 

path = pa+"/"+series+"/astro/%d.JPG"%n_photo
##
    

os.system('cd '+pa+ '/astro;solve-field  -l 60 --downsample 4 '+path+' --overwrite')

##
hdulist4 = fits.open(pa+"/"+series+'/astro/%d.axy'%n_photo)
data4 = hdulist4[1].data #数据
header4 = hdulist4[1].header
header4_ = hdulist4[0].header


data4.X = data4.X
data = fits.BinTableHDU(data4)

data.writeto(pa+"/"+series+'/astro/%d_a.xyls'%n_photo, overwrite=True)
##
path1 = pa+"/"+series+"/astro/%d_a.xyls"%n_photo
path2 = pa+"/"+series+'/astro/'+series+'e%d.JPG'%n_photo
cmd ='solve-field '+path1+' --crpix-center -no-tweak --overwrite -E 4  --scale-units arcsecperpix --scale-low 30 --scale-high 80 --width 4284 --height 2144 --plot-bg '+path2
os.system(cmd)