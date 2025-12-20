import sys, os, time
import numpy as np
import matplotlib.pyplot as plt

# --- project imports ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from instruments.rigol_dg1062z import RigolDG1062Z
from instruments.tektronix_mso58 import TekMSO58


# ---------------------------------------------------------
# Measurement helpers
# ---------------------------------------------------------
def compute_amplitude(y):
    """Return peak amplitude from waveform."""
    return (np.max(y) - np.min(y)) / 2.0


def compute_phase(t, y, freq_hz):
    """
    Estimate phase from time-of-peak.
    crude but completely sufficient for a Bode sweep.
    """
    idx = np.argmax(y)
    t_peak = t[idx]
    return (t_peak * freq_hz * 360.0) % 360


# ---------------------------------------------------------
# Main sweep
# ---------------------------------------------------------
def main():

    RIGOL_ADDR = "10.59.133.252"   # <-- your Rigol
    TEK_ADDR   = "TCPIP0::10.59.133.248::inst0::INSTR"   # <-- your MSO58

    freqs = np.logspace(2, 4, num=15)  # 100 Hz → 10 kHz sweep
    drive_amplitude = 1.0  # Vpp

    # -----------------------------------------------------
    # Connect to instruments
    # -----------------------------------------------------
    print("Connecting to Rigol DG1062Z... at ", RIGOL_ADDR)
    rig = RigolDG1062Z(RIGOL_ADDR)
    rig.connect()
    print("Rigol:", rig.id())

    print("Connecting to Tektronix MSO58...")
    tek = TekMSO58(TEK_ADDR)
    tek.connect()

    # Ensure Tek is ready
    tek.channel_on(1)
    tek.autoset()

    amps = []
    phases = []

    print("\nStarting frequency sweep...\n")

    for f in freqs:
        print(f" → {f:.2f} Hz")

        # -------------------------------------------------
        # Configure Rigol output
        # -------------------------------------------------
        rig.configure_sine(
            channel=1,
            freq=f,
            amplitude=drive_amplitude,
            offset=0
        )
        rig.output_on(1)

        # allow scope to settle
        time.sleep(0.7)

        # -------------------------------------------------
        # Acquire waveform from Tek (your binary method)
        # -------------------------------------------------
        t, v = tek.acquire_waveform(1)

        # -------------------------------------------------
        # Compute Bode data
        # -------------------------------------------------
        amp = compute_amplitude(v)
        phase = compute_phase(t, v, f)

        amps.append(amp)
        phases.append(phase)

    rig.output_off(1)
    rig.close()
    tek.close()

    # ---------------------------------------------------------
    # Plot magnitude
    # ---------------------------------------------------------
    plt.figure(figsize=(10,6))
    plt.semilogx(freqs, 20*np.log10(np.array(amps)), marker='o')
    plt.grid(True, which='both')
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude (dB)")
    plt.title("Bode Plot – Magnitude")
    plt.show()

    # ---------------------------------------------------------
    # Plot phase
    # ---------------------------------------------------------
    plt.figure(figsize=(10,6))
    plt.semilogx(freqs, phases, marker='o')
    plt.grid(True, which='both')
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Phase (deg)")
    plt.title("Bode Plot – Phase")
    plt.show()


if __name__ == "__main__":
    main()
