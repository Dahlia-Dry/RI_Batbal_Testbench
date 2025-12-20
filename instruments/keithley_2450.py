import time
import numpy as np
from pymeasure.instruments.keithley import Keithley2450 as PMKeithley2450
import os
import csv

class Keithley2450:
    """
    Keithley 2450 SMU driver implemented using PyMeasure.
    """
    def __init__(self, ip_address, timeout=5000):
        self.ip = ip_address
        self.timeout = timeout
        self.inst = None

    # --------------------------------------------------
    # Connection
    # --------------------------------------------------

    def connect(self):
        resource = f"TCPIP::{self.ip}::INSTR"
        self.inst = PMKeithley2450(resource)
        self.inst.timeout = self.timeout

        self.inst.reset()
        self.inst.disable_source()

        return {
            "instrument": "keithley_2450",
            "resource": resource,
        }

    def close(self):
        if self.inst:
            self.inst.disable_source()
            self.inst.shutdown()
            self.inst = None

    # --------------------------------------------------
    # Actions
    # --------------------------------------------------

    def smu_reset(self):
        self.inst.reset()
        self.inst.disable_source()
        return {}

    def smu_zero_output(self):
        if self.inst.source_mode == "voltage":
            self.inst.source_voltage = 0.0
        else:
            self.inst.source_current = 0.0

        self.inst.disable_source()

        return {
            "source_level": 0.0,
            "output_enabled": False,
        }

    # --------------------------------------------------

    def smu_configure(
        self,
        source_function,
        source_level,
        compliance_limit,
        measure_function,
        sense_mode="2w",
        output_enabled=False,
    ):
        # Sense mode
        self.inst.use_four_wire = (sense_mode == "4w")

        # Source configuration
        if source_function == "voltage":
            self.inst.apply_voltage(compliance_current=compliance_limit)
            self.inst.source_voltage = source_level
        else:
            self.inst.apply_current(compliance_voltage=compliance_limit)
            self.inst.source_current = source_level

        # Measurement function
        if measure_function == "current":
            self.inst.measure_current()
        else:
            self.inst.measure_voltage()

        # Output
        if output_enabled:
            self.inst.enable_source()
        else:
            self.inst.disable_source()

        return {
            "source_function": source_function,
            "source_level": source_level,
            "compliance_limit": compliance_limit,
            "measure_function": measure_function,
            "sense_mode": sense_mode,
            "output_enabled": output_enabled,
        }

    # --------------------------------------------------

    def smu_set_source(
        self,
        source_function,
        level,
        compliance_limit,
        output_enabled=True,
    ):
        if source_function == "voltage":
            self.inst.apply_voltage(compliance_current=compliance_limit)
            self.inst.source_voltage = level
        else:
            self.inst.apply_current(compliance_voltage=compliance_limit)
            self.inst.source_current = level

        if output_enabled:
            self.inst.enable_source()
        else:
            self.inst.disable_source()

        return {
            "source_function": source_function,
            "source_level": level,
            "compliance_limit": compliance_limit,
            "output_enabled": output_enabled,
        }

    # --------------------------------------------------

    def smu_set_output(self, enabled):
        if enabled:
            self.inst.enable_source()
        else:
            self.inst.disable_source()

        return {
            "output_enabled": enabled
        }

    # --------------------------------------------------
    # Measurements
    # --------------------------------------------------

    def smu_measure_voltage(self):
        return {
            "voltage": float(self.inst.voltage)
        }

    def smu_measure_current(self):
        return {
            "current": float(self.inst.current)
        }

    # --------------------------------------------------
    # Sweep
    # --------------------------------------------------

    def smu_sweep(self, start, stop, step, delay=0.0, save_to=None):
        points = []

        source_mode = self.inst.source_mode  # "voltage" or "current"
        self.inst.enable_source()

        for level in np.arange(start, stop + step, step):
            if source_mode == "voltage":
                self.inst.source_voltage = level
                measured = self.inst.current
            else:
                self.inst.source_current = level
                measured = self.inst.voltage

            if delay > 0:
                time.sleep(delay)

            points.append(
                {
                    "source_level": float(level),
                    "measured": float(measured),
                }
            )

        self.inst.disable_source()
        result = {"points": points}

        # Optional CSV save
        if save_to:
            os.makedirs(os.path.dirname(save_to), exist_ok=True)

            with open(save_to, "w", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["source_level", "measured"],
                )
                writer.writeheader()
                writer.writerows(points)

            result["file"] = save_to

        return result