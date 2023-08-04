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
import re
from bs4 import BeautifulSoup
import json
from pymongo import MongoClient
import datetime
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
    database = os.environ.get("RADATABASE")
    collection = os.environ.get("RACOLLECTION")

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

    # Add total client number

        for i in range(len(df) - 1):
            if df['ap_name'][i] == df['ap_name'][i+1]:
                df['sta_count_all'][i] = int(
                    df['sta_count'][i]) + int(df['sta_count'][i+1])
                df['sta_count_all'][i+1] = df['sta_count_all'][i]

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

    # =============================================================================

    # Store json data to MongoDB

    client = MongoClient(mongoip,27017)
    db = client[database]
    col=db[collection]
    col.insert_many(data_json)
    print('Done')

if __name__ == "__main__":
    main()