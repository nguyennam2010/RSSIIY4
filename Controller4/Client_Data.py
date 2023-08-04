# -*- coding: utf-8 -*-
"""
Created on Thu Nov  3 16:16:14 2022

@author: Hoai-Nam
"""

import login_Aruba
import os
from dotenv import load_dotenv
import pandas as pd
import requests
import time
# from time import sleep
from bs4 import BeautifulSoup
import json
import datetime
from pymongo import MongoClient
from datetime import timedelta

# Load variables from .env file
load_dotenv()

def main():
    # =============================================================================

    # Add datetime (GMT +8) and timestamp

    ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    ts = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fz")
    ts
    n = 8
    # Subtract 8 hours from datetime object
    ts = ts - timedelta(hours=n)
    ts_tw_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ts_tw = datetime.datetime.now()
    # =============================================================================
    
    # MongoDB Database & Collection

    mongoip = os.environ.get("MONGOIP")
    database = os.environ.get("CLDATABASE")
    collection = os.environ.get("CLCOLLECTION")

    # =============================================================================

    # Aruba API account & password

    account = os.environ.get("ACCOUNT")
    password = os.environ.get("PASSWORD")
    Controller_url = os.environ.get("CONTROLLER_URL")

    # =============================================================================

    # Login to Aruba

    url, headers, chartData, res_data, cookieStr = login_Aruba.login(account, password, Controller_url)

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

    # create json: df[] => data_json

    data_json = json.loads(df.to_json(orient='records'))

    for i in range(len(data_json)):
        data_json[i]['ts'] = ts
        data_json[i]['DatetimeStr'] = ts_tw_str
        data_json[i]['Datetime'] = ts_tw

    # =============================================================================

    # Store json data to MongoDB

    client = MongoClient(mongoip,27017)
    db = client[database]
    col=db[collection]
    col.insert_many(data_json)
    print('Done')

if __name__ == "__main__":
    main()