# OSCILLOSCOPE
from instrument_base import Instrument

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
    
    