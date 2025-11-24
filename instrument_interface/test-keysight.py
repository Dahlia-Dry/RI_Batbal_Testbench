import pyvisa

def test():
    rm = pyvisa.ResourceManager()

    # Important: use your instrument's IP — you said:
    # TCPIP::10.59.133.254::inst0::INSTR

    psu = rm.open_resource("TCPIP::10.59.133.254::inst0::INSTR")

    print(psu.query("*IDN?"))