# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 07:52:22 2023

@author: Hoai-Nam Nguyen
"""

import time
from datetime import datetime, timedelta
import threading

while (1):
    try:
        start_time = time.time()
        exec(open("Positioning_IY.py").read())
        #exec(open("Positioning_IY3D2.py").read())
        end_time = time.time()
        total_time = round(end_time - start_time)
        #print(total_time)
        print(end_time)
        time.sleep(400-total_time)
    except:
        time.sleep(400)
