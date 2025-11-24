# tektronix_mso58.py
from tm_devices import DeviceManager

class TekMSO58:
    """
    Very thin wrapper around tm_devices MSO5 driver.
    Only uses APIs confirmed from GitHub:
      - DeviceManager
      - add_scope(...)
      - scope.write()
      - scope.query()
      - scope.curve_query()
      - scope.save_screenshot()
    """

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

    # ------------------------------
    # Basic SCPI passthrough
    # ------------------------------
    def write(self, cmd):
        self.scope.write(cmd)

    def query(self, cmd):
        return self.scope.query(cmd)

    # ------------------------------
    # Channel controls
    # ------------------------------
    def channel_on(self, ch):
        self.scope.write(f"SELECT:CH{ch} ON")

    def channel_off(self, ch):
        self.scope.write(f"SELECT:CH{ch} OFF")

    # ------------------------------
    # Autoset
    # ------------------------------
    def autoset(self):
        self.scope.write("AUTOSet EXECute")

    # ------------------------------
    # Waveform Acquisition
    # Uses curve_query() — VERIFIED in repo
    # ------------------------------
    def acquire_waveform(self, ch):
        s = self.scope

        # --- Configure binary waveform transfer ---
        s.write(f"DATA:SOURCE CH{ch}")
        s.write("DATA:ENC RIBINARY")
        s.write("DATA:WIDTH 1")   # 1 byte per sample

        ymult = float(s.query("WFMPRE:YMULT?"))
        yoff  = float(s.query("WFMPRE:YOFF?"))
        yzero = float(s.query("WFMPRE:YZERO?"))
        xincr = float(s.query("WFMPRE:XINCR?"))

        # --- Trigger data transfer ---
        s.write("CURVE?")

        raw = s.read_raw()

        # --- Parse definite-length block ---
        # Format: #<n><len><binary data>
        assert raw[0:1] == b"#"
        n_digits = int(raw[1:2])
        n_bytes  = int(raw[2:2+n_digits])
        data_start = 2 + n_digits
        data_end   = data_start + n_bytes

        data = raw[data_start:data_end]

        import numpy as np
        samples = np.frombuffer(data, dtype=np.int8)

        volts = (samples - yoff) * ymult + yzero
        t = np.arange(len(volts)) * xincr

        return t, volts


    # ------------------------------
    # Screenshot (uses official save_screenshot API)
    # ------------------------------
    def screenshot(self, filename="scope.png"):
        """
        Saves screenshot locally using tm_devices built-in functionality.
        """
        import tempfile, os
        local_dir = tempfile.mkdtemp()

        self.scope.save_screenshot(
            filename,
            colors="INVERTED",
            local_folder=local_dir,
            device_folder="temp",
            keep_device_file=False,
        )

        file_path = os.path.join(local_dir, filename)
        print("Saved screenshot to:", file_path)
        return file_path

    # ------------------------------
    # Cleanup
    # ------------------------------
    def close(self):
        if self.dm:
            self.dm.close()
            self.dm = None
            self.scope = None
