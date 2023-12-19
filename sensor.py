# import pandas as pd





class WaterFlowSensorDigitalTwin:
    def __init__(self, node_id):
        self.node_id = node_id
        self.timestamp = None
        self.flowrate = None
        self.total_flow = None
        self.status = "Idle"  # Initial status

    def update(self, timestamp, flowrate, total_flow):
        # Update the digital twin's state based on sensor data
        self.timestamp = timestamp
        self.flowrate = flowrate
        self.total_flow = total_flow
        self.status = self.get_status()
        # Perform logic or calculations based on the sensor data
        if flowrate is not None and flowrate > 0:
            self.status = "Flowing"
        else:
            self.status = "Idle"

        print(f"Sensor {self.node_id} Updated - Status: {self.status}")

    def get_status(self):
        return self.status

    def get_flowrate(self):
        return self.flowrate

    def get_total_flow(self):
        return self.total_flow
