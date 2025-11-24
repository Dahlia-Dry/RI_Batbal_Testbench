
from instrument_interface.config_loader import load_config

from instrument_interface.keysight_e36312 import KeysightE36312
from instrument_interface.tektronix_mso58 import TekMSO58
import matplotlib.pyplot as plt

config = load_config()

tek_ip = config["instruments"]["tektronix_mso58"]["ip"]
psu_ip = config["instruments"]["keysight_e36312"]["ip"]

scope = TekMSO58(tek_ip)
psu = KeysightE36312(psu_ip)

print("Connecting to Scope:", scope.connect())

# Setup scope
scope.autoset()
scope.set_channel_on(1)

# Acquire waveform
wave = scope.acquire_waveform(1)
print("Captured samples:", len(wave))

plt.plot(wave)
plt.title("Waveform from Tektronix MSO58 CH1")
plt.show()
