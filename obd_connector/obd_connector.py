from threading import Thread, Event
from typing import Dict, List
from copy import copy
from obd import OBD, OBDResponse, OBDCommand, commands


class OBDConnector(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.obd = OBD()
        self._stopping = Event()
        self._loop_wait = 0.2
        self._command_names = [
            "ENGINE_LOAD",
            "COOLANT_TEMP",
            "RPM",
            "SPEED",
            "FUEL_LEVEL",
            "OIL_TEMP",
            "FUEL_RATE",
            "GET_CURRENT_DTC"
        ]
        self._commands: List[OBDCommand] = list()
        self._metrics: Dict[str, List[OBDResponse]] = dict()
        if not self.obd.is_connected():
            raise RuntimeError("No OBD Connection")
        self.register_events()

    @property
    def metrics(self):
        return copy(self._metrics)

    @property
    def engine_load(self) -> float:
        load = self._metrics["ENGINE_LOAD"][-1].value
        load_pct = load.magnitude/100 if load else 0.0
        return load_pct

    @property
    def coolant_temp(self) -> float:
        temp = self._metrics["COOLANT_TEMP"][-1].value
        temp = temp.magnitude if temp else -273.13
        return temp

    @property
    def engine_rpm(self) -> float:
        return self._metrics["RPM"][-1].value

    @property
    def vehicle_speed_kph(self) -> float:
        return self._metrics["SPEED"][-1].value

    @property
    def fuel_level(self) -> float:
        return self._metrics["FUEL_LEVEL"][-1].value

    @property
    def oil_temp(self):
        return self._metrics["OIL_TEMP"][-1].value

    @property
    def fuel_rate(self):
        return self._metrics["FUEL_RATE"][-1].value

    @property
    def diagnostic_trouble_codes(self):
        return self._metrics["GET_CURRENT_DTC"][-1].value

    def register_events(self):
        for command in self._command_names:
            if command not in commands:
                raise KeyError(f"{command} not supported")
            self._commands.append(commands[command])
            self._metrics[command] = [OBDResponse()]

    def run(self):
        while not self._stopping.wait(self._loop_wait):
            if not self.obd.is_connected():
                raise RuntimeError("OBD Connection unexpectedly closed")
            for cmd in self._commands:
                self._metrics[cmd.name].append(self.obd.query(cmd, force=True))

    def stop(self):
        self._stopping.set()
