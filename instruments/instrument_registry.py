from instruments.keysight_es36312 import KeysightE36312
from instruments.rigol_dg1062z import RigolDG1062Z
from instruments.tektronix_mso58 import TekMSO58
from instruments.keithley_2450 import Keithley2450
from instruments.ni_vb8034 import NIVirtualBench

INSTRUMENT_CLASSES = {
    "keysight_e36312":    KeysightE36312,
    "rigol_dg1062z":      RigolDG1062Z,
    "tektronix_mso58":    TekMSO58,
    "keithley_2450":      Keithley2450,  
    "ni_virtualbench": NIVirtualBench,
    "local": None
}
