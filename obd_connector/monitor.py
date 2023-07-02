from time import sleep
from pprint import pprint
from obd_connector.connection import OBDConnection


class Monitor:
    def __init__(self):
        self.connector = OBDConnection()
        self.connector.start()

    def log_stats(self):
        data = {'engine_load': self.connector.engine_load,
                'coolant_temp': self.connector.coolant_temp,
                'engine_rpm': self.connector.engine_rpm,
                'vehicle_speed': self.connector.vehicle_speed,
                'fuel_level': self.connector.fuel_level,
                'ambient_temp': self.connector.ambient_temp,
                'oil_temp': self.connector.oil_temp,
                'fuel_rate': self.connector.fuel_rate,
                'dtcs': self.connector.diagnostic_trouble_codes}
        pprint(data)

    def stop(self):
        self.connector.stop()


if __name__ == "__main__":
    monitor = Monitor()
    while True:
        monitor.log_stats()
        sleep(5)
