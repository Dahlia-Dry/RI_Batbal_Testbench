# rigol_dg1062z.py
import pyvisa


class RigolDG1062Z:
    """
    Standalone driver for Rigol DG1062Z signal generator.
    Uses pyVISA with TCPIP::<IP>::INSTR (VXI-11), which you verified works.
    """

    def __init__(self, ip, timeout=5000):
        self.ip = ip
        self.timeout = timeout
        self.rm = pyvisa.ResourceManager()
        self.inst = None

    # -------------------------------
    # Connection
    # -------------------------------
    def connect(self):
        resource = f"TCPIP::{self.ip}::INSTR"
        print(f"Connecting to Rigol at {resource} ...")
        self.inst = self.rm.open_resource(resource)
        self.inst.timeout = self.timeout

        idn = self.query("*IDN?")
        print("Connected:", idn)
        return idn

    def close(self):
        if self.inst:
            self.inst.close()
            self.inst = None

    # -------------------------------
    # Core SCPI IO
    # -------------------------------
    def write(self, cmd):
        if self.inst is None:
            raise RuntimeError("Rigol not connected.")
        self.inst.write(cmd)

    def query(self, cmd):
        if self.inst is None:
            raise RuntimeError("Rigol not connected.")
        return self.inst.query(cmd).strip()

    # -------------------------------
    # Waveform configuration
    # -------------------------------
    def set_function(self, channel, func):
        self.write(f"SOUR{channel}:FUNC {func}")

    def set_frequency(self, channel, freq_hz):
        self.write(f"SOUR{channel}:FREQ {freq_hz}")

    def set_amplitude(self, channel, volts_pkpk):
        self.write(f"SOUR{channel}:VOLT {volts_pkpk}")

    def set_offset(self, channel, offset_v):
        self.write(f"SOUR{channel}:VOLT:OFFS {offset_v}")

    def output_on(self, channel):
        self.write(f"OUTP{channel} ON")

    def output_off(self, channel):
        self.write(f"OUTP{channel} OFF")

    # -------------------------------
    # Composite helper (no changes needed)
    # -------------------------------
    def configure_sine(self, channel, freq, amplitude, offset=0):
        self.set_function(channel, "SIN")
        self.set_frequency(channel, freq)
        self.set_amplitude(channel, amplitude)
        self.set_offset(channel, offset)

    # -------------------------------
    # Load settings
    # -------------------------------
    def high_impedance_mode(self, channel):
        self.write(f"OUTP{channel}:LOAD INF")

    def fifty_ohm_mode(self, channel):
        self.write(f"OUTP{channel}:LOAD 50")

    # -------------------------------
    # IDN
    # -------------------------------
    def id(self):
        return self.query("*IDN?")
