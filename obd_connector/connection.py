from threading import Thread, Event
from typing import Dict, List
from obd import OBD, OBDResponse, OBDCommand, commands


class OBDConnection(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.obd = OBD()
        self._stopping = Event()
        self._command_names = [
            "ENGINE_LOAD",
            "COOLANT_TEMP",
            "RPM",
            "SPEED",
            "FUEL_LEVEL",
            "AMBIENT_AIR_TEMP",
            "OIL_TEMP",
            "FUEL_RATE",
            "GET_CURRENT_DTC"
        ]
        self._commands: List[OBDCommand] = list()
        self._metrics: Dict[str, OBDResponse] = dict()

    @property
    def engine_load(self):
        return self._metrics["ENGINE_LOAD"].value

    @property
    def coolant_temp(self):
        return self._metrics["COOLANT_TEMP"].value

    @property
    def engine_rpm(self):
        return self._metrics["RPM"].value

    @property
    def vehicle_speed(self):
        return self._metrics["SPEED"].value

    @property
    def fuel_level(self):
        return self._metrics["FUEL_LEVEL"].value

    @property
    def ambient_temp(self):
        return self._metrics["AMBIENT_AIR_TEMP"]

    @property
    def oil_temp(self):
        return self._metrics["OIL_TEMP"].value

    @property
    def fuel_rate(self):
        return self._metrics["FUEL_RATE"].value

    @property
    def diagnostic_trouble_codes(self):
        return self._metrics["GET_CURRENT_DTC"].value

    def register_events(self):
        for command in self._command_names:
            if command not in commands:
                raise KeyError(f"{command} not supported")
            self._commands.append(commands[command])
            self._metrics[command] = OBDResponse()

    def run(self):
        while self._stopping.wait(0.1):
            if not self.obd.is_connected():
                raise RuntimeError("OBD Connection unexpectedly closed")
            for cmd in self._commands:
                self._metrics[cmd.name] = self.obd.query(cmd, force=True)

    def stop(self):
        self._stopping.set()
