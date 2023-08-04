# -*- coding: utf-8 -*-
"""
Created on Sat Aug  5 03:06:49 2023

@author: Administrator
"""

import math
from math import pow
import numpy as np
from scipy.optimize import least_squares

# =============================================================================
# Create functions for WiFi Positioning

# Simplified path loss model
def calc_dist(rssi,a,n):
    cal_d= pow(10,((rssi-a)/(-10*n)))
    return cal_d

# Calculate distance error
def dist_error_2d(x1,y1,x2,y2):  
    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)  
    return dist 

# Least square algorithm for indoor positioning
def trilaterate(distances, positions):
  def residuals(x, distances, positions):
    residuals = []
    for i in range(len(distances)):
      residuals.append(np.linalg.norm(x - positions[i]) - distances[i])
    return residuals
  
  initial_guess = np.mean(positions, axis=0)
  result = least_squares(residuals, initial_guess, args=(distances, positions))
  return result.x

# 2D trilateration algorithm 
def trilateration_2d_co(distances, positions, name):
    # Calculate the position of the object
    position = trilaterate(distances, positions)
    
    final = [name, position[0], position[1]]
    return final

# 3D trilateration algorithm
def trilateration_3d_co(distances, positions, name):
    # Calculate the position of the object
    position = trilaterate(distances, positions)

    final = [name, position[0], position[1], position[2]]
    return final