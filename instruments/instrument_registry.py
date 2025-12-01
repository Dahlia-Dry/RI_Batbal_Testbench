from keysight_es36312 import KeysightE36312
from rigol_dg1062z import RigolDG1062Z
from tektronix_mso58 import TekMSO58

INSTRUMENT_CLASSES = {
    "keysight_e36312":    KeysightE36312,
    "rigol_dg1062z":      RigolDG1062Z,
    "tektronix_mso58":    TekMSO58,
    "keithley_2450":      Instrument,  # TODO: write your driver
}
