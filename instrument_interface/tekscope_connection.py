import pyvisa
from tm_devices import DeviceManager


def preclean_visa_buffer(resource):
    """
    Prevents intermittent DeviceManager.add_scope() failures by
    clearing any leftover binary output in the Tektronix VISA buffer
    before tm_devices tries to auto-detect the driver.

    This eliminates:
        VI_ERROR_TMO ... clear_visa_output_buffer_and_get_idn()
    """
    rm = pyvisa.ResourceManager()
    try:
        inst = rm.open_resource(resource, timeout=1000)
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


class TekScopeConnectionManager:
    """
    Safe, reliable wrapper around tm_devices TekScope drivers.
    Automatically:
      • pre-cleans VISA buffer
      • opens DeviceManager
      • connects to the proper TekScope driver
      • exposes the scope object safely
    """

    def __init__(self, resource, alias="SCOPE1"):
        self.resource = resource
        self.alias = alias
        self.dm = None
        self.scope = None

    # -----------------------------------------------------------
    # CONNECT
    # -----------------------------------------------------------
    def connect(self):
        print(f"Connecting to Tektronix scope @ {self.resource} ...")

        # 🔥 eliminate random timeouts
        preclean_visa_buffer(self.resource)

        # connect with tm_devices
        self.dm = DeviceManager()
        self.scope = self.dm.add_scope(self.resource, alias=self.alias)

        idn = self.scope.query("*IDN?")
        print("Connected:", idn)
        return self.scope

    # -----------------------------------------------------------
    # DISCONNECT
    # -----------------------------------------------------------
    def close(self):
        if self.scope:
            try:
                self.scope.close()
            except Exception:
                pass
        if self.dm:
            try:
                self.dm.close()
            except Exception:
                pass

    # -----------------------------------------------------------
    # CONTEXT MANAGER (optional convenience)
    # -----------------------------------------------------------
    def __enter__(self):
        self.connect()
        return self.scope

    def __exit__(self, exc_type, exc, tb):
        self.close()
