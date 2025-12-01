# rigol_dg1062z.py
import pyvisa

class RigolDG1062Z(Instrument):
    # -------------------------------
    # Waveform configuration
    # -------------------------------
    def set_function(self, channel, func):
        self.write(f"SOUR{channel}:FUNC {func}")

    def set_frequency(self, channel, freq_hz):
        self.write(f"SOUR{channel}:FREQ {freq_hz}")

    def set_amplitude(self, channel, volts_pkpk):
        self.write(f"SOUR{channel}:VOLT {volts_pkpk}")

    def set_offset(self, channel, offset_v):
        self.write(f"SOUR{channel}:VOLT:OFFS {offset_v}")

    def output_on(self, channel):
        self.write(f"OUTP{channel} ON")

    def output_off(self, channel):
        self.write(f"OUTP{channel} OFF")

    # -------------------------------
    # Composite helper (no changes needed)
    # -------------------------------
    def configure_sine(self, channel, freq, amplitude, offset=0):
        self.set_function(channel, "SIN")
        self.set_frequency(channel, freq)
        self.set_amplitude(channel, amplitude)
        self.set_offset(channel, offset)

    # -------------------------------
    # Load settings
    # -------------------------------
    def high_impedance_mode(self, channel):
        self.write(f"OUTP{channel}:LOAD INF")

    def fifty_ohm_mode(self, channel):
        self.write(f"OUTP{channel}:LOAD 50")

    # -------------------------------
    # IDN
    # -------------------------------
    def id(self):
        return self.query("*IDN?")
