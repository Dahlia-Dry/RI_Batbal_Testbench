from tm_devices.drivers.scopes.tekscope.mso5b import MSO5B


class TekMSO58:
    """
    Tektronix MSO58 scope using tm_devices.
    Does NOT inherit from Instrument because:
    - MSO58 does not use PyVISA
    - tm_devices handles all communication internally
    """

    def __init__(self, address: str):
        self.address = address
        self._scope: MSO5B | None = None

    # -------------------------
    # CONNECTION
    # -------------------------
    def connect(self):
        print(f"Connecting to Tektronix MSO58 at {self.address}...")
        self._scope = MSO5B(self.address)
        print("Connected:", self._scope.idn)
        return self._scope.idn

    def close(self):
        if self._scope:
            self._scope.close()
            self._scope = None

    # -------------------------
    # BASIC CONTROLS
    # -------------------------
    def autoset(self):
        self._scope.auto_set()

    def set_channel_on(self, ch: int):
        self._scope.channels[f"CH{ch}"].state = "ON"

    def set_channel_off(self, ch: int):
        self._scope.channels[f"CH{ch}"].state = "OFF"

    # -------------------------
    # WAVEFORM ACQUISITION
    # -------------------------
    def acquire_waveform(self, channel: int = 1):
        """
        Returns:
            times (numpy array)
            volts (numpy array)
        """
        ch = self._scope.channels[f"CH{channel}"]
        wf = ch.read_waveform()    # Already parsed by tm_devices
        return wf.times, wf.volts
