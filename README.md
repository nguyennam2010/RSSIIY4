# Process and store data in Data Center's MongoDB
## Feature
To retrieve, process, and store WiFi data in MongoDB databases server in NTUST Data Center

## Requirement
- MongoDB > 3.4.x
## Directory

```

RSSIIY
|__ data
|  |__ (.csv files) #Leave it empty! the user should download the .csv files from Google drive manually.
|__ docs
|   |__ All_Controller4.html # pydoc file for All_Controller4.py
|   |__ Positioning_IY.html # pydoc file for Positioning_IY4.py
|   |__ Retrieve_RSSI.html # pydoc file for Retrieve_RSSI.py
|   |__ dashboard_development.md # Guide for dashboard development using WISE-PaaS
|__ Positioning_IY.py #  Estimate AP locations (WiFi Positioning)
|__ call_Positioning_IY.py # Auto-run the file Positioning_IY.py every 5 minutes
|__ All_Controller4.py # Retrieve AP and Client data from Aruba WiFi Controller
|__ call_All_Controller4.py # Auto-run the file All_Controller.py every 5 minutes
|__ Retrieve_RSSI.py # Retrieve RSSI data from Aruba WiFi Controller
|__ EdgeSDK_Client_Number.py # Connect client number to WISE-PaaS DataHub
|__ EdgeSDK_AP_Coordinate.py # Connect interfering/rogue APs coordinate axis (x, y) to WISE-PaaS DataHub
|__ .env.example #Configuration files with empty variables.
|__ README.md

```

## A. Access to Data Center's MongoDB databases server

### Access to Data Center Window server

- From Window, choose Remote Desktop Connection
- Enter Data Center IP address, username and password to connect to the server (Contact Victor to get the IP address, username and password).
![1](https://github.com/nguyennam2010/RSSIIY/assets/102983698/d2fd531e-75cf-47fd-8805-14296482c35c)


### Connect to MongoDB databases server

- To turn on auth server, open cmd and cd to
```
cd C:\Program Files\MongoDB\Server\3.6\bin
```
- Enter:
```
mongod --bind_ip_all
```
to listen to outside ip

![2](https://github.com/nguyennam2010/RSSIIY/assets/102983698/3e1ce288-c899-4d2f-b9dd-15753de21dad)


- Open Robo3T. We can now connect to MongoDB databases server

![3](https://github.com/nguyennam2010/RSSIIY/assets/102983698/0a9e6479-1e0c-4a64-bbd7-787715963edf)


## B. Auto-run python script 
- Open Spyder and run these 4 python scripts:
  - Run ```call_Positioning_IY.py``` to auto-run the file Positioning_IY.py every 5 minutes
  - Run ```call_All_Controller.py``` to auto-run the file All_Controller.py every 5 minutes
  - Run ```EdgeSDK_AP_Coordinate.py``` to connect interfering/rogue APs coordinate axis (x, y) to WISE-PaaS DataHub, in order to show rogue APs (x, y) axis to Dashboard
  - Run ```EdgeSDK_Client_Number.py``` to connect client number to WISE-PaaS DataHub (in order to show the number of clients in Dashboard).

## C. Query data from databases to WISE-PaaS

### Add MongoDB data source to Dashboard

- Open Dashboard -> Setting -> Data Source -> Add data source
- Choose MongoDB and enter:
    - Datasource Name (ex： Aruba_AP)
    - Enable TLS
    - API URL. We use GPU Server from BMW lab (ex: http://GPUSERVERIP:3333).
      - Info of our lab Server: https://hackmd.io/@jackychiang/SkZ-z-dU5
    - VM MongoDB URL （ex: mongodb://administrator:administrator@MONGOIP:27017)
    - MongoDB Database (ex: WiFi_AP_Data)

![4](https://github.com/nguyennam2010/RSSIIY/assets/102983698/f4cd6f4f-1f79-42cd-91cf-e16de26148e5)


### Display aruba AP data into Dashboard

- Create new dashboard, query to desired data source (ex: Aruba_AP)
- Insert appropriate aggregation. For example, we want to query AP data from WiFi_AP_Data:

```
db.Controller_4.aggregate([
{"$sort":{"ts":-1, "Client":-1}},
{"$match": { "ts":{ "$gte" : "$from"}}}, 
{"$project": {"AP Name":"$AP Name", "value":"$Client","ts":"$ts"}},
{"$limit":48}
            ])
```

- The result shows the AP and their client numbers:
![5](https://github.com/nguyennam2010/RSSIIY/assets/102983698/3de019e1-b311-4947-a3d6-0f30d90eaf58)


### Run mongodb-grafana API on background

1. Install foreverjs package (only install once) npm install forever -g
2. Go the the directory 
```
cd Desktop/mongodb-grafana/dist/server
```
3. Run API in background
```
forever start mongodb-proxy.js
```
4. Check API is running
```
forever list
```
5. Check API from browser
- http://you.ip.address.here:3333/
- If successful it will shows:
```
{"message":"Cannot read properties of undefined (reading 'url')"}
```
Sometimes, if GPU server shuts down due to power cutoff, you need to rerun the API. 
In this case, you only need to do the step from 2 to 5.

https://github.com/eric248550/mongodb-grafana#run-mongodb-grafana-api-on-background

## D. Demo video

https://youtu.be/wY7TLPMICaM


