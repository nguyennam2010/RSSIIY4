#Retrive and separate RSSI data to each rogue AP

import Show_Command
import requests
import pandas as pd 
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
warnings.filterwarnings("ignore")

# Function to retrieve and process RSSI data from API

def rss_retrieve(IY, floor, vMM_aosip,token):    
    df = {} # Initiate RSSI dataframe for a floor

    for ap in IY:
        command = 'show+ap+monitor+ap-list+ap-name+IY_'+ap # Run CLI command to retrieve RSSI data
        list_ap_database = Show_Command.show_command(vMM_aosip,token,command)
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