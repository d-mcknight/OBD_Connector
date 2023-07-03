from time import sleep
from pprint import pprint
from obd_connector.obd_connector import OBDConnector


class Monitor:
    def __init__(self):
        self.connector = OBDConnector()
        self.connector.start()

    def log_stats(self):
        data = {'engine_load': self.connector.engine_load,
                'coolant_temp': self.connector.coolant_temp,
                'engine_rpm': self.connector.engine_rpm,
                'vehicle_speed': self.connector.vehicle_speed,
                'fuel_level': self.connector.fuel_level,
                'oil_temp': self.connector.oil_temp,
                'fuel_rate': self.connector.fuel_rate,
                'dtcs': self.connector.diagnostic_trouble_codes}
        pprint(data)

    def stop(self):
        self.connector.stop()


if __name__ == "__main__":
    monitor = Monitor()
    try:
        while True:
            monitor.log_stats()
            sleep(1)
    except KeyboardInterrupt:
        monitor.stop()
        data = monitor.connector.metrics
        pprint(data)
