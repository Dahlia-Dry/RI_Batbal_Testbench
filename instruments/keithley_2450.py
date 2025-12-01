# Source Meter Unit (SMU)
import pyvisa

def test():

    rm = pyvisa.ResourceManager()

    smu = rm.open_resource("TCPIP::10.59.133.251::inst0::INSTR")
    print(smu.query("*IDN?"))

test()