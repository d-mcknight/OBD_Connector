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
    def metrics(self) -> List[dict]:
        """
        Get all measured metrics as a time series. Note that the `time` attached
        to each list element will differ slightly from the actual time the
        metrics were collected.
        """
        metrics = copy(self._metrics)
        squashed_metrics = list()
        for command, values in metrics.items():
            for idx, val in enumerate(values):
                while len(squashed_metrics) < idx + 1:
                    squashed_metrics.append(dict())
                squashed_metrics[idx].setdefault('time', val.time)
                squashed_metrics[idx][command] = \
                    val.value.magnitude if val.value else None
        return squashed_metrics

    @property
    def engine_load(self) -> float:
        """
        Get the engine load as a float (0.0-1.0)
        """
        load = self._metrics["ENGINE_LOAD"][-1].value
        return load.magnitude/100 if load else 0.0

    @property
    def coolant_temp(self) -> float:
        """
        Get coolant temperature in degrees Celcius (defaults to -273.15)
        """
        temp = self._metrics["COOLANT_TEMP"][-1].value
        return temp.magnitude if temp else -273.15

    @property
    def engine_rpm(self) -> float:
        """
        Get engine RPM as a float
        """
        rpm = self._metrics["RPM"][-1].value
        return rpm.magnitude if rpm else 0.0

    @property
    def vehicle_speed(self) -> float:
        """
        Get vehicle speed in km/h
        """
        speed = self._metrics["SPEED"][-1].value
        return speed.magnitude if speed else 0.0

    @property
    def fuel_level(self) -> float:
        """
        Get the current fuel level as a float (0.0-1.0)
        """
        fuel = self._metrics["FUEL_LEVEL"][-1].value
        return fuel.magnitude/100 if fuel else 0.0

    @property
    def oil_temp(self) -> float:
        """
        Get engine oil temperature in degrees Celcius (defaults to -273.15)
        """
        temp = self._metrics["OIL_TEMP"][-1].value
        return temp.magnitude if temp else -273.15

    @property
    def fuel_rate(self) -> float:
        """
        Get the instantaneous rate of fuel consumption in L/hr
        """
        consumption = self._metrics["FUEL_RATE"][-1].value
        return consumption.magnitude if consumption else -1.0

    @property
    def diagnostic_trouble_codes(self) -> List[str]:
        """
        Get a list of active Diagnostic Trouble Codes
        """
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
