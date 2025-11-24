import pyvisa

class Instrument:
    def __init__(self, ip_address, timeout=5000):
        self.ip = ip_address
        self.rm = pyvisa.ResourceManager()
        self.timeout = timeout
        self.inst = None

    def connect(self):
        resource = f"TCPIP::{self.ip}::INSTR"
        print(resource)
        self.inst = self.rm.open_resource(resource)
        self.inst.timeout = self.timeout
        return self.query("*IDN?")

    def write(self, cmd):
        if self.inst is None:
            raise RuntimeError("Instrument not connected.")
        self.inst.write(cmd)

    def query(self, cmd):
        if self.inst is None:
            raise RuntimeError("Instrument not connected.")
        return self.inst.query(cmd).strip()

    def close(self):
        if self.inst:
            self.inst.close()
            self.inst = None