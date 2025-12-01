# tektronix_mso58.py
from tm_devices import DeviceManager
from instruments.tekscope_connection import preclean_visa_buffer
import numpy as np
import time
import pandas as pd
import matplotlib.pyplot as plt

class TekMSO58:
    supported_actions = ["setup_scope", "capture", "screenshot"]
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

        preclean_visa_buffer(self.address)

        self.dm = DeviceManager()
        self.scope = self.dm.add_scope(self.address, alias=self.alias)

        return self.scope.query("*IDN?")

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
        self.scope.commands.display.waveview1.ch[ch].state.write("ON")

    def channel_off(self, ch):
        self.scope.commands.display.waveview1.ch[ch].state.write("OFF")

    # ------------------------------
    # Manual setup
    # ------------------------------

    def setup_scope(self, trigger, channels):
        # Trigger
        trig_type = trigger.get("type", "edge").upper()
        trig_source = trigger.get("source", "CH1")
        trig_level = trigger.get("level", 1.0)

        # Example SCPI for Tektronix MSO5/MSO6
        #print(dir(self.scope.commands.trigger))
        self.scope.commands.trigger.a.type.write(trig_type)
        #self.scope.commands.trigger.level.write(trig_level)
        #self.scope.commands.trigger.source.write(trig_source)
        self.write(f"TRIGGER:A:LEVEL {trig_level}")
        self.write(f"TRIGGER:A:EDGE:SOURCE {trig_source}")

        # Channel settings
        for ch, cfg in channels.items():
            scale = cfg.get("scale", None)
            position = cfg.get("position", None)

            if scale is not None:
                self.scope.commands.ch[ch].scale.write(scale)
            if position is not None:
                self.scope.commands.ch[ch].position.write(scale)

    # ------------------------------
    # Waveform Acquisition
    # Uses curve_query() — VERIFIED in repo
    # ------------------------------
    def capture(self, channels, duration, save_to=None, sample_rate=None, show_plot=False):
        #self.scope.commands.acquire.state.write("OFF")
        self.scope.commands.acquire.mode.write("SAMPLE")
        self.scope.commands.acquire.stopafter.write("SEQUENCE")

        self.write("HOR:MODE MANUAL")
        self.write(f"HOR:MAIN:SCALE {duration / 10}")

        if sample_rate:
            record_length = int(duration * sample_rate)
            self.write(f"HORIZONTAL:RECORDLENGTH {record_length}")
        
        self.scope.commands.acquire.state.write("RUN")

        # Give the scope enough time to acquire
        # Wait until acquisition stops (e.g., in SEQUENCE mode)
        while int(self.scope.commands.acquire.state.query()) != 0:
            time.sleep(0.5)

        curve_returned = self.scope.curve_query(1, output_csv_file="test.csv")

        datafile = pd.DataFrame()

        for ch in channels:
            # --- Configure binary waveform transfer ---
            self.write(f"DATA:SOURCE CH{ch}")
            self.write("DATA:ENC RIBINARY")
            self.write("DATA:WIDTH 1")   # 1 byte per sample

            ymult = float(self.query("WFMPRE:YMULT?"))
            yoff  = float(self.query("WFMPRE:YOFF?"))
            yzero = float(self.query("WFMPRE:YZERO?"))
            xincr = float(self.query("WFMPRE:XINCR?"))

            # --- Trigger data transfer ---
            self.write("CURVE?")

            raw = self.scope.read_raw()

            # --- Parse definite-length block ---
            # Format: #<n><len><binary data>
            assert raw[0:1] == b"#"
            n_digits = int(raw[1:2])
            n_bytes  = int(raw[2:2+n_digits])
            data_start = 2 + n_digits
            data_end   = data_start + n_bytes

            data_raw = raw[data_start:data_end]

            samples = np.frombuffer(data_raw, dtype=np.int8)

            data_offset = (samples - yoff) * ymult + yzero
            datafile["t"] = np.arange(len(data_offset)) * xincr
            datafile[f"data_ch{ch}"] = data_offset



        if save_to is not None:
            datafile.to_csv(save_to)

        if show_plot:
            #fig=plt.figure()
            plt.scatter(x=datafile["t"],y=datafile["data_ch1"])
            plt.show()
        return datafile 


        
    def record_to_csv_binary(self, channels, duration, output_file=False, sample_rate=None):
        # 1. Timebase settings so the duration fits the screen (10 divisions)
        self.write("HOR:MODE MANUAL")
        self.write(f"HOR:MAIN:SCALE {duration / 10}")

        # 2. Configure record length
        if sample_rate:
            record_length = int(duration * sample_rate)
            self.write(f"HORIZONTAL:RECORDLENGTH {record_length}")
        # else: auto-select record length

        # 3. Run a single sequence acquisition
        self.write("ACQUIRE:STOPAFTER SEQUENCE")
        self.write("ACQUIRE:STATE RUN")

        # Give the scope enough time to acquire
        time.sleep(duration * 1.2)

        # Stop acquisition before reading
        self.write("ACQUIRE:STATE STOP")

        datafile = pd.DataFrame()

        for ch in channels:
            # --- Configure binary waveform transfer ---
            self.write(f"DATA:SOURCE CH{ch}")
            self.write("DATA:ENC RIBINARY")
            self.write("DATA:WIDTH 1")   # 1 byte per sample

            ymult = float(self.query("WFMPRE:YMULT?"))
            yoff  = float(self.query("WFMPRE:YOFF?"))
            yzero = float(self.query("WFMPRE:YZERO?"))
            xincr = float(self.query("WFMPRE:XINCR?"))

            # --- Trigger data transfer ---
            self.write("CURVE?")

            raw = self.scope.read_raw()

            # --- Parse definite-length block ---
            # Format: #<n><len><binary data>
            assert raw[0:1] == b"#"
            n_digits = int(raw[1:2])
            n_bytes  = int(raw[2:2+n_digits])
            data_start = 2 + n_digits
            data_end   = data_start + n_bytes

            data_raw = raw[data_start:data_end]

            samples = np.frombuffer(data_raw, dtype=np.int8)

            data_offset = (samples - yoff) * ymult + yzero
            datafile["t"] = np.arange(len(data_offset)) * xincr
            datafile[f"data_ch{ch}"] = data_offset

        if output_file is not None:
            datafile.to_csv(output_file)

        return datafile 


    # ------------------------------
    # Screenshot (uses official save_screenshot API)
    # ------------------------------
    def screenshot(self, save_to="scope.png"):
        """
        Saves screenshot locally using tm_devices built-in functionality.
        """

        self.scope.save_screenshot(
            save_to,
            colors="INVERTED",
            keep_device_file=False,
        )

        return

    # ------------------------------
    # Cleanup
    # ------------------------------
    def close(self):
        if self.dm:
            self.dm.close()
            self.dm = None
            self.scope = None
