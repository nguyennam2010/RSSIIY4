# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 19:48:59 2023

@author: Hoai-Nam Nguyen
"""

import time
from datetime import datetime, timedelta

script_1 = __import__("Process_RSSI")
script_2 = __import__("Positioning_IY")


while (1):
    try:
        start_time = time.time()
        print("Run script 1...")
        script_1.main()
        print("Run script 2...")
        script_2.main()
        end_time = time.time()
        total_time = round(end_time - start_time)
        print(total_time)
        time.sleep(300-total_time)
    except:
        time.sleep(150)