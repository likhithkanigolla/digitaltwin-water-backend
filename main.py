import asyncio
import threading
import time
import requests
import json
import xml.etree.ElementTree as ET
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 

from sensor import WaterFlowSensorDigitalTwin
from typing import List

# from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

import re

# _url= "http://onem2m.iiit.ac.in:443/~/in-cse/in-name/"
# _url= "http://localhost:2000/~/in-cse/in-name/"
_url= "http://10.3.1.117:8200/~/in-cse/in-name/"

_ae = "AE-DT/"
ack = []
soil_payload = {'1':0}
sand_payload = {'1':0}


nodeVal_temp = 0
nodeVal_utds = 0
nodeVal_ctds = 0
nodeVal_vol = 0



_node1 = "Node-1"
_node2 = "Node-2"
_node3 = "Node-3"

_desc = "/Descriptor/la/"
_ack = "/Acknowledgment/la/"
main_data = {}
main_desc = {}


payload = ""
headers = {
  "X-M2M-Origin": "admin:admin",
  "Content-Type": "application/json"
  }


# url1 = _url + _ae + _node1 + _desc
# url2 = _url + _ae + _node2 + _desc

sensor_node1 = WaterFlowSensorDigitalTwin(node_id= _node1)
sensor_node2 = WaterFlowSensorDigitalTwin(node_id= _node2)
sensor_node3 = WaterFlowSensorDigitalTwin(node_id= _node3)

print("Printing Sensor Node Details")
print(sensor_node1)
print(sensor_node2)
print(sensor_node3)

def desc_parser(xml_data):
    # Parse the XML-like data
    root = ET.fromstring(xml_data)
    
    # Initialize a dictionary to store the selected parsed data
    selected_data = {}
    
    # Iterate through the <str> elements
    for element in root.findall('.//str'):
        name = element.get('name')
        val = element.get('val')
        
        if name == "Node ID" or name == "Node Location":
            # Include only "Node ID" and "Node Location" in the result
            if name == "Node Location":
                # Parse the Node Location value as a dictionary and convert to the desired format
                location_dict = eval(val)  # Note: Be cautious when using eval in production code
                val = [location_dict['Latitude'], location_dict['Longitude']]
            
            selected_data[name] = val

            print("------------------------------------Val = ", val)

        elif name == "Data String Parameters":
            # Parse the Data String Parameters value as a list and exclude "timestamp"
            parameters_list = eval(val)  # Note: Be cautious when using eval in production code
            filtered_parameters = [param for param in parameters_list if param != "timestamp"]
            print(filtered_parameters)
            selected_data[name] = filtered_parameters
    
    # Convert the selected data dictionary to JSON format
    json_data = json.dumps(selected_data)
    
    return json_data

def get_desc(name):
    _URL = _url + _ae + name + _desc 
    response = requests.request("GET",_URL,headers=headers,data=payload)
    data = json.loads(response.text)
    # data = desc_parser(data["m2m:cin"]["con"])
   
    print("Descriptor Data:")
    data = data["m2m:cin"]["con"]
    print(data)
    # data = data
    match = re.search(r'Node Location: \[([\d., -]+)\]', data)
    if match:
        node_location = [float(coord) for coord in match.group(1).split(',')]
        print("Node Location:", node_location)
    else:
        print("Node location not found in the input string.")
    
    global val 
    val = {}
    val["Latitude"] = node_location[0]
    val["Longitude"] = node_location[1]
    print("val = ", val)
    main_desc[name] = data

def get_data(name):
    _URL = _url + _ae + name + "/Data/la"
    response = requests.request("GET",_URL,headers=headers,data=payload)
    data = json.loads(response.text)
    # data = eval(data["m2m:cin"]["con"])[1:]
    data = eval(data["m2m:cin"]["con"])
    print("Sensor Data:")
    print(data)
    # data = data
    main_data[name] = data



def update_data():
    while True:
        try:
            get_desc(_node1)
            get_desc(_node2)
            get_desc(_node3)
            
            get_data(_node1)
            get_data(_node2)
            get_data(_node3)

            # Update the digital twins with sensor data
            if _node1 in main_data and len(main_data[_node1]) > 2:
                sensor_node1.update(
                    temperature=main_data[_node1][0],  # Assuming the temperature is at index 0
                    u_tds=main_data[_node1][1],   # Assuming the u_tds is at index 1
                    c_tds=main_data[_node1][2],  # Assuming the total flow is at index 2
                    v_tds=main_data[_node1][3]  # Assuming the total flow is at index 2
                )
            else:
                # Handle missing or incomplete data for sensor_node1
                sensor_node1.update(temperature=None, u_tds=None, c_tds=None, v_tds=None)

            if _node2 in main_data and len(main_data[_node2]) > 2:
                sensor_node2.update(
                    temperature=main_data[_node2][0],  # Assuming the temperature is at index 0
                    u_tds=main_data[_node2][1],   # Assuming the u_tds is at index 1
                    c_tds=main_data[_node2][2],  # Assuming the total flow is at index 2
                    v_tds=main_data[_node2][3]  # Assuming the total flow is at index 2
                )
            else:
                # Handle missing or incomplete data for sensor_node2
                sensor_node2.update(temperature=None, u_tds=None, c_tds=None, v_tds=None)
                
            if _node3 in main_data and len(main_data[_node3]) > 2:
                sensor_node3.update(
                    temperature=main_data[_node3][0],  # Assuming the temperature is at index 0
                    u_tds=main_data[_node3][1],   # Assuming the u_tds is at index 1
                    c_tds=main_data[_node3][2],  # Assuming the total flow is at index 2
                    v_tds=main_data[_node3][3]  # Assuming the total flow is at index 2
                )
            else:
                # Handle missing or incomplete data for sensor_node3
                sensor_node3.update(temperature=None, u_tds=None, c_tds=None, v_tds=None)

            time.sleep(20)
        except Exception as e:
            print(f"Error in update_data: {e}")


def get_ack(name):


    _URL = _url + _ae + name + _ack 
    response = requests.request("GET",_URL,headers=headers,data=payload)
    ack = json.loads(response.text)
    
    print("Acknowledgment Data:")
    ack = ack["m2m:cin"]["con"]
    print(ack)

    # main_desc[name] = ack


def post_to_onem2m(data):
    url = "http://10.3.1.117:8200/~/in-cse/in-name/AE-DT/Node-1/Actuation"
    
    data = str(data)
    data_json = json.dumps(data)
    payload = json.dumps({
        "m2m:cin": {
            "con": data
        }
    })
    headers = {
    'X-M2M-Origin': 'admin:admin',
    'Content-Type': 'application/json;ty=4'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
        
thread_data = threading.Thread(target=update_data)
thread_data.daemon = True
thread_data.start()


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

    
@app.post("/real-time-location")
async def get_real_time_location():
    data = {"latitude": val["Latitude"], "longitude": val["Longitude"]}
    return JSONResponse(content=data)

@app.post("/acknowledgment")
async def get_acknowledgment():
    data = {"ack": ack}
    return JSONResponse(content=data)

@app.get('/desc/{name}')
def r_desc(name):
    print(name)
    return main_desc[name]

@app.get('/data/{name}')
def r_data(name):
    print("Node Name:",name)
    return main_data[name]


@app.post("/actuation")
async def actuation(data: dict):
    array = data.get("array")
    if array is None or not isinstance(array, list):
        return {"error": "Invalid data format"}

    print("Received array from frontend:", array)
    post_to_onem2m(array)

    get_ack(_node1)

    return {"message": "Array received successfully"}

@app.post("/percent")
async def percent(data: dict):
    global nodeVal_utds
    global nodeVal_ctds
    global nodeVal_temp
    global nodeVal_vol
    TempVal=0
    
    global node_data
    array = data.get("array")
    sectionNumber = data.get("sectionNumber")


    if array is None or not isinstance(array, list):
        return {"error": "Invalid data format"}
    
    print("Received percent array from frontend:", array)
    p1 = array[0]
    p2 = array[1]
    p3 = array[2]

    var12 = [0.05,196.703,195.628,0.5004]
    var23 = [-0.324,-1093.86, 8455.5780, 8.58857]
    
    soil1varutds= 16.134
    soil1varctds= 183.34
    soil1vartemp= -0.72
    soil1varvol= 0.204
    
    sand1varutds= 18.332
    sand1varctds= 333.103
    sand1vartemp= -0.64
    sand1varvol= 0.16
    
    soil2varutds= 9.175
    soil2varctds= 204.45
    soil2vartemp= 0.17
    soil2varvol= 0.095
    
    sand2varutds= 5.758
    sand2varctds= 10.44
    sand2vartemp= -1.6
    sand2varvol= 0
    
    soil3varutds= 2.175
    soil3varctds= 219.70
    soil3vartemp= -1.235
    soil3varvol= 0.116
    
    sand3varutds= 0.792
    sand3varctds= 94.442
    sand3vartemp= 0.088
    sand3varvol= 0.083
    
    soil4varutds= 13.759
    soil4varctds= 214.99
    soil4vartemp= -0.995
    soil4varvol= 0.082
    
    sand4varutds= 2.386
    sand4varctds= 76.846
    sand4vartemp= 0.75
    sand4varvol= 0.152
     
    # var31 = 48445.578
    dist = 0
    print(var12)
    print("Section Number From Backend : ", sectionNumber)
    if(sectionNumber==1 or sectionNumber==3):
            print("inside if condition")
            TempValSoil = soil_payload[str(sectionNumber)]
            TempValSand = sand_payload[str(sectionNumber)]
            # print("TempValue+1:", TempVal+1)
    elif(sectionNumber==4 or sectionNumber==6):
            TempValSoil = soil_payload[str(sectionNumber)]
            TempValSand = sand_payload[str(sectionNumber)]
    
    
    if TempValSoil == 1:
        selected_soil_utds = soil1varutds
        selected_soil_ctds = soil1varctds
        selected_soil_temp = soil1vartemp
        selected_soil_vol = soil1varvol
    elif TempValSoil == 2:
        selected_soil_utds = soil2varutds
        selected_soil_ctds = soil2varctds
        selected_soil_temp = soil2vartemp
        selected_soil_vol = soil2varvol 
    elif TempValSoil == 3:
        selected_soil_utds = soil3varutds
        selected_soil_ctds = soil3varctds
        selected_soil_temp = soil3vartemp
        selected_soil_vol = soil3varvol  
    elif TempValSoil == 4:
        selected_soil_utds = soil4varutds
        selected_soil_ctds = soil4varctds
        selected_soil_temp = soil4vartemp
        selected_soil_vol = soil4varvol
    else:
        selected_soil_utds = 0
        selected_soil_ctds = 0
        selected_soil_temp = 0
        selected_soil_vol = 0
        
    if TempValSand == 1:
        selected_sand_utds = sand1varutds
        selected_sand_ctds = sand1varctds
        selected_sand_temp = sand1vartemp
        selected_sand_vol = sand1varvol
    elif TempValSand == 2:
        selected_sand_utds = sand2varutds
        selected_sand_ctds = sand2varctds
        selected_sand_temp = sand2vartemp
        selected_sand_vol = sand2varvol 
    elif TempValSand == 3:
        selected_sand_utds = sand3varutds
        selected_sand_ctds = sand3varctds
        selected_sand_temp = sand3vartemp
        selected_sand_vol = sand3varvol  
    elif TempValSand == 4:
        selected_sand_utds = sand4varutds
        selected_sand_ctds = sand4varctds
        selected_sand_temp = sand4vartemp
        selected_sand_vol = sand4varvol
    else:
        selected_sand_utds = 0
        selected_sand_ctds = 0
        selected_sand_temp = 0
        selected_sand_vol = 0
          
    print("Soil Values: ",selected_soil_temp,selected_soil_utds,selected_soil_ctds,selected_soil_vol)
    print("Sand Values: ",selected_sand_temp,selected_sand_utds,selected_sand_ctds,selected_sand_vol)
    
    if(p1 <= 100):
        #bw node 1 and 2
        print("TempValue Inside P1 :", TempVal)
        dist = p1
        name='Node-1'
        node_data = r_data(name)
        nodeVal_temp = ((dist/100) * var12[0]) + (node_data[0] + selected_soil_temp + selected_sand_temp)
        nodeVal_utds = ((dist/100) * var12[1]) + (node_data[1] + selected_soil_ctds + selected_sand_ctds)
        nodeVal_ctds = ((dist/100) * var12[2]) + (node_data[2] + selected_soil_utds + selected_sand_utds)
        nodeVal_vol  = ((dist/100) * var12[3]) + (node_data[3] + selected_soil_vol + selected_sand_vol)
        # nodeVal_temp = 100
        # nodeVal_utds = TempVal
        # nodeVal_ctds = 100
        # nodeVal_vol = 100
        
    else:
        #bw 2 and 3
        dist = p2
        name='Node-2'
        node_data = r_data(name)
        nodeVal_temp = ((dist/100) * var23[0]) + (node_data[0] + selected_soil_temp + selected_sand_temp)
        nodeVal_utds = ((dist/100) * var23[1]) + (node_data[1] +selected_soil_ctds+ selected_sand_ctds)
        nodeVal_ctds = ((dist/100) * var23[2]) + (node_data[2] +selected_soil_utds+ selected_sand_utds)
        nodeVal_vol  = ((dist/100) * var23[3]) + (node_data[3] + selected_soil_vol+ selected_sand_vol)
        # nodeVal_temp = 150
        # nodeVal_utds = TempVal
        # nodeVal_ctds = 200
        # nodeVal_vol = 300
    print("Temparature: ",nodeVal_temp," Uncompensated_TDS: ",nodeVal_utds, " Compensated_TDS:", nodeVal_ctds," Voltage_TDS:", nodeVal_vol)
    print("SoilData:", soil_payload)
    
    
@app.post("/nodeVal")
async def get_newNode():
    data = {"nodeVal_temp":nodeVal_temp, "nodeVal_utds": nodeVal_utds,"nodeVal_ctds": nodeVal_ctds,"nodeVal_vol": nodeVal_vol, "node_data": node_data}
    return JSONResponse(content=data)


@app.post("/sand")
async def receive_soil_container_count(payload: dict):
    # Process the soil container count as needed
    # Access the values using the keys in the payload dictionary
    key = next(iter(payload))  # Get the first key in the dictionary
    value = payload[key]
    
    print(f'Received sand Container Count - {payload}')
    sand_payload[key] = value
    
    return {"message": "Soil Container Count received successfully"}

@app.post("/soil")
async def receive_soil_container_count(payload: dict):
    # Process the soil container count as needed
    # Access the values using the keys in the payload dictionary
    key = next(iter(payload))  # Get the first key in the dictionary
    value = payload[key]
    
    print(f'Received Soil Container Count - {payload}')
    soil_payload[key] = value
    
    return {"message": "Soil Container Count received successfully"}

if __name__=='__main__':
    import uvicorn
    uvicorn.run(app,host="0.0.0.0",port=8080)
