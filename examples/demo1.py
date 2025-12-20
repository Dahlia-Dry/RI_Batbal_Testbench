#WORKING
# captures the waveform currently displayed on the screen and plots it
import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
import matplotlib.pyplot as plt
from instruments.tektronix_mso58 import TekMSO58

def main():

    # Your Tek IP
    TEK_IP = "TCPIP0::10.59.133.248::inst0::INSTR"

    tek = TekMSO58(TEK_IP)
    tek.connect()

    # Turn CH1 on and autoscale
    #tek.channel_on(1)
    #tek.autoset()

    print("Acquiring waveform...")
    t, v = tek.acquire_waveform(1)

    # Plot
    plt.plot(t, v)
    plt.title("Tektronix MSO58 Waveform")
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (V)")
    plt.grid(True)
    plt.show()

    tek.close()

if __name__ == "__main__":
    main()
