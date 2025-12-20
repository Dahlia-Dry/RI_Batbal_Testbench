import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
#from instrument_interface.rigol_dg1062z import RigolDG1062Z
import pyvisa 
 
addr = "10.59.133.252"  # <-- whatever you're using

print("Connecting...")
rigol = pyvisa.ResourceManager().open_resource(f"TCPIP::{addr}::INSTR")
print("Rigol:", rigol.query("*IDN?"))

