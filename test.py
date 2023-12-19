# import xml.etree.ElementTree as ET

# def parse_data(xml_data):
#     # Parse the XML-like data
#     root = ET.fromstring(xml_data)
    
#     # Initialize a dictionary to store the parsed data
#     parsed_data = {}
    
#     # Iterate through the <str> elements
#     for element in root.findall('.//str'):
#         name = element.get('name')
#         val = element.get('val')
        
#         if name == "Node Location":
#             # Parse the Node Location value as a dictionary
#             val = eval(val)  # Note: Be cautious when using eval in production code
            
#         elif name == "Data String Parameters":
#             # Parse the Data String Parameters value as a list
#             val = eval(val)  # Note: Be cautious when using eval in production code
        
#         parsed_data[name] = val
    
#     return parsed_data

# # Example usage:
# xml_data = """<obj><str name="Node ID" val="WM-WF-PH02-70"/>
# <str name="Node Location" val="{'Latitude': 17.446267, 'Longitude': 78.349436}"/>
# <str name="Device Model" val="{'Controller': 'Raspberry Pi 3B+, id=1.0', 'Device': 'Smart Retrofit Water Meter node with Flow Rate and Total Flow', 'Sensors': ['(Timestamp)', '(Flowrate = Smart Water Meter - Retrofit, id=1.0)', '(Total Flow = Smart Water Meter - Retrofit, id=1.0)']}"/>
# <str name="Version History" val="[{'ver': 'V7.0.0', 'dt_start': '14-11-2021 00-00-00', 'dt_end': '31-12-9999 23-59-59'}]"/>
# <str name="Data String Parameters" val="['Timestamp', 'Flowrate', 'Total Flow']"/>
# <str name="Parameters Description" val="Data Description, [datatype], [Units], [Resolution], [Accuracy]"/>
# <str name="Timestamp" val="The number of seconds that have elapsed since Thursday, 1970 Jan 1 00:00:00 UTC, [int], [s], [60 s], [n/a]"/>
# <str name="Flowrate" val="The instantaneous value of Flow rate, [float], [Kl/min], [0.1 Kl/min], [n/a]"/>
# <str name="Total Flow" val="The instantaneous value of Total flow, [float], [Kl], [0.1 Kl], [n/a]"/>
# </obj>"""

# result = parse_data(xml_data)

# # Print the desired values
# print("Node Location:", result.get("Node Location"))
# print("Data String Parameters:", result.get("Data String Parameters"))


import xml.etree.ElementTree as ET
import json

def parse_data_to_json(xml_data):
    # Parse the XML-like data
    root = ET.fromstring(xml_data)
    
    # Initialize a dictionary to store the selected parsed data
    selected_data = {}
    
    # Iterate through the <str> elements
    for element in root.findall('.//str'):
        name = element.get('name')
        val = element.get('val')
        
        if name == "Node ID" or name == "Node Location" or name == "Data String Parameters":
            # Include only "Node ID," "Node Location," and "Data String Parameters" in the result
            if name == "Node Location":
                # Parse the Node Location value as a dictionary and convert to the desired format
                location_dict = eval(val)  # Note: Be cautious when using eval in production code
                val = [location_dict['Latitude'], location_dict['Longitude']]
            elif name == "Data String Parameters":
                # Parse the Data String Parameters value as a list
                val = eval(val)  # Note: Be cautious when using eval in production code
            
            selected_data[name] = val
    
    # Convert the selected data dictionary to JSON format
    json_data = json.dumps(selected_data, indent=2)
    
    return json_data

# Example usage:
xml_data = """<obj><str name="Node ID" val="WM-WF-PH02-70"/>
<str name="Node Location" val="{'Latitude': 17.446267, 'Longitude': 78.349436}"/>
<str name="Device Model" val="{'Controller': 'Raspberry Pi 3B+, id=1.0', 'Device': 'Smart Retrofit Water Meter node with Flow Rate and Total Flow', 'Sensors': ['(Timestamp)', '(Flowrate = Smart Water Meter - Retrofit, id=1.0)', '(Total Flow = Smart Water Meter - Retrofit, id=1.0)']}"/>
<str name="Version History" val="[{'ver': 'V7.0.0', 'dt_start': '14-11-2021 00-00-00', 'dt_end': '31-12-9999 23-59-59'}]"/>
<str name="Data String Parameters" val="['Timestamp', 'Flowrate', 'Total Flow']"/>
<str name="Parameters Description" val="Data Description, [datatype], [Units], [Resolution], [Accuracy]"/>
<str name="Timestamp" val="The number of seconds that have elapsed since Thursday, 1970 Jan 1 00:00:00 UTC, [int], [s], [60 s], [n/a]"/>
<str name="Flowrate" val="The instantaneous value of Flow rate, [float], [Kl/min], [0.1 Kl/min], [n/a]"/>
<str name="Total Flow" val="The instantaneous value of Total flow, [float], [Kl], [0.1 Kl], [n/a]"/>
</obj>"""

result = parse_data_to_json(xml_data)

# Print the result in JSON format
print(result)

