# Dashboard Development

After pushing MongoDB data to Dashboard, this is how you develop the Dashboard.

## Variables

Create variables for AP and floor.

![](https://i.imgur.com/XKiUE7M.png)

## AP information

- Query:

```
db.Controller_4.aggregate([
{"$sort":{"ts":-1, "Client":-1}},
{"$match": {"AP Name":"$ap", "ts":{ "$gte" : "$from"}}}, 
{"$project": {"_id":0,"AP Name":"$AP Name", "Client":"$Client","IP Address":"$IP address","MAC Address":"$MAC address","Model":"$Model","AP Group":"$AP_Group", "TW Time":"$DatetimeStr"}},
{"$limit":1}
            ])
```

- Result:

![image](https://github.com/nguyennam2010/RSSIIY3/assets/102983698/55efa9e8-41f9-4e58-a876-46f570d44df2)

## Client number

- Query (2.4 GHz):

```
db.AP_List.aggregate([
{"$match": {"ap_name":"$ap","radio_band": 0, "ts":{ "$gte" : "$from", "$lt":"$to"}}}, 
{"$project": {"_id":0, "name":"2.4 GHz", "ap_name":"$ap", "value":"$sta_count","ts":"$ts"}}
            ])
```

- Result:

![image](https://github.com/nguyennam2010/RSSIIY3/assets/102983698/babfa7fe-30de-4b7d-acd0-564213aa9d4d)

## Noise floor
- Query (5 GHz):

```
db.AP_List.aggregate([
{"$match": {"ap_name":"IY_1F_AP01","radio_band":1,  "ts":{ "$gte" : "$from", "$lt":"$to"}}}, 
{"$project": {"_id":0,"name":"5 GHz", "value":"$noise_floor","ts":"$ts"}}
            ])
```

- Result:

![image](https://github.com/nguyennam2010/RSSIIY3/assets/102983698/33a35dc8-3560-46ff-8581-f81b3bf77ccb)

## Channel utilization
- Query (2.4 GHz - tx time):

```
db.AP_List.aggregate([
{"$match": {"ap_name":"$ap","radio_band": 0, "ts":{ "$gte" : "$from", "$lt":"$to"}}}, 
{"$project": {"_id":0, "name":"tx time", "value":"$tx_time","ts":"$ts"}}
            ])
```
- Result:

![image](https://github.com/nguyennam2010/RSSIIY3/assets/102983698/c4b365b0-f367-4c87-a588-3f3a167cd6fd)

## Client information

- Query:

```
db.Controller_4.aggregate([
{"$sort":{"ts":-1, "Client":-1}},
{"$match": {"ap_name":"$ap", "ts":{ "$gte" : "$from", "$lt":"$to"}}}, 
{"$project": {"_id":0,"Client User Name":"$client_user_name", "MAC Address":"$sta_mac_address","IP Address":"$client_ip_address","OS":"$client_dev_type","WLAN":"$ssid","AP Name":"$ap","Client Health":"$client_health", "Radio Band":"$radio_band","Channel":"$channel","SNR":"$snr","TW Time":"$DatetimeStr"}},
{"$limit":100}
])
```

- Result:

![image](https://github.com/nguyennam2010/RSSIIY3/assets/102983698/5908236c-149a-472d-8939-8b7db00f1046)

## Client map

To visualize as map in Dashboard, you need to push your data to DataHub.

First, you need to download SDK code from [WISE-PaaS documentation](https://docs.wise-paas.advantech.com/en/Guides_and_API_References/Data_Acquisition/DataHub/py_Edge_SDK_Manual/v1.1.7)

Their code for random data generation:

![image](https://github.com/nguyennam2010/RSSIIY3/assets/102983698/443262a8-dd34-4d0b-86be-190200554063)

You need to adjust the above code to connect to DataHub. For example, push AP name and Client number from MongoDB:

![image](https://github.com/nguyennam2010/RSSIIY3/assets/102983698/f4f27158-849b-48bf-b3b4-61213de19cc1)

Then you can push the data to DataHub follow this video: https://www.youtube.com/watch?v=IP46vcWuHhY

Now you edit Composer to bind the data to the map. Create appropriate assets and bind the corresponding data from DataHub:

![image](https://github.com/nguyennam2010/RSSIIY3/assets/102983698/3ac22595-1fa0-413e-aa63-b7df8616b702)

Use advanced setting to change color of the Client nodes:

<img width="793" alt="image" src="https://github.com/nguyennam2010/RSSIIY3/assets/102983698/6e1e92bd-8ef8-45d3-9ac8-79a4294c33aa">

```
function(value, oldValue, option){ 
    if(value>=10) return "symbols/builtIn/large transformer/red light.json";
    if(value<10 & value>2) return "symbols/builtIn/large transformer/yellow light.json";
    if(value<=2) {value=0;return "symbols/builtIn/large transformer/green light.json";}
    else return "symbols/builtIn/large transformer/green light.json";}
```

- Now the map can show number of clients and color corresponding to the data.
    - Green light: < 2 users (clients)
    - Yellow light: 2 < users < 10
    - Red light: > 10 users

In Dashboard, choose SaaS Composer-Viewer and choose the SaaS Composer directory to the file setting:

<img width="955" alt="image" src="https://github.com/nguyennam2010/RSSIIY3/assets/102983698/917c5747-5441-42fd-9898-a75707fdf37d">

## Interference map

Same as Client map, you import the IY building map to SaaS Composer and bind their (x, y) variables.

<img width="793" alt="image" src="https://github.com/nguyennam2010/RSSIIY3/assets/102983698/941d11dd-4070-4cc0-9a94-4dc8087b946c">









