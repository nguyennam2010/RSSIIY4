# -*- coding: utf-8 -*-
"""
Created on Thu Nov  3 16:16:14 2022

@author: Administrator
"""

import pandas as pd
import requests
import warnings
import time
# from time import sleep
from bs4 import BeautifulSoup
import json
import datetime
import numpy as np
import pymongo
from pymongo import MongoClient
import re
from datetime import datetime, timedelta

# =============================================================================

# MongoDB Database & Collection

Database=DATABASE
Collections=COLLECTION

# =============================================================================

# Aruba API account & password

account = ACCOUNT
password = PASSWORD

# =============================================================================


Controller_url=CONTROLLERURL

# Avoid warning

warnings.filterwarnings('ignore') 
path = 'data.txt'
# =============================================================================

# auto login and get cookie

url = Controller_url+'/screens/wms/wms.login'
headers = {'Content-Type': 'text/html','User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
chartData = 'opcode=login&url=%2Flogin.html&needxml=0&uid='+account+'&passwd='+password
res_data = requests.post(url, verify=False, headers = headers, data = chartData.encode('utf-8'))
cookieStr = res_data.cookies['SESSION']

# =============================================================================

################################ DASHBOARD DATA ###############################

# =============================================================================
# =============================================================================

# Retrieve and parse AP data

url = Controller_url+'/screens/cmnutil/execUiQuery.xml'
headers = {'Content-Type': 'text/plain'}
cookie = {"SESSION": cookieStr}
payloadData = 'query=<aruba_queries><query><qname>backend-observer-radio-65</qname><type>list</type><list_query><device_type>radio</device_type><requested_columns>ap_name radio_band channel_str radio_mode total_data_bytes eirp_10x max_eirp noise_floor arm_ch_qual sta_count current_channel_utilization rx_time tx_time channel_interference channel_free channel_busy avg_data_rate tx_avg_data_rate rx_avg_data_rate ap_quality</requested_columns><sort_by_field>ap_name</sort_by_field><sort_order>asc</sort_order><pagination><start_row>0</start_row><num_rows>1020</num_rows></pagination></list_query></query></aruba_queries>&UIDARUBA='+cookieStr

res = requests.post(url, verify=False, headers=headers,
                    cookies=cookie, data=payloadData.encode('utf-8'))

soup = BeautifulSoup(res.text, 'html.parser')
header_tags = soup.find_all('header')
row_tags = soup.find_all('row')


# =============================================================================

# Rearrange DataFrame: put into df[]

df = pd.DataFrame()
index = 0

row_tags[0]
for values in row_tags:

    data = values.find_all('value')
    data_total = []

    time_stamp = int(time.time())
    struct_time = time.localtime(time_stamp)
    timeString = time.strftime("%Y-%m-%d-%H-%M", struct_time)
    data_total.append(time_stamp)

    for i in range(len(data)):

        data_total.append(data[i].text)

    index += 1
    df[index] = data_total


# =============================================================================

# Add header to dataframe: put into df[]

for values in header_tags:
    AP1_Data = []
    AP1_Data.append('time_stamp')
    column_name = values.find_all('column_name')
    for i in range(len(column_name)):
        AP1_Data.append(column_name[i].text)

df.index = AP1_Data
df = df.T
df.reset_index(drop=True, inplace=True)
df.reset_index(drop=True, inplace=True)
# df = df[['ap_name','sta_count','ap_ip_address','ap_eth_mac_address','ap_status','ap_deployment_mode','ap_model','ap_group']]


# ===================================================================================

# when 'noise_floor' is null, decide whether it should crawl the specific data again

# def function recall(i): detect that [noise_floor][i] is missing, crawl the missing data again
# recall(i) return df_2, which put all accurate data in it

def recall(i):
    global account, password, Controller_url
    try:
        url = Controller_url+'/screens/wms/wms.login'
        headers = {'Content-Type': 'text/html',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
        chartData = 'opcode=login&url=%2Flogin.html&needxml=0&uid='+account+'&passwd='+password
        res_data = requests.post(
            url, verify=False, headers=headers, data=chartData.encode('utf-8'))
        cookieStr = res_data.cookies['SESSION']
        url = Controller_url+'/screens/cmnutil/execUiQuery.xml'
        headers = {'Content-Type': 'text/plain'}
        cookie = {"SESSION": cookieStr}
        payloadData = 'query=<aruba_queries><query><qname>backend-observer-radio-65</qname><type>list</type><list_query><device_type>radio</device_type><requested_columns>ap_name radio_band channel_str radio_mode total_data_bytes eirp_10x max_eirp noise_floor arm_ch_qual sta_count current_channel_utilization rx_time tx_time channel_interference channel_free channel_busy avg_data_rate tx_avg_data_rate rx_avg_data_rate ap_quality</requested_columns><sort_by_field>ap_name</sort_by_field><sort_order>asc</sort_order><pagination><start_row>' + \
            str(i) + '</start_row><num_rows>1</num_rows></pagination></list_query></query></aruba_queries>&UIDARUBA='+cookieStr
        res = requests.post(url, verify=False, headers=headers,
                            cookies=cookie, data=payloadData.encode('utf-8'))
        soup = BeautifulSoup(res.text, 'html.parser')
        header_tags = soup.find_all('header')
        row_tags = soup.find_all('row')

        df_2 = pd.DataFrame()
        index = 0

        for values in row_tags:
            data = values.find_all('value')
            data_total = []
            time_stamp = int(time.time())
            struct_time = time.localtime(time_stamp)
            timeString = time.strftime("%Y-%m-%d-%H-%M", struct_time)
            data_total.append(time_stamp)

            for j in range(len(data)):
                data_total.append(data[j].text)
            df_2[index] = data_total

        for values in header_tags:
            AP2_Data = []
            AP2_Data.append('time_stamp')
            column_name = values.find_all('column_name')
            for i in range(len(column_name)):
                AP2_Data.append(column_name[i].text)

        df_2.index = AP2_Data
        df_2 = df_2.T
        df_2.reset_index(drop=True, inplace=True)

        return df_2
    except:
        print('error')
        df_2 = pd.DataFrame()
        return df_2

# put df_2 into the original data array df, substitute the error data


for i in range(len(df)):
    f = 0
    while (df['noise_floor'][i] == '' and f <= 2):
        f = f+1
        df_2 = recall(i)

        if (not df_2.empty):
            df['time_stamp'][i] = df_2['time_stamp'][0]
            df['noise_floor'][i] = df_2['noise_floor'][0]
            df['ap_name'][i] = df_2['ap_name'][0]
            df['radio_band'][i] = df_2['radio_band'][0]
            df['total_data_bytes'][i] = df_2['total_data_bytes'][0]
            df['avg_data_rate'][i] = df_2['avg_data_rate'][0]
            df['tx_avg_data_rate'][i] = df_2['tx_avg_data_rate'][0]
            df['rx_avg_data_rate'][i] = df_2['rx_avg_data_rate'][0]
            df['channel_str'][i] = df_2['channel_str'][0]
            df['radio_mode'][i] = df_2['radio_mode'][0]
            df['eirp_10x'][i] = df_2['eirp_10x'][0]
            df['max_eirp'][i] = df_2['max_eirp'][0]
            df['arm_ch_qual'][i] = df_2['arm_ch_qual'][0]
            df['sta_count'][i] = df_2['sta_count'][0]
            df['current_channel_utilization'][i] = df_2['current_channel_utilization'][0]
            df['rx_time'][i] = df_2['rx_time'][0]
            df['tx_time'][i] = df_2['tx_time'][0]
            df['channel_interference'][i] = df_2['channel_interference'][0]
            df['channel_free'][i] = df_2['channel_free'][0]
            df['channel_busy'][i] = df_2['channel_busy'][0]

# =============================================================================

# data type transfer: str => int, xxxx/60000 => decimal point

df['sta_count_all'] = df['sta_count']
for i in range(len(df)):
    try:
        df['rx_time'][i] = int(re.findall(
            "([0-9]+)\/", df['rx_time'][i])[0])/60000
    except Exception:
        df['rx_time'][i] = 0
    try:
        df['tx_time'][i] = int(re.findall(
            "([0-9]+)\/", df['tx_time'][i])[0])/60000
    except Exception:
        df['tx_time'][i] = 0
    try:
        df['channel_interference'][i] = int(re.findall(
            "([0-9]+)\/", df['channel_interference'][i])[0])/60000
    except Exception:
        df['channel_interference'][i] = 0
    try:
        df['channel_free'][i] = int(re.findall(
            "([0-9]+)\/", df['channel_free'][i])[0])/60000
    except Exception:
        df['channel_free'][i] = 0
    try:
        df['channel_busy'][i] = int(re.findall(
            "([0-9]+)\/", df['channel_busy'][i])[0])/60000
    except Exception:
        df['channel_busy'][i] = 0
    try:
        df['total_data_bytes'][i] = int(df['total_data_bytes'][i])
    except Exception:
        df['total_data_bytes'][i] = 0
    try:
        df['noise_floor'][i] = int(df['noise_floor'][i])
    except Exception:
        df['noise_floor'][i] = 0
    try:
        df['eirp_10x'][i] = int(df['eirp_10x'][i])
    except Exception:
        df['eirp_10x'][i] = 0
    try:
        df['max_eirp'][i] = int(df['max_eirp'][i])
    except Exception:
        df['max_eirp'][i] = 0
    try:
        df['arm_ch_qual'][i] = int(df['arm_ch_qual'][i])
    except Exception:
        df['arm_ch_qual'][i] = 0
    try:
        df['sta_count'][i] = int(df['sta_count'][i])
    except Exception:
        df['sta_count'][i] = 0
    try:
        df['avg_data_rate'][i] = int(df['avg_data_rate'][i])
    except Exception:
        df['avg_data_rate'][i] = 0
    try:
        df['tx_avg_data_rate'][i] = int(df['tx_avg_data_rate'][i])
    except Exception:
        df['tx_avg_data_rate'][i] = 0
    try:
        df['rx_avg_data_rate'][i] = int(df['rx_avg_data_rate'][i])
    except Exception:
        df['rx_avg_data_rate'][i] = 0
    try:
        df['ap_quality'][i] = int(df['ap_quality'][i])
    except Exception:
        df['ap_quality'][i] = 0
    try:
        df['radio_mode'][i] = int(df['radio_mode'][i])
    except Exception:
        df['radio_mode'][i] = 0

# Add total client number

    for i in range(len(df) - 1):
        if df['ap_name'][i] == df['ap_name'][i+1]:
            df['sta_count_all'][i] = int(
                df['sta_count'][i]) + int(df['sta_count'][i+1])
            df['sta_count_all'][i+1] = df['sta_count_all'][i]


# =============================================================================

# Add datetime (GMT +8) and timestamp


ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
ts = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fz")
ts
n = 8

# Subtract 8 hours from datetime object

ts = ts - timedelta(hours=n)
ts_tw_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
ts_tw = datetime.now()


# =============================================================================

# create json: df[] => data_json

df = df[df['ap_name'].str.contains('IY')]
df = df[['ap_name','radio_band','noise_floor','rx_time','tx_time','channel_interference','channel_free','sta_count']]

data_json = json.loads(df.to_json(orient='records'))

for i in range(len(data_json)):
    data_json[i]['ts'] = ts
    data_json[i]['DatetimeStr'] = ts_tw_str
    data_json[i]['Datetime'] = ts_tw
    data_json[i]['radio_band'] = int(data_json[i]['radio_band'])
# Store json data to MongoDB
from bson.objectid import ObjectId
from datetime import datetime, timedelta

previous_day = datetime.now() - timedelta(days=1) 

client = MongoClient(MONGOIP,27017)
db = client[DASHBOARDDB]
col=db[RADIOCOLLECTION]
# col.delete_many({"Datetime": {"$lt": previous_day}})
#col.delete_many({})
col.insert_many(data_json)


# =============================================================================

################################ AP DATA ######################################

# =============================================================================

# Retrieve and parse AP data

url = Controller_url+'/screens/cmnutil/execUiQuery.xml'
headers = {'Content-Type': 'text/plain'}
cookie = {"SESSION":cookieStr}
payloadData = 'query=<aruba_queries><query><qname>backend-observer-ap-42</qname><type>list</type><list_query><device_type>ap</device_type><requested_columns>ap_name ap_eth_mac_address ap_group ap_deployment_mode ap_model ap_serial_number ap_ip_address ap_status ap_state_reason ap_provisioned ap_uptime lms_ip ap_active_aac ap_standby_aac ap_cluster_name ap_cur_dual_5g_mode ap_tri_radio_mode radio_count total_data_bytes sta_count ssid_count ap_datazone role pcap_on green_state mesh_role mesh_cluster_name mesh_portal_ap_mac mesh_portal_name mesh_parent_ap_mac mesh_parent_name mesh_uplink_time mesh_uplink_age mesh_child_num</requested_columns><sort_by_field>sta_count</sort_by_field><sort_order>desc</sort_order><pagination><start_row>0</start_row><num_rows>200</num_rows></pagination></list_query><filter><global_operator>and</global_operator><filter_list><filter_item_entry><field_name>ap_status</field_name><comp_operator>equals</comp_operator><value><![CDATA[1]]></value></filter_item_entry><filter_item_entry><field_name>role</field_name><comp_operator>equals</comp_operator><value><![CDATA[1]]></value></filter_item_entry></filter_list></filter></query></aruba_queries>&UIDARUBA='+cookieStr

res = requests.post(url, verify=False, headers = headers, cookies = cookie, data = payloadData.encode('utf-8'))

soup = BeautifulSoup(res.text, 'html.parser')
header_tags = soup.find_all('header')
row_tags=soup.find_all('row')




# =============================================================================

# Rearrange DataFrame

df=pd.DataFrame()
index=0

for values in row_tags:
    
    data=values.find_all('value')
    data_total=[]
    
    time_stamp =int(time.time())
    struct_time = time.localtime(time_stamp) 
    timeString = time.strftime("%Y-%m-%d-%H-%M", struct_time) 
    data_total.append(time_stamp)

    for i in range(len(data)):

        data_total.append(data[i].text)
        
    index+=1
    df[index]=data_total


# =============================================================================

# Add header to dataframe

for values in header_tags:
    Header_Data=[] 
    Header_Data.append('time_stamp')
    column_name=values.find_all('column_name')
    for i in range(len(column_name)) :
        Header_Data.append(column_name[i].text)


df.index=Header_Data
df=df.T
df.reset_index(drop=True, inplace=True)
df = df[df['ap_name'].str.contains('IY')]
df = df[['ap_name','sta_count','ap_ip_address','ap_eth_mac_address','ap_status','ap_deployment_mode','ap_model','ap_group']]
df1 = df
# =============================================================================

# Add datetime (GMT +8) and timestamp

import datetime
from datetime import timedelta

ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
ts = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fz")
ts
n = 8
# Subtract 8 hours from datetime object
ts = ts - timedelta(hours=n)
ts_tw_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
ts_tw = datetime.datetime.now()


# =============================================================================

# create json

data_json = json.loads(df.to_json(orient='records'))

for i in range(len(data_json)):
    try:
        data_json[i]['sta_count'] = int(data_json[i]['sta_count'])
        data_json[i]['ap_status'] = int(data_json[i]['ap_status'])
        data_json[i]['ap_provisioned'] = int(data_json[i]['ap_provisioned'])
        data_json[i]['ap_uptime'] = int(data_json[i]['ap_uptime'])
        data_json[i]['ap_deployment_mode'] = int(data_json[i]['ap_deployment_mode'])
        data_json[i]['ap_model'] = int(data_json[i]['ap_model'])
    except Exception:
        pass
    data_json[i]['ts'] = ts 
    data_json[i]['DatetimeStr'] = ts_tw_str
    data_json[i]['Datetime'] = ts_tw
data_json[1]
    
# =============================================================================

# Store json data to MongoDB

from bson.objectid import ObjectId
from datetime import datetime, timedelta

previous_day = datetime.now() - timedelta(days=1)

client = MongoClient(MONGODBIP,27017)
db = client[APDB]
col=db[APCOLLECTION]
col.delete_many({"Datetime": {"$lt": previous_day}})
col.insert_many(data_json)

# =============================================================================

################################ CLIENT DATA ##################################

# =============================================================================

# Retrieve and parse AP data

url = Controller_url+'/screens/cmnutil/execUiQuery.xml'
headers = {'Content-Type': 'text/plain'}
cookie = {"SESSION":cookieStr}
payloadData = 'query=<aruba_queries><query><qname>backend-observer-sta-17</qname><type>list</type><list_query><device_type>sta</device_type><requested_columns>sta_mac_address client_ht_phy_type openflow_state client_ip_address client_user_name client_dev_type client_ap_location client_conn_port client_conn_type client_timestamp client_role_name client_active_uac client_standby_uac ap_cluster_name client_health total_moves successful_moves steer_capability ssid ap_name channel channel_str channel_busy tx_time rx_time channel_free channel_interference current_channel_utilization radio_band bssid speed max_negotiated_rate noise_floor radio_ht_phy_type snr total_data_frames total_data_bytes avg_data_rate tx_avg_data_rate rx_avg_data_rate tx_frames_transmitted tx_frames_dropped tx_bytes_transmitted tx_bytes_dropped tx_time_transmitted tx_time_dropped tx_data_transmitted tx_data_dropped tx_data_retried tx_data_transmitted_retried tx_data_bytes_transmitted tx_abs_data_bytes tx_data_bytes_dropped tx_time_data_transmitted tx_time_data_dropped tx_mgmt rx_frames rx_bytes rx_data rx_data_bytes rx_abs_data_bytes rx_data_retried tx_data_frame_rate_dist rx_data_frame_rate_dist tx_data_bytes_rate_dist rx_data_bytes_rate_dist connection_type_classification total_data_throughput tx_data_throughput rx_data_throughput client_auth_type client_auth_subtype client_encrypt_type client_fwd_mode</requested_columns><sort_by_field>client_user_name</sort_by_field><sort_order>desc</sort_order><pagination><start_row>0</start_row><num_rows>200</num_rows></pagination></list_query><filter><global_operator>and</global_operator><filter_list><filter_item_entry><field_name>client_conn_type</field_name><comp_operator>not_equals</comp_operator><value><![CDATA[0]]></value></filter_item_entry></filter_list></filter></query></aruba_queries>&UIDARUBA='+cookieStr
res = requests.post(url, verify=False, headers = headers, cookies = cookie, data = payloadData.encode('utf-8'))
soup = BeautifulSoup(res.text, 'html.parser')
header_tags = soup.find_all('header')

row_tags=soup.find_all('row')

# =============================================================================

# Rearrange DataFrame

df=pd.DataFrame()
index=0
for values in row_tags:
    
    data=values.find_all('value')
    data_total=[]
    
    time_stamp =int(time.time())
    struct_time = time.localtime(time_stamp)
    timeString = time.strftime("%Y-%m-%d-%H-%M", struct_time)
    data_total.append(time_stamp)

    for i in range(len(data)):

        data_total.append(data[i].text)
        
    index+=1
    df[index]=data_total

for values in header_tags:
    Client_Data=[] 
    Client_Data.append('time_stamp')
    column_name=values.find_all('column_name')
    for i in range(len(column_name)) :
        #print(column_name[i].text)
        Client_Data.append(column_name[i].text)


df.index=Client_Data
df=df.T
df=df.sort_values(by=['ap_name'])
df.reset_index(drop=True, inplace=True)

df = df[df['ap_name'].str.contains('IY')]
df[['client_user_name','sta_mac_address','client_ip_address','client_dev_type','ssid','ap_name','client_health','radio_band','channel','snr']]
df3 = df
# =============================================================================

# Add datetime (GMT +8) and timestamp

# import datetime
# from datetime import timedelta

# ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
# ts = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fz")
# ts
# n = 8
# # Subtract 8 hours from datetime object
# ts = ts - timedelta(hours=n)
# ts_tw_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# ts_tw = datetime.datetime.now()

# =============================================================================

# create json

data_json = json.loads(df.to_json(orient='records'))

for i in range(len(data_json)):
    data_json[i]['ts'] = ts
    data_json[i]['DatetimeStr'] = ts_tw_str
    data_json[i]['Datetime'] = ts_tw
    
data_json[1]
# =============================================================================

# Store json data to MongoDB

client = MongoClient(MONGOIP,27017)
db = client[CLIENTDB]
col=db[CLIENTCOLLECTION]
#col.delete_many({})
col.insert_many(data_json)


print('ok')
