import pyvisa

def test():


    rm = pyvisa.ResourceManager()

    rigol = rm.open_resource("TCPIP::10.59.133.252::INSTR")

    print(rigol.query("*IDN?"))

test()