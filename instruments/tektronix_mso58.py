from tm_devices import DeviceManager
import pyvisa
import numpy as np
import time
import pandas as pd
import matplotlib.pyplot as plt

class TekMSO58:
    """
    TekMSO58 driver implemented using tm_devices.
    
    """

    def __init__(self, address, alias="SCOPE1"):
        self.address = address
        self.alias = alias
        self.dm = None
        self.scope = None

    def connect(self):
        print(f"Connecting to Tektronix MSO58 at {self.address}...")

        self.preclean_visa_buffer()

        self.dm = DeviceManager()
        self.scope = self.dm.add_scope(self.address, alias=self.alias)

        return self.scope.query("*IDN?")
    
    def preclean_visa_buffer(self):
        """
        Prevents intermittent DeviceManager.add_scope() failures by
        clearing any leftover binary output in the Tektronix VISA buffer
        before tm_devices tries to auto-detect the driver.
        """
        rm = pyvisa.ResourceManager()
        try:
            inst = rm.open_resource(self.address, timeout=1000)
        except Exception:
            return  # If Tek isn't reachable yet, let tm_devices deal with it

        try:
            # Drain every unread byte
            while True:
                try:
                    inst.read_raw()
                except Exception:
                    break

            # VISA clear
            try:
                inst.clear()
            except Exception:
                pass

        finally:
            try:
                inst.close()
            except Exception:
                pass

    # ------------------------------
    # Basic SCPI passthrough
    # ------------------------------
    def write(self, cmd):
        self.scope.write(cmd)

    def query(self, cmd):
        return self.scope.query(cmd)

    # Channel controls
    def channel_on(self, ch):
        self.scope.commands.display.waveview1.ch[ch].state.write("ON")

    def channel_off(self, ch):
        self.scope.commands.display.waveview1.ch[ch].state.write("OFF")

    # Manual setup

    def configure_scope(self, trigger, channels, timebase=None, measurements=None):
        TEK_MEASUREMENT_MAP = {
            # Voltage
            "vpp":        "PK2Pk",
            "vmax":       "MAXimum",
            "vmin":       "MINimum",
            "vtop":       "TOP",
            "vbase":      "BASE",
            "vamp":       "AMPlitude",
            "vrms":       "RMS",
            "vmean":      "MEAN",
            # Time / Frequency
            "freq":       "FREQuency",
            "period":     "PERiod",
            "duty":       "DUTY",
            "poswidth":   "PWIDTH",
            "negwidth":   "NWIDTH",
            # Edges
            "rise":       "RISE",
            "fall":       "FALL",
            # Signal quality
            "overshoot":  "OVERSHOOT",
            "preshoot":   "PRESHOOT",
        }

        # Trigger
        trig_type = trigger.get("type", "edge").upper()
        trig_source = trigger.get("source", "CH1")
        trig_level = trigger.get("level", 1.0)

        # Tektronix MSO5/MSO6 trigger configuration
        self.scope.commands.trigger.a.type.write(trig_type)
        self.write(f"TRIGGER:A:LEVEL {trig_level}")
        self.write(f"TRIGGER:A:EDGE:SOURCE {trig_source}")

        # Channels
        for ch, cfg in channels.items():
            self.write(f"SELECT:{ch} ON")

            scale = cfg.get("scale")
            position = cfg.get("position")

            if scale is not None:
                self.scope.commands.ch[ch].scale.write(scale)

            if position is not None:
                self.scope.commands.ch[ch].position.write(position)

        # Timebase (optional)
        if timebase:
            tb_scale = timebase.get("scale")
            tb_position = timebase.get("position")

            if tb_scale is not None:
                self.scope.commands.horizontal.scale.write(tb_scale)

            if tb_position is not None:
                self.scope.commands.horizontal.position.write(tb_position)

        # Measurements (optional)
        for idx in range(1, 9):  # MEAS1..MEAS8
            self.write(f"MEASUrement:MEAS{idx}:STATE OFF")
            self.write(f"MEASUrement:MEAS{idx}:DELETE")
        self.write("DISPlay:MEASurement:STATE OFF")

        if measurements:
            for idx, meas in enumerate(measurements, start=1):
                meas_type = TEK_MEASUREMENT_MAP[meas.get("type")]
                source = meas.get("source")

                if not meas_type or not source:
                    continue

                # Example: MEASUrement:MEAS1:TYPE PK2Pk
                self.write(f"MEASUrement:MEAS{idx}:TYPE {meas_type.upper()}")
                self.write(f"MEASUrement:MEAS{idx}:SOURCE1 {source}")

        # Return active configuration
        return {
            "trigger": {
                "type": trig_type.lower(),
                "level": trig_level,
                "source": trig_source,
            },
            "channels": channels,
            "timebase": timebase,
            "measurements": measurements,
        }

    # Waveform Acquisition
    def capture(self, channels, duration, save_to=None, sample_rate=None, show_plot=False):
        self.scope.commands.acquire.state.write("OFF")
        self.scope.commands.acquire.mode.write("SAMPLE")
        self.scope.commands.acquire.stopafter.write("SEQUENCE")

        self.write("HOR:MODE MANUAL")
        self.write(f"HOR:MAIN:SCALE {duration}")

        if sample_rate:
            record_length = int(duration * sample_rate)
            self.write(f"HORIZONTAL:RECORDLENGTH {record_length}")

        datafile = pd.DataFrame()

        for ch in channels:
            print(f"Acquiring ch {ch}")

            self.write(f"DATA:SOURCE CH{ch}")
            self.write("DATA:ENC SRIbinary")
            self.write("DATA:WIDTH 2")

            self.write("ACQ:STOPAfter SEQ")
            self.write("ACQ:STATE ON")

            while int(self.query("ACQ:STATE?")) != 0:
                time.sleep(0.1)

            self.write("ACQ:STATE OFF")
            time.sleep(0.05)

            ymult = float(self.query("WFMPRE:YMULT?"))
            yoff  = float(self.query("WFMPRE:YOFF?"))
            yzero = float(self.query("WFMPRE:YZERO?"))
            xincr = float(self.query("WFMPRE:XINCR?"))

            self.write("CURVE?")
            raw = self.scope.read_raw()

            assert raw[0:1] == b"#"
            ndigits = int(raw[1:2])
            nbytes  = int(raw[2:2+ndigits])
            start = 2 + ndigits
            end   = start + nbytes

            buf = raw[start:end]
            samples = np.frombuffer(buf, dtype="<i2")
            volts = (samples - yoff) * ymult + yzero
            t = np.arange(len(volts)) * xincr

            datafile["t"] = t
            datafile[f"{ch}"] = volts

        if save_to is not None:
            datafile.to_csv(save_to)

        if show_plot:
            plt.plot(datafile["t"], datafile[f"{channels[0]}"])
            plt.show()

        # Retrieve configured measurements
        measurements = {}

        for idx in range(1, 9):  # Tek supports MEAS1..MEAS8
            try:
                mtype = self.query(f"MEASUrement:MEAS{idx}:TYPE?").strip().lower()
                if mtype in ("", "none"):
                    continue

                value = float(self.query(f"MEASUrement:MEAS{idx}:VALue?"))
                measurements[mtype] = value
            except Exception:
                # Ignore unused or unsupported measurement slots
                pass

        # Return structured capture info
        return {
            "channels": channels,
            "duration": duration,
            "file": save_to,
            "num_channels": len(channels),
            "samples_per_channel": {
                ch: len(datafile[f"{ch}"]) for ch in channels
            },
            "measurements": measurements,
        }


    # Screenshot
    def screenshot(self, save_to="scope.png"):
        """
        Saves screenshot locally using tm_devices built-in functionality.
        """

        self.scope.save_screenshot(
            save_to,
            colors="INVERTED",
            keep_device_file=False,
        )

        return {
            "file": save_to,
            "colors": "INVERTED",
        }

    # ------------------------------
    # Cleanup
    # ------------------------------
    def close(self):
        if self.dm:
            self.dm.close()
            self.dm = None
            self.scope = None
