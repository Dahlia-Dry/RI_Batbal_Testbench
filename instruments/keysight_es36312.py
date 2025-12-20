from instruments.instrument_base import Instrument
import time

class KeysightE36312(Instrument):
    """
    Keysight E36312 driver implemented using pyvisa.
    """

    # -------------
    # Channel control
    # -------------

    def _select(self, ch):
        self.write(f"INST:NSEL {ch}")

    def set_voltage(self, ch, voltage):
        self._select(ch)
        self.write(f"VOLT {voltage}")

    def set_current(self, ch, current):
        self._select(ch)
        self.write(f"CURR {current}")

    # --- NEW: clearer aliases for schema-level actions ---

    def set_current_limit(self, ch, current):
        self.set_current(ch, current)

    def set_voltage_limit(self, ch, voltage):
        self.set_overvoltage_protection(ch, voltage)

    def output_on(self, ch):
        self._select(ch)
        self.write("OUTP ON")

    def output_off(self, ch):
        self._select(ch)
        self.write("OUTP OFF")

    # --- NEW: explicit output actions ---

    def enable_output(self, ch):
        self.output_on(ch)
        return {"channel": ch, "output_enabled": True}

    def disable_output(self, ch):
        self.output_off(ch)
        return {"channel": ch, "output_enabled": False}

    # -------------
    # Measurements
    # -------------

    def measure_voltage(self, ch):
        self._select(ch)
        v = float(self.query("MEAS:VOLT?"))
        return {"channel": ch, "voltage": v}

    def measure_current(self, ch):
        self._select(ch)
        i = float(self.query("MEAS:CURR?"))
        return {"channel": ch, "current": i}
    
    def measure_power(self, ch):
        self._select(ch)
        v = float(self.query("MEAS:VOLT?"))
        i = float(self.query("MEAS:CURR?"))
        return {"channel": ch, "power": v * i}

    # -------------
    # Protections & sense
    # -------------

    def set_overvoltage_protection(self, ch, limit):
        self._select(ch)
        self.write(f"VOLT:PROT {limit}")

    def clear_protection(self, ch):
        self._select(ch)
        self.write("VOLT:PROT:CLE")

    # --- NEW: sense mode control ---

    def enable_remote_sense(self, ch):
        self._select(ch)
        self.write("VOLT:SENS ON")

    def disable_remote_sense(self, ch):
        self._select(ch)
        self.write("VOLT:SENS OFF")

    # -------------
    # High-level actions
    # -------------

    def set_power(self, ch, voltage, current_limit, ramp_time=0.0, steps=20):
        """
        Convenience action: set voltage + current limit with optional ramp.
        """

        self.set_current_limit(ch, current_limit)

        if ramp_time is None or ramp_time <= 0:
            self.set_voltage(ch, voltage)
            self.output_on(ch)
            return {
                "channel": ch,
                "voltage": voltage,
                "current_limit": current_limit,
                "ramped": False,
            }

        self.output_on(ch)
        dv = voltage / steps
        dt = ramp_time / steps

        for i in range(1, steps + 1):
            self.set_voltage(ch, dv * i)
            time.sleep(dt)

        self.set_voltage(ch, voltage)

        return {
            "channel": ch,
            "voltage": voltage,
            "current_limit": current_limit,
            "ramped": True,
            "ramp_time": ramp_time,
        }


    def ramp_voltage(self, ch, target_voltage, ramp_time, steps=20):
        self._select(ch)

        dv = target_voltage / steps
        dt = ramp_time / steps

        self.output_on(ch)

        for i in range(1, steps + 1):
            self.set_voltage(ch, dv * i)
            time.sleep(dt)

        self.set_voltage(ch, target_voltage)

        return {
            "channel": ch,
            "final_voltage": target_voltage,
            "ramp_time": ramp_time,
        }


    def configure_psu(
        self,
        channel,
        current_limit=None,
        voltage_limit=None,
        output_enabled=False,
        sense_mode="local",
    ):
        if sense_mode == "remote":
            self.enable_remote_sense(channel)
        else:
            self.disable_remote_sense(channel)

        if current_limit is not None:
            self.set_current_limit(channel, current_limit)

        if voltage_limit is not None:
            self.set_voltage_limit(channel, voltage_limit)

        if output_enabled:
            self.output_on(channel)
        else:
            self.output_off(channel)

        return {
            "channel": channel,
            "current_limit": current_limit,
            "voltage_limit": voltage_limit,
            "output_enabled": output_enabled,
            "sense_mode": sense_mode,
        }
