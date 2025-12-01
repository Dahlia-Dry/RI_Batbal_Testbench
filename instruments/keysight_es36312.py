from instruments.instrument_base import Instrument

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
