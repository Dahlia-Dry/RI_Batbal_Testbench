from instruments.instrument_base import Instrument

class RigolDG1062Z(Instrument):
    """
    RigolDG1062Z driver implemented using pyvisa
    """
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
    
    def configure_output(self, channel, impedance=None, enabled=None):
        if impedance:
            imp = impedance.lower()
            if imp in ("50ohm", "50"):
                self.fifty_ohm_mode(channel)
            elif imp in ("highz", "high-z", "inf", "infinite"):
                self.high_impedance_mode(channel)
            else:
                raise ValueError(f"Unsupported output impedance: {imp}")

        if enabled is not None:
            if enabled:
                self.output_on(channel)
            else:
                self.output_off(channel)

        return {
            "channel": channel,
            "impedance": impedance,
            "output_enabled": enabled,
        }

    
    def start_waveform(self, channel, waveform, output=None):
        """
        Configure waveform parameters and start waveform output.

        By default, output is enabled unless explicitly disabled.
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
        offset = waveform.get("offset", 0.0)

        if freq is not None:
            self.set_frequency(channel, freq)

        if amp is not None:
            self.set_amplitude(channel, amp)

        self.set_offset(channel, offset)

        # --- 3. Output handling (explicit defaults) ---
        output = output or {}
        enabled = output.get("enabled", True)
        impedance = output.get("impedance")

        output_state = self.configure_output(
            channel=channel,
            impedance=impedance,
            enabled=enabled,
        )

        print(f"[RigolDG1062Z] Channel {channel} waveform started.")

        # --- 4. Return structured state ---
        return {
            "channel": channel,
            "waveform": wtype,
            "frequency": freq,
            "amplitude": amp,
            "offset": offset,
            **output_state,
        }


    def stop_waveform(self, channel):
        self.output_off(channel)
        print(f"[RigolDG1062Z] Channel {channel} waveform stopped.")
        return {
            "channel": channel,
            "output_enabled": False,
        }
