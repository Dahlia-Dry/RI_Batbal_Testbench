from instruments.instrument_base import Instrument
import time

class KeysightE36312(Instrument):
    supported_actions = ["set_power"]

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

    def output_on(self, ch):
        self._select(ch)
        self.write("OUTP ON")

    def output_off(self, ch):
        self._select(ch)
        self.write("OUTP OFF")

    # -------------
    # Measurements
    # -------------

    def measure_voltage(self, ch):
        self._select(ch)
        return float(self.query("MEAS:VOLT?"))

    def measure_current(self, ch):
        self._select(ch)
        return float(self.query("MEAS:CURR?"))

    # -------------
    # Protections
    # -------------

    def set_overvoltage_protection(self, ch, limit):
        self._select(ch)
        self.write(f"VOLT:PROT {limit}")

    def clear_protection(self, ch):
        self._select(ch)
        self.write("VOLT:PROT:CLE")

    def set_power(self, ch, voltage, current_limit, ramp_time=0.0, steps=20):
        """
        Configure channel voltage + current limit with optional ramping.

        Parameters:
            ch (int): channel number (1, 2, or 3)
            voltage (float): target voltage
            current_limit (float): current limit (A)
            ramp_time (float): seconds to ramp from 0V to target V
            steps (int): number of ramp increments (default 20)
        """

        # --- Always set current limit first ---
        self.set_current(ch, current_limit)

        # --- If no ramp time, set voltage directly ---
        if ramp_time is None or ramp_time <= 0:
            self.set_voltage(ch, voltage)
            self.output_on(ch)
            return

        # --- Perform a smooth linear ramp ---
        dv = voltage / steps
        dt = ramp_time / steps

        # Ensure output is enabled before ramp (Keysight requires this for real output)
        self.output_on(ch)

        for i in range(1, steps + 1):
            v = dv * i
            self.set_voltage(ch, v)
            time.sleep(dt)

        # At the end, ensure exact final voltage (remove rounding error)
        self.set_voltage(ch, voltage)