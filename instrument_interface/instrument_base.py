import pyvisa

class Instrument:
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.rm = pyvisa.ResourceManager()
        self.connection = None

    def connect(self):
        resource = f"TCPIP::{self.ip_address}::INSTR"
        self.connection = self.rm.open_resource(resource)
        print(f"Connected to {self.idn}")

    @property
    def idn(self):
        return self.query("*IDN?")

    def write(self, cmd):
        self.connection.write(cmd)

    def query(self, cmd):
        return self.connection.query(cmd)

    def close(self):
        if self.connection:
            self.connection.close()