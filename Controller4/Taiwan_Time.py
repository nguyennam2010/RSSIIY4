# -*- coding: utf-8 -*-
"""
Created on Sat Aug  5 02:00:57 2023

@author: Administrator
"""

import requests
from datetime import timedelta
from datetime import datetime, timedelta
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
warnings.filterwarnings("ignore")

def calculate_taiwan_time():
    # =============================================================================
    # Add datetime (GMT +8)
    ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z") #datetime (GMT)
    ts = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fz")

    n = 8
    # Subtract 8 hours from datetime object for Taiwan time
    ts = ts - timedelta(hours=n)
    ts_tw_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ts_tw = datetime.now() #datetime Taiwan (GMT + 8)
    return ts, ts_tw_str, ts_tw
