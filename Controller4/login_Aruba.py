# -*- coding: utf-8 -*-
"""
Created on Thu Nov  3 16:16:14 2022

@author: Hoai-Nam
"""

import requests
import warnings

account = 'apiUser'
password = 'x564#kdHrtNb563abcde'
Controller_url='https://140.118.151.248:4343'

# Login Aruba function

def login(ACCOUNT, PASSWORD, CONTROLLERURL):

    # Avoid warning

    warnings.filterwarnings('ignore') 
    path = 'data.txt'
    # =============================================================================

    # auto login and get cookie

    url = CONTROLLERURL+'/screens/wms/wms.login'
    headers = {'Content-Type': 'text/html','User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
    chartData = 'opcode=login&url=%2Flogin.html&needxml=0&uid='+ACCOUNT+'&passwd='+PASSWORD
    res_data = requests.post(url, verify=False, headers = headers, data = chartData.encode('utf-8'))
    cookieStr = res_data.cookies['SESSION']
    return url, headers, chartData, res_data, cookieStr

login_result = login(account, password, Controller_url)

# =============================================================================

# Test result
