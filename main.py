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
# _ae = "AE-WM/WM-WF/"

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

if __name__=='__main__':
    import uvicorn
    uvicorn.run(app,host="0.0.0.0",port=8080)

