from wisepaasdatahubedgesdk.EdgeAgent import EdgeAgent
import wisepaasdatahubedgesdk.Common.Constants as constant
from wisepaasdatahubedgesdk.Model.Edge import EdgeAgentOptions, MQTTOptions, DCCSOptions, EdgeData, EdgeTag, EdgeStatus, EdgeDeviceStatus, EdgeConfig, NodeConfig, DeviceConfig, AnalogTagConfig, DiscreteTagConfig, TextTagConfig
from wisepaasdatahubedgesdk.Common.Utils import RepeatedTimer
import time
import datetime
nodeID="37052693-fccf-4a43-b9e8-f3b89d2a69a3"
apiURL="https://api-dccs-ensaas.education.wise-paas.com/"
CredentialKEY="6f4c4b5d89db8cc94fd1402b3c970eom"
edgeAgentOptions = EdgeAgentOptions(nodeId = nodeID)#nodeID
edgeAgentOptions.connectType = constant.ConnectType['DCCS']
dccsOptions = DCCSOptions(apiUrl = apiURL, credentialKey = CredentialKEY)
edgeAgentOptions.DCCS = dccsOptions
_edgeAgent = EdgeAgent(edgeAgentOptions)
_edgeAgent.connect()

import pymongo
import pandas as pd
myclient = pymongo.MongoClient("140.118.70.38",27017)
mydb = myclient["WiFi_Dashboard_Data"]
mycol = mydb["Int_Coordinate"]

data = pd.DataFrame(list(mycol.find().sort('_id',-1).limit(1)))
data['DatetimeStr'][0]
data = pd.DataFrame(list(mycol.find({'DatetimeStr':data['DatetimeStr'][0]}).sort('_id',-1)))
data = data.reset_index(drop=True).drop_duplicates().drop(columns=['_id'], axis=0)
data["x3"] = data['x3'].apply(lambda x: x*100)
data["y3"] = data['y3'].apply(lambda x: x*100)

df = data[['floor','essid','x3','y3']]
df['essid'].fillna('?', inplace=True)

fl = {}
for i in range(10):
    fl[i] = df[(df['floor'] == '{}F'.format(i+1))].reset_index(drop=True).drop_duplicates()
    for j in range(20 - len(fl[i])):
        fl[i].loc[len(fl[i])] = [-9999, -9999, -9999, -9999]

#creat data connect

def creatdataconnect(_edgeAgent):
    config = __generateConfig()
    _edgeAgent.uploadConfig(action = constant.ActionType['Create'], edgeConfig = config)
def updateconfig(_edgeAgent):
    config = __generateConfig()
    _edgeAgent.uploadConfig(action = constant.ActionType['Update'], edgeConfig = config)

def __generateConfig():
    config = EdgeConfig()
    nodeConfig = NodeConfig(nodeType = constant.EdgeType['Gateway'])
    config.node = nodeConfig
    for i in range(10):
        deviceConfig = DeviceConfig(id = 'Floor'+str(i+1),
          name = 'Floor'+str(i+1),
          description = 'Floor'+str(i+1),
          deviceType = 'Smart Device',
          retentionPolicyName = '')
        for j in range(20):
            analog = AnalogTagConfig(name = 'x'+str(j+1),
                description = str(j+1)+ 'x',
                readOnly = False,
                arraySize = 0,
                spanHigh = 1000,
                spanLow = 0,
                engineerUnit = '',
                integerDisplayFormat = 4,
                fractionDisplayFormat = 2)
            deviceConfig.analogTagList.append(analog)
        for j in range(20):
            analog = AnalogTagConfig(name = 'y'+str(j+1),
                description = str(j+1) + 'y',
                readOnly = False,
                arraySize = 0,
                spanHigh = 1000,
                spanLow = 0,
                engineerUnit = '',
                integerDisplayFormat = 4,
                fractionDisplayFormat = 2)
            deviceConfig.analogTagList.append(analog)  
        for j in range(20):
            textTag = TextTagConfig(name = 'AP'+str(j+1),
                description = str(j+1) + 'AP',
                readOnly = False,
                arraySize = 0)
            deviceConfig.textTagList.append(textTag)      
            
        config.node.deviceList.append(deviceConfig)
    
    return config 
def __generateData():
    import pymongo
    import pandas as pd
    myclient = pymongo.MongoClient("140.118.70.38",27017)
    mydb = myclient["WiFi_Dashboard_Data"]
    mycol = mydb["Int_Coordinate"]

    data = pd.DataFrame(list(mycol.find().sort('_id',-1).limit(1)))
    data['DatetimeStr'][0]
    data = pd.DataFrame(list(mycol.find({'DatetimeStr':data['DatetimeStr'][0]}).sort('_id',-1)))
    data = data.reset_index(drop=True).drop_duplicates().drop(columns=['_id'], axis=0)
    data["x3"] = data['x3'].apply(lambda x: x*100)
    data["y3"] = data['y3'].apply(lambda x: x*100)

    df = data[['floor','essid','x3','y3']]
    df['essid'].fillna('?', inplace=True)

    fl = {}
    for i in range(10):
        fl[i] = df[(df['floor'] == '{}F'.format(i+1))].reset_index(drop=True).drop_duplicates()
        for j in range(20 - len(fl[i])):
            fl[i].loc[len(fl[i])] = [-9999, -9999, -9999, -9999]
    edgeData = EdgeData()
    for i in range(10):
      for j in range(20):
          deviceId = 'Floor'+str(i+1)
          tagName = 'x'+str(j+1)
          value = fl[i]['x3'][j]
          
          tag = EdgeTag(deviceId, tagName, value)
          edgeData.tagList.append(tag)
      for j in range(20):
          deviceId = 'Floor'+str(i+1)
          tagName = 'y'+str(j+1)
          value = fl[i]['y3'][j]
              
          tag = EdgeTag(deviceId, tagName, value)
          edgeData.tagList.append(tag)
      for j in range(20):
          deviceId = 'Floor'+str(i+1)
          tagName = 'AP'+str(j+1)
          value = fl[i]['essid'][j]
          tag = EdgeTag(deviceId, tagName, value)
          edgeData.tagList.append(tag)

    edgeData.timestamp = datetime.datetime.now()
    return edgeData
def senddata(_edgeAgent):
     data = __generateData()
     _edgeAgent.sendData(data)

def __generateDelteDeviceConfig():
      config = EdgeConfig()
      nodeConfig = NodeConfig()
      config.node = nodeConfig
      for i in range(11):
        deviceConfig = DeviceConfig(id = 'Floor' + str(i+1))
        config.node.deviceList.append(deviceConfig)
      return config
def delet(_edgeAgent):
    config=__generateDelteDeviceConfig()
    _edgeAgent.uploadConfig(action = constant.ActionType['Delete'], edgeConfig = config)
    
### Delete - Create - Update SDK setting. You can only run one in a time (Delete or Create or Update)

## Delete setting
#delet(_edgeAgent)

## Create setting
#creatdataconnect(_edgeAgent)   #creatconnect
#_edgeAgent.disconnect()

## Update setting
updateconfig(_edgeAgent)
while(1):
    try:
        senddata(_edgeAgent)
        # Set update interval = 5 mins
        time.sleep(1)
    except:
        time.sleep(1)
print('Done!')