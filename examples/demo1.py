import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from instrument_interface.rigol_dg1062z import RigolDG1062Z
from instrument_interface.tektronix_mso58 import TekMSO58
from instrument_interface.config_loader import load_config
import matplotlib.pyplot as plt

def main():

    config = load_config()
    rigol_ip = config["instruments"]["rigol_dg1062z"]["ip"]
    tek_ip   = config["instruments"]["tektronix_mso58"]["ip"]

    # -------------------------
    # Connect to instruments
    # -------------------------
    rigol = RigolDG1062Z(rigol_ip)
    rigol.connect()

    tek = TekMSO58(f"TCPIP::{tek_ip}::INSTR")
    tek.connect()

    # -------------------------
    # Configure Rigol output
    # -------------------------
    rigol.configure_sine(channel=1, freq=200, amplitude=2.0)
    rigol.output_on(1)

    # -------------------------
    # Configure scope
    # -------------------------
    tek.set_channel_on(1)
    tek.autoset()

    # -------------------------
    # Acquire waveform
    # -------------------------
    t, v = tek.acquire_waveform(1)

    # -------------------------
    # Plot
    # -------------------------
    plt.plot(t, v)
    plt.title("Rigol → Tektronix MSO58")
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (V)")
    plt.show()

    rigol.output_off(1)
    tek.close()

if __name__ == "__main__":
    main()
