class WaterFlowSensorDigitalTwin:
    def __init__(self, node_id):
        self.node_id = node_id
        self.temperature = None
        self.u_tds = None
        self.c_tds = None  # Added compensated TDS
        self.v_tds = None  # Added voltage TDS
        self.status = "Idle"  # Initial status

    def update(self, temperature, u_tds, c_tds, v_tds):
        # Update the digital twin's state based on sensor data
        self.temperature = temperature
        self.u_tds = u_tds
        self.c_tds = c_tds
        self.v_tds = v_tds
        self.status = self.get_status()
        # Perform logic or calculations based on the sensor data
        if u_tds is not None and u_tds > 0:
            self.status = "Flowing"
        else:
            self.status = "Idle"

        print(f"Sensor {self.node_id} Updated - Status: {self.status}")

    def get_status(self):
        return self.status

    def get_u_tds(self):
        return self.u_tds

    def get_c_tds(self):
        return self.c_tds

    def get_v_tds(self):
        return self.v_tds
