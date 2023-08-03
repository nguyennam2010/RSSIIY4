# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 00:02:25 2023
@author: Hoai-Nam Nguyen
"""

import requests
import json
import math
import pandas as pd 
from pymongo import MongoClient
from datetime import timedelta
from datetime import datetime, timedelta
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
warnings.filterwarnings("ignore")

# =============================================================================

# Add datetime (GMT +8)

ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z") #datetime (GMT)
ts = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fz")

n = 8
# Subtract 8 hours from datetime object for Taiwan time
ts = ts - timedelta(hours=n)
ts_tw_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
ts_tw = datetime.now() #datetime Taiwan (GMT + 8)

# Login to Aruba 
username= ACCOUNT # Aruba controller username
password= PASSWORD # Aruba controller password
vMM_aosip=AOSIP # Aruba controller IP address
MONGOIP = MONGOIP  # MongoDB IP address
ROGUEAPDB = ROGUEAPDB # RogueAP database
ROGUEAPCOLLECTION = ROGUEAPCOLLECTION # Coordinate collection

df = pd.read_excel('AP_name.xlsx')

# Create floor list
f = df['Floor'].tolist()

# Create CLI input ap-name list
IY = df.values.tolist()
IY = [[value for value in inner_list[1:] if not (isinstance(value, float) and math.isnan(value))] for inner_list in IY]


# =============================================================================

# Login controller functions

#Get the token to access vMM information  -- via API
def authentication(username,password,aosip):

    url_login = "https://" + aosip + ":4343/v1/api/login"
    payload_login = 'username=' + username + '&password=' + password
    headers = {'Content-Type': 'application/json'}
    get_uidaruba = requests.post(url_login, data=payload_login, headers=headers, verify=False)

    if get_uidaruba.status_code != 200:
        print('Status:', get_uidaruba.status_code, 'Headers:', get_uidaruba.headers,'Error Response:', get_uidaruba.reason)
        uidaruba = "error"

    else:
        uidaruba = get_uidaruba.json()["_global_result"]['UIDARUBA']
        return uidaruba

#Function to access show command API
def show_command(aosip,uidaruba,command):
    url_login = 'https://' + aosip + ':4343/v1/configuration/showcommand?command='+command+'&UIDARUBA=' + uidaruba
    aoscookie = dict(SESSION = uidaruba)
    AOS_response = requests.get(url_login, cookies=aoscookie, verify=False)

    if AOS_response.status_code != 200:
        print('Status:', AOS_response.status_code, 'Headers:', AOS_response.headers,'Error Response:', AOS_response.reason)
        AOS_response = 'error'

    else:
        AOS_response = AOS_response.json()

    return AOS_response

#Get the token to access vMM information  -- via API
token = authentication(username,password,vMM_aosip)

# Function to retrieve and process data from API

def main_loc(IY, floor):    
    df = {} # Initiate RSSI dataframe for a floor

    for ap in IY:
        command = 'show+ap+monitor+ap-list+ap-name+IY_'+ap # Run CLI command to retrieve RSSI data
        list_ap_database = show_command(vMM_aosip,token,command)
        df[ap] = pd.DataFrame(list_ap_database['Monitored AP Table'])
        df[ap]['curr-rssi'] = pd.to_numeric(df[ap]['curr-rssi'])
        df[ap] = df[ap][(df[ap]['ap-type']!='valid')][['essid','bssid','curr-rssi','ap-type', 'chan']]
        df[ap] = df[ap][(df[ap]['curr-rssi']>0)& (df[ap]['curr-rssi']<60)]

    try:
        ap1_int = df[IY[0]]['bssid']
    except Exception:
        ap1_int = None

    try:
        ap3_int = df[IY[1]]['bssid']
    except Exception:
        ap3_int = None

    try:
        ap5_int = df[IY[2]]['bssid']
    except Exception:
        ap5_int = None

    try:
        ap7_int = df[IY[3]]['bssid']
    except Exception:
        ap7_int = None

    try:
        ap9_int = df[IY[4]]['bssid']
    except Exception:
        ap9_int = None

    # Group all the interfering APs on a floor

    ap13_int = pd.concat([ap1_int,ap3_int]).reset_index(drop=True).drop_duplicates()
    try:
        ap57_int = pd.concat([ap5_int,ap7_int]).reset_index(drop=True).drop_duplicates()
        ap_all_int = pd.concat([ap13_int,ap57_int]).reset_index(drop=True).drop_duplicates()
        ap_all_int = pd.concat([ap_all_int,ap9_int]).reset_index(drop=True).drop_duplicates()
    except Exception:
        ap_all_int = ap1_int.reset_index(drop=True).drop_duplicates()
    ap_all = pd.DataFrame(ap_all_int).reset_index(drop=True)
    ap_all['essid'], ap_all['ap type'], ap_all['channel']= '','',''
    for i in range(len(ap)):
        try:
            ap_all[IY[i][-4:]] = None
        except Exception:
            pass
    ap_all['mon AP number'] = None

    for i in range(len(ap_all)):
        no_ap = 0

        for ap in IY:
            try:
            # Get essid
                ap_all['essid'][i] = list(df[ap][(df[ap]['bssid']==ap_all['bssid'][i])]['essid'])[0]
                ap_all['ap type'][i] = list(df[ap][(df[ap]['bssid']==ap_all['bssid'][i])]['ap-type'])[0]
                ap_all['channel'][i] = list(df[ap][(df[ap]['bssid']==ap_all['bssid'][i])]['chan'])[0]
            # Get rssi
                if df[ap]['bssid'].str.contains(ap_all['bssid'][i]).any():
                    ap_all[ap[-4:]][i] = -list(df[ap][df[ap]['bssid']==ap_all['bssid'][i]]['curr-rssi'])[0] 
                    no_ap+=1
            except Exception:
                pass
        ap_all['mon AP number'][i] = no_ap

    ap_all = ap_all[(ap_all['mon AP number']>0)].sort_values('essid').reset_index(drop=True).drop_duplicates()


    ap_all['xloc'], ap_all['yloc'], ap_all['floor'] = '', '', ''
    ap_all_int = ap_all['bssid']

    ap_all['floor'] = floor

    return ap_all

# =============================================================================

# Run code for every floor in IY

df0 = main_loc(IY[0], f[0])
try:
    df1 = main_loc(IY[1], f[1])
    dfa = df0.append(df1, ignore_index=True)
except Exception:
    pass
try:
    df2 = main_loc(IY[2], f[2])
    dfa = dfa.append(df2, ignore_index=True)
except Exception:
    pass
try:
    df3 = main_loc(IY[3], f[3])
    dfa = dfa.append(df3, ignore_index=True)
except Exception:
    pass
try:
    df4 = main_loc(IY[4], f[4])
    dfa = dfa.append(df4, ignore_index=True)
except Exception:
    pass
try:
    df5 = main_loc(IY[5], f[5])
    dfa = dfa.append(df5, ignore_index=True)
except Exception:
    pass
try:
    df6 = main_loc(IY[6], f[6])
    dfa = dfa.append(df6, ignore_index=True)
except Exception:
    pass
try:
    df7 = main_loc(IY[7], f[7])
    dfa = dfa.append(df7, ignore_index=True)
except Exception:
    pass
try:
    df8 = main_loc(IY[8], f[8])
    dfa = dfa.append(df8, ignore_index=True)
except Exception:
    pass
try:
    df9 = main_loc(IY[9], f[9])
    dfa = dfa.append(df9, ignore_index=True)
except Exception:
    pass
try:
    df10 = main_loc(IY[10], f[10])
    dfa = dfa.append(df10, ignore_index=True)
except Exception:
    pass

# =============================================================================

# Save as json format
data_json = json.loads(dfa.to_json(orient='records'))

# Add datetime
for i in range(len(data_json)):
    data_json[i]['ts'] = ts 
    data_json[i]['DatetimeStr'] = ts_tw_str
    data_json[i]['Datetime'] = ts_tw

# =============================================================================

# Store json data to MongoDB

client = MongoClient(MONGOIP,27017)
db = client[ROGUEAPDB]
col=db[ROGUEAPCOLLECTION]
## Set time to auto-delete MongoDB
#previous_day = datetime.now() - timedelta(days=30) 
# col.delete_many({"Datetime": {"$lt": previous_day}})
col.insert_many(data_json)
print('Done!')
dfa