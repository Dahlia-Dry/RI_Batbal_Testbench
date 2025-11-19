# OSCILLOSCOPE
from instrument_base import Instrument
import pyvisa

class TektronixMSO58(Instrument):
    def autoset(self):
        self.write("AUTOS EXEC")
    
    def measure_vpp(self, channel=1):
        return self.query(f"MEASU:MEAS{channel}:VAL?")
    
    def acquire_waveform(self, channel=1):
        self.write(f"DATA:SOU CH{channel}")
        self.write("DATA:ENC ASC")
        data = self.query("CURV?")
        return [float(v) for v in data.split(",")]
    
def test():
    rm = pyvisa.ResourceManager()

    scope = rm.open_resource("TCPIP::10.59.133.248::INSTR")

    print(scope.query("*IDN?"))

test()