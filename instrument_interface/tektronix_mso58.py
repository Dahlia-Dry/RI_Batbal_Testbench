# tektronix_mso58.py
from tm_devices import DeviceManager

class TekMSO58:
    def __init__(self, address, alias="SCOPE1"):
        self.address = address
        self.alias = alias
        self.dm = None
        self.scope = None

    def connect(self):
        print(f"Connecting to Tektronix MSO58 at {self.address}...")
        self.dm = DeviceManager()
        self.scope = self.dm.add_scope(self.address, alias=self.alias)

        idn = self.scope.query("*IDN?")
        print("Connected:", idn)
        return idn

    def close(self):
        print("Closing Tektronix MSO58...")
        try:
            if self.scope:
                self.scope.close()
        except Exception:
            pass
        try:
            if self.dm:
                self.dm.close()
        except Exception:
            pass
        print("Closed.")

    # ---------------------------
    # Channel control (SCPI only)
    # ---------------------------
    def set_channel_on(self, ch: int):
        self.scope.write(f"SELECT:CH{ch} ON")

    def set_channel_off(self, ch: int):
        self.scope.write(f"SELECT:CH{ch} OFF")

    def set_timebase(self, scale: float):
        self.scope.write(f"HORizontal:SCAle {scale}")

    def set_vertical_scale(self, ch: int, scale: float):
        self.scope.write(f"CH{ch}:SCAle {scale}")

    def autoset(self):
        self.scope.write("AUTOSet EXECute")

    # ---------------------------
    # Waveform acquisition (binary)
    # ---------------------------
    def acquire_waveform(self, ch: int):
        s = self.scope

        s.write("DATa:ENCdg RIBinary")
        s.write("DATa:WIDth 1")
        s.write(f"DATa:SOURCE CH{ch}")

        ymult = float(s.query("WFMPRE:YMULT?"))
        yoff  = float(s.query("WFMPRE:YOFF?"))
        yzero = float(s.query("WFMPRE:YZERO?"))
        xincr = float(s.query("WFMPRE:XINCR?"))

        s.write("CURVe?")
        raw = s.visa_resource.read_raw()

        # parse Tek block header
        prefix = raw[0:2].decode("ascii")  # should be '#4' or similar
        digits = int(prefix[1])
        header_len = 2 + digits
        data = raw[header_len:-1]   # everything except final LF

        import numpy as np
        samples = np.frombuffer(data, dtype=np.int8)

        volts = (samples - yoff) * ymult + yzero
        t = np.arange(len(volts)) * xincr

        return t, volts
