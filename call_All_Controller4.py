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
        exec(open("All_Controller4.py").read())
        end_time = time.time()
        total_time = round(end_time - start_time)
        print(total_time)
        time.sleep(300-total_time)
    except:
        time.sleep(150)
