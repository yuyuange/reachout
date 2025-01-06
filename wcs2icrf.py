
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 11 19:27:58 2022

@author: yuyuan
"""
import time
import exifread
import datetime
import cv2
import numpy as np
import pandas as pd
import os
from spacepy import coordinates as coord
from spacepy.time import Ticktock
from astropy.time import Time
from astropy.wcs.wcs import WCS
from scipy import interpolate
from geographiclib.constants import Constants


wgs84A = Constants.WGS84_a/1000
wgs84B = wgs84A * (1 - Constants.WGS84_f)
from aurointersection import ellipsoidLineIntersection,ellipsoidLineIntersects
from transformations import rotation_matrix


X = [-1,0,0]
Y = [0,1,0]
Z = [0,0,-1]

def date2es(date): 
    """
    Converts UTC to ephemeris seconds.
    """
    jd = Time(date, scale='utc').jd
    return (jd - 2451545) * 86400
    # cxform used the following which limits precision unnecessarily to 1sec:
#    return long(round((jd - 2451545) * 86400))

def hapgood_matrix(theta, axis):
    if axis==[1,0,0]:
        axis = 0
    elif axis==[0,1,0]:
        axis = 1
    elif axis==[0,0,1]:
        axis = 2

    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    t1 = (axis+1) % 3
    t2 = (axis+2) % 3
    if (t1 > t2):
        tmp = t1
        t1  = t2
        t2  = tmp
    
    mat = np.zeros((3,3))

    mat[axis,axis] = 1.0
    mat[t1,t1]     = cos_theta
    mat[t2,t2]     = cos_theta

    mat[t1,t2]     =  sin_theta
    mat[t2,t1]     = -sin_theta
    return mat

def T0(et):
    """
    Julian Centuries from a certain time to 1 Jan 2000 12:00
    """
    return (et / 86400.0)/36525.0

def H(et):
    """
    time, in hours, since preceding UT midnight
    """
    jd    = (et / 86400.0) - 0.5
    dfrac = jd - int(jd)
    hh    = dfrac * 24.0

    if (hh < 0.0):
        hh += 24.0

    return hh

def mat_P(et):
    """
    J2000 to GEI matrix
    """
    t0 = T0(et)
    
    mat = rotation_matrix(np.deg2rad(-1.0*(0.64062 * t0  +  0.00030 * t0*t0)), Z)

    mat_tmp = rotation_matrix(np.deg2rad(0.55675 * t0  -  0.00012 * t0*t0), Y)
    mat = np.dot(mat, mat_tmp)
        
    mat_tmp = rotation_matrix(np.deg2rad(-1.0*(0.64062 * t0  +  0.00008 * t0*t0)), Z)
    mat = np.dot(mat, mat_tmp)
    return mat[:3,:3]

def mat_T1(et):
    """
    GEI to GEO matrix
    """
    theta = 100.461 + 36000.770 * T0(et) + 360.0*(H(et)/24.0)

    mat = rotation_matrix(np.deg2rad(theta), Z)
    return mat[:3,:3]

def mat_j2000_to_geo(et):
    # j2000_twixt_gei -> gei_twixt_geo
    mat = np.dot(mat_T1(et), mat_P(et))
    return mat

def j2000_to_geo(date, vecsJ2000):
    return x_to_y(mat_j2000_to_geo, date, vecsJ2000)

def x_to_y(matFn, date, vecs, reverse=False):
    global vecs1
    vecs1 = np.asarray(vecs)
    assert vecs1.ndim == 2 
    assert vecs1.shape[1] == 3
    
    et = date2es(date)
    global mat
    mat = matFn(et)

    if reverse:
        mat = mat.T
    # vecsOut = matrix_multiply(mat, vecs[...,np.newaxis]).reshape(vecs.shape)
    # print(mat,vecs1[...,np.newaxis])
    vecsOut = np.dot(mat,vecs1.T).T

    return vecsOut

def j2000Toecef(j2000Vecs, time_):
    """
    Convert cartesian J2000 coordinates to geodetic coordinates.
    
    :param j2000Vecs: shape (n,3)
    :param datetime time_:
    :rtype: tuple (latitudes, longitudes) in degrees
    """
    t0 = time.time()
    j2000Vecs = np.asarray(j2000Vecs)
    geoX, geoY, geoZ = j2000_to_geo(time_, j2000Vecs).T
    # print('convert J2000-GEO:', time.time()-t0, 's')
    
    return geoX, geoY, geoZ

def xyz2lla(x,y,z):

    cvals = coord.Coords([x/Re,y/Re,z/Re], 'GEO','car')
    cvals.ticks = Ticktock(time_b, 'ISO')
    geocoord = cvals.convert('GDZ', 'sph')
    lat = geocoord.lati
    lon = geocoord.long
    radi = geocoord.radi
    lla = np.array([lat,lon,radi])
    return lla

coord.DEFAULTS.set_values(use_irbem=False, itol=5)

Re = 6378.137
series = '030'
n_photo = 110875

##file path
path = os.path.dirname(__file__) +"/"+series
raw_path = path+"/image_raw/iss"+series+"e%d.NEF"%n_photo

path_direc = os.path.join(path+'/pixeldirection_astro')
if not os.path.exists(path_direc):
    os.makedirs(path_direc)

path_hor = os.path.join(path+'/hor')
if not os.path.exists(path_hor):
    os.makedirs(path_hor)

## iss position
data_1 = pd.read_csv(path+'/issreport030.csv')
time1 = data_1['Time (ISO-YMD)'].values
x = data_1['x (km)'].values
y = data_1['y (km)'].values
z = data_1['z (km)'].values
length = len(x)
##interpolation for time
xx = np.linspace(0,length-1,length)  #i axis
x = interpolate.interp1d(xx,x,kind='linear')
y = interpolate.interp1d(xx,y,kind='linear')
z = interpolate.interp1d(xx,z,kind='linear')

t1 = datetime.datetime.fromisoformat(time1[0])


img = exifread.process_file(open(raw_path,'rb'))
time_img = img['Image DateTime']
time_img = str(time_img)
time_img = datetime.datetime.strptime(time_img, "%Y:%m:%d %H:%M:%S")
time_img_astro = time_img.strftime("%Y-%m-%dT%H:%M:%S")
timelag = datetime.timedelta(seconds=-18)

time_true = time_img+timelag
time_diff = time_true - t1
time_diff = time_diff.total_seconds()
i0 = int(time_diff*10)
time_b = time1[i0]
issposition = np.array([x(i0),y(i0),z(i0)])

img = cv2.imread(path+'/astro/'+series+'e%d.JPG'%n_photo)
corner = True
height,width,channel =img.shape

startX = 0
startY = 0


if corner:
        startX -= 0.5 # top left corner instead of pixel center
        startY -= 0.5
x, y = np.meshgrid(np.arange(startX,startX+width+corner), np.arange(startY,startY+height+corner))

wcs = WCS(path+'/astro/%d_a.wcs'%n_photo)

ra, dec = wcs.all_pix2world(x, y, 0, ra_dec_order=True)

np.deg2rad(ra,ra)
np.deg2rad(dec,dec)


x_GCRS =np.zeros([height,width])
y_GCRS =np.zeros([height,width])
z_GCRS =np.zeros([height,width])
for i in range(height):
    for j in range(width):
        z = np.sin(dec[i,j])
        y = np.cos(dec[i,j])*np.sin(ra[i,j])
        x = np.cos(dec[i,j])*np.cos(ra[i,j])
        x_GCRS[i,j] = x
        y_GCRS[i,j] = y
        z_GCRS[i,j] = z

            
J2000vec = np.zeros([height,width,3])
J2000vec[:,:,0] = x_GCRS
J2000vec[:,:,1] = y_GCRS
J2000vec[:,:,2] = z_GCRS

img_orientation1 =   np.zeros([height,width,3])
for j in range(height):
    xyz = j2000Toecef(J2000vec[j,:,:],time_img_astro)
    geox = xyz[0]
    geoy = xyz[1]
    geoz = xyz[2]
    img_orientation1[j,:,0] = geox
    img_orientation1[j,:,1] = geoy
    img_orientation1[j,:,2] = geoz
    
np.savetxt(path_direc+"/%dx.txt"%n_photo, img_orientation1[:,:,0])
np.savetxt(path_direc+"/%dy.txt"%n_photo, img_orientation1[:,:,1])
np.savetxt(path_direc+"/%dz.txt"%n_photo, img_orientation1[:,:,2])



lineintersection = np.zeros([height,width,2])

img_orientation = img_orientation1.reshape(-1,3)
aa = ellipsoidLineIntersects(wgs84A,wgs84B,issposition,img_orientation)
ab = ellipsoidLineIntersection(wgs84A,wgs84B,issposition,img_orientation)

horiline = aa.reshape(height,width)

time1 = [time_b for i in range(len(aa))]
cvals = coord.Coords(ab/Re, 'GEO','car')
cvals.ticks = Ticktock(time1, 'ISO')
geocoord = cvals.convert('GDZ', 'sph')
lat = geocoord.lati
lon = geocoord.long
lat = lat.reshape(height,width)
lon = lon.reshape(height,width)
lineintersection[:,:,0] = lon
lineintersection[:,:,1] = lat


# for i in range(height):
#     linedirection = img_orientation1[i,:,:]
    
#     for j in range(width):
#         cvals = coord.Coords([x/Re,y/Re,z/Re], 'GEO','car')
#         cvals.ticks = Ticktock(time_b, 'ISO')
#         geocoord = cvals.convert('GDZ', 'sph')        
#         lineintersection[i,j] = np.array([geocoord.long[0],geocoord.lati[0]])
#     horiline[i,:] = aa

    # for j in range(width):
    #     linedirection = np.array([[img_orientation1[i,j,0],img_orientation1[i,j,1],img_orientation1[i,j,2]],[img_orientation1[i,j,0],img_orientation1[i,j,1],img_orientation1[i,j,2]]])
    #     aa = ellipsoidLineIntersects(wgs84A,wgs84B,issposition,linedirection)
    #     if aa[0]  == 1:
    #         ab = ellipsoidLineIntersection(wgs84A,wgs84B,issposition,linedirection)
    #         ab1 = xyz2lla(ab[0,0],ab[0,1],ab[0,2])
    #         lineintersection[i,j] = np.array([ab1[1,0],ab1[0,0]])
    #     horiline[i,j] = aa[0]
        
cv2.imwrite(path+'/horiline%d.JPG'%n_photo,horiline*255)
horiline = cv2.imread(path+'/horiline%d.JPG'%n_photo)
combine = cv2.addWeighted(img,1,horiline,0.1,0)
cv2.imwrite(path+'/combine%d.jpg'%n_photo,combine)

np.savetxt(path_direc+"/%dlineintlon.txt"%n_photo, lineintersection[:,:,0])
np.savetxt(path_direc+"/%dlineintlat.txt"%n_photo, lineintersection[:,:,1])
# np.savetxt(path+"/pixeldirection_astro/%dlineintz.txt"%n_photo, lineintersection[:,:,2])