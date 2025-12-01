# rigol_dg1062z.py
import pyvisa
from instruments.instrument_base import Instrument

class RigolDG1062Z(Instrument):
    supported_actions = ["start_waveform"]
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
    
    def start_waveform(self, channel, waveform, output=None):
        """
        Configure and enable a waveform based on YAML specification.

        waveform = {
            "type": "sine",
            "frequency": 1e6,
            "amplitude": 2.0,
            "offset": 0.0,
        }

        output = {
            "impedance": "50ohm" | "highz",
            "enabled": true | false
        }
        """

        # --- 1. Waveform type ---
        wtype = waveform["type"].lower()

        if wtype == "sine":
            func = "SIN"
        elif wtype == "square":
            func = "SQU"
        elif wtype == "ramp":
            func = "RAMP"
        else:
            raise ValueError(f"Unsupported waveform type: {wtype}")

        self.set_function(channel, func)

        # --- 2. Basic parameters ---
        freq = waveform.get("frequency")
        amp = waveform.get("amplitude")
        offset = waveform.get("offset", 0)

        if freq is not None:
            self.set_frequency(channel, freq)

        if amp is not None:
            self.set_amplitude(channel, amp)

        self.set_offset(channel, offset)

        # --- 3. Output settings ---
        if output:
            imp = output.get("impedance", "").lower()
            if imp == "50ohm" or imp == "50":
                self.fifty_ohm_mode(channel)
            elif imp in ("highz", "high-z", "inf", "infinite"):
                self.high_impedance_mode(channel)
            elif imp != "":
                raise ValueError(f"Unsupported output impedance: {imp}")

            # enable/disable output
            if output.get("enabled", True):
                self.output_on(channel)
            else:
                self.output_off(channel)
        else:
            # default: ON
            self.output_on(channel)

        print(f"[RigolDG1062Z] Channel {channel} waveform started.")
