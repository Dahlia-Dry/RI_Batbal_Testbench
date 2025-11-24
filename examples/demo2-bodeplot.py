import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

import numpy as np
import matplotlib.pyplot as plt
import time

from instrument_interface.rigol_dg1062z import RigolDG1062Z
from instrument_interface.tektronix_mso58 import TekMSO58
from instrument_interface.config_loader import load_config


def measure_amplitude_and_phase(t, v_in, v_out):
    """Return (gain, phase_deg) based on cross-correlation."""
    # amplitude = half peak-to-peak
    A_in = (np.max(v_in) - np.min(v_in)) / 2
    A_out = (np.max(v_out) - np.min(v_out)) / 2
    gain = A_out / A_in if A_in != 0 else np.nan

    # Phase via cross-correlation
    c = np.correlate(v_out - np.mean(v_out), v_in - np.mean(v_in), mode="full")
    delay_idx = np.argmax(c) - (len(v_in) - 1)
    dt = t[1] - t[0]
    delay_time = delay_idx * dt
    freq = 1 / (t[-1] - t[0])  # rough estimate (1 cycle in capture)

    phase_deg = -delay_time * freq * 360
    return gain, phase_deg


def main():
    config = load_config()

    rigol_ip = config["instruments"]["rigol_dg1062z"]["ip"]
    tek_ip   = config["instruments"]["tektronix_mso58"]["ip"]

    # ---------------------------
    # Connect instruments
    # ---------------------------
    print("Connecting instruments...")
    rigol = RigolDG1062Z(rigol_ip)
    rigol.connect()

    tek = TekMSO58(f"TCPIP::{tek_ip}::INSTR")
    tek.connect()

    # ---------------------------
    # Frequency sweep parameters
    # ---------------------------
    freqs = np.logspace(1, 5, 30)  # 10 Hz → 100 kHz, 30 points
    amplitude = 1.0  # Vpp
    results_gain = []
    results_phase = []

    print("Starting frequency sweep...")

    for f in freqs:
        print(f"\n--- Frequency = {f:.1f} Hz ---")

        # Signal generator settings
        rigol.configure_sine(channel=1, freq=f, amplitude=amplitude)
        rigol.output_on(1)
        time.sleep(0.1)

        # Scope autoset at first frequency
        if f == freqs[0]:
            tek.autoset()

        # Acquire waveform
        t, ch1 = tek.acquire_waveform(1)
        _, ch2 = tek.acquire_waveform(2)

        gain, phase = measure_amplitude_and_phase(t, ch1, ch2)
        results_gain.append(gain)
        results_phase.append(phase)

    rigol.output_off(1)
    tek.close()

    # ---------------------------
    # Plot Bode diagram
    # ---------------------------
    fig, ax1 = plt.subplots()

    # Magnitude (gain)
    ax1.set_xscale("log")
    ax1.set_xlabel("Frequency (Hz)")
    ax1.set_ylabel("Gain (V/V)", color="tabblue")
    ax1.plot(freqs, results_gain, "-o")
    ax1.grid(True, which="both")

    # Phase
    ax2 = ax1.twinx()
    ax2.set_ylabel("Phase (deg)", color="tab:red")
    ax2.plot(freqs, results_phase, "r^-")

    plt.title("Bode Plot — Automated via Rigol + Tektronix MSO58")
    plt.show()


if __name__ == "__main__":
    main()
