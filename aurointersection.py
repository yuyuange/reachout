#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 15:54:25 2024
aurointersection
@author: yuyuan
"""
import numpy as np
def _isInsideEllipsoid(point, a, b):
    x,y,z = point
    return (x/a)**2 + (y/a)**2 + (z/b)**2 < 1
def _closestDistance(d1, d2):
    """
    Assuming a single line origin, this returns the distances (either d1 or d2)
    whose absolute values are smallest.
    """
    with np.errstate(invalid='ignore'):
        dMin = np.where(np.abs(d1) < np.abs(d2), d1, d2)
    return dMin
def _filterPointsOutsideDirectedLine(d):
    if d.ndim == 0:
        d = np.array(np.nan) if d < 0 else d
    else:
        with np.errstate(invalid='ignore'):
            d[d<0] = np.nan
    return d

def ellipsoidLineIntersection(a, b, lineOrigin, lineDirection, directed=True):
      lineOrigin = np.require(lineOrigin, dtype=np.float64)
      lineDirection = np.require(lineDirection, dtype=np.float64)
      
      # turn into column vectors
      direction = lineDirection.T
      origin = -lineOrigin[:,None]
      
      radius = np.array([[1/a], [1/a], [1/b]])
      directionTimesRadius = direction * radius
      originTimesRadius = origin * radius
      
      # einsum is a bit faster for calculating the element-wise dot product
      # equivalent to np.sum(x*y, axis=0) or inner1d(x.T, y.T)
      directionDotOrigin = np.einsum("ij,ij->j", directionTimesRadius, originTimesRadius)
      directionDotDirection = np.einsum("ij,ij->j", directionTimesRadius, directionTimesRadius)
      originDotOrigin = np.einsum("ij,ij->j", originTimesRadius, originTimesRadius)
    
      rootTerm = np.square(directionDotOrigin)
      rootTerm -= originDotOrigin*directionDotDirection
      rootTerm += directionDotDirection
      with np.errstate(invalid='ignore'): # ignore warnings for negative numbers (= no intersection)
          np.sqrt(rootTerm, rootTerm)
      root = rootTerm
    
      if directed:
          if _isInsideEllipsoid(lineOrigin, a, b):
              d2 = directionDotOrigin
              d2 += root
              dMin = d2
          else:
              d1 = directionDotOrigin
              d1 -= root
              dMin = d1
          dMin = _filterPointsOutsideDirectedLine(dMin)
      else:
          d1 = directionDotOrigin - root
          d2 = directionDotOrigin
          d2 += root
          dMin = _closestDistance(d1, d2)
      
      dMin /= directionDotDirection
      
      res = directionTimesRadius
      np.multiply(direction, dMin, res)
      res -= origin
      return res.T

def ellipsoidLineIntersects(a, b, lineOrigin, lineDirection, directed=True):
    lineOrigin = np.require(lineOrigin, dtype=np.float64)
    lineDirection = np.require(lineDirection, dtype=np.float64)
    
    # turn into column vectors
    direction = lineDirection.T
    origin = -lineOrigin[:,None]
    
    radius = np.array([[1/a], [1/a], [1/b]])
        
    directionTimesRadius = direction * radius
    originTimesRadius = origin * radius
    directionDotOrigin = np.einsum("ij,ij->j", directionTimesRadius, originTimesRadius)
    directionDotDirection = np.einsum("ij,ij->j", directionTimesRadius, directionTimesRadius)
    originDotOrigin = np.einsum("ij,ij->j", originTimesRadius, originTimesRadius)

    rootTerm = np.square(directionDotOrigin)
    rootTerm -= originDotOrigin*directionDotDirection
    rootTerm += directionDotDirection
    
    with np.errstate(invalid='ignore'): # ignore warnings for negative numbers (= no intersection)
        if directed:
            np.sqrt(rootTerm, rootTerm)
            root = rootTerm
            if _isInsideEllipsoid(lineOrigin, a, b):
                d2 = directionDotOrigin
                d2 += root
                dMin = d2
            else:
                d1 = directionDotOrigin
                d1 -= root
                dMin = d1
            intersects = dMin >= 0
        else:
            intersects = rootTerm >= 0
    
    return intersects
