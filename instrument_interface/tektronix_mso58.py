from instrument_base import Instrument
import numpy as np

class TekMSO58(Instrument):

    # -------------------------
    # Basic configuration
    # -------------------------

    def autoset(self):
        self.write("AUTOS EXEC")

    def set_channel_on(self, ch):
        self.write(f"SEL:CH{ch} ON")

    def set_channel_off(self, ch):
        self.write(f"SEL:CH{ch} OFF")

    def set_vertical_scale(self, ch, scale_vdiv):
        self.write(f"CH{ch}:SCA {scale_vdiv}")

    def set_horizontal_scale(self, sec_div):
        self.write(f"HOR:SCA {sec_div}")

    # -------------------------
    # Measurements
    # -------------------------

    def measure_vpp(self, ch):
        self.write(f"MEASU:MEAS1:SOU CH{ch}")
        self.write("MEASU:MEAS1:TYPe VPP")
        return float(self.query("MEASU:MEAS1:VAL?"))

    def measure_freq(self, ch):
        self.write(f"MEASU:MEAS1:SOU CH{ch}")
        self.write("MEASU:MEAS1:TYPe FREQuency")
        return float(self.query("MEASU:MEAS1:VAL?"))

    # -------------------------
    # Waveform acquisition
    # -------------------------

    def acquire_waveform(self, ch):
        self.write(f"DATa:SOUrce CH{ch}")
        self.write("DATa:ENCdg ASCII")
        self.write("DATa:WIDth 1")

        raw = self.query("CURVe?")
        data = np.array([float(x) for x in raw.split(",")])
        return data