import os
import platform
import subprocess
import socket

# ---- 1. Ping test ----
def ping(ip):
    param = "-n" if platform.system().lower()=="windows" else "-c"
    return subprocess.call(
        ["ping", param, "1", ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    ) == 0


# ---- 2. Test raw SCPI socket (port 5025) ----
def scpi_socket(ip, port=5025):
    try:
        s = socket.socket()
        s.settimeout(0.3)
        s.connect((ip, port))
        s.send(b"*IDN?\n")
        data = s.recv(1024).decode(errors="ignore").strip()
        s.close()
        if data:
            return data
    except:
        return None


# ---- 3. Test VXI-11 (optional but recommended) ----
def vxi11_query(ip):
    try:
        import vxi11
        dev = vxi11.Instrument(ip, timeout=0.5)
        return dev.ask("*IDN?").strip()
    except:
        return None


# ---- 4. Test HiSLIP (port 4880) ----
def hislip_query(ip, port=4880):
    try:
        s = socket.socket()
        s.settimeout(0.3)
        s.connect((ip, port))
        # HiSLIP handshake will fail normally, but we test port alive
        s.close()
        return True
    except:
        return False


# ---- 5. Main scanner ----
def scan_subnet(base="10.59.31."):
    print(f"Scanning subnet {base}0/24...\n")
    for i in range(1, 255):
        ip = base + str(i)

        # Step 1 – Check if host is alive
        if not ping(ip):
            continue

        # Step 2 – Try SCPI socket
        idn = scpi_socket(ip)
        if idn:
            print(f"📡 SCPI device at {ip}:  {idn}")
            continue

        # Step 3 – Try VXI-11
        idn = vxi11_query(ip)
        if idn:
            print(f"📡 VXI-11 device at {ip}: {idn}")
            continue

        # Step 4 – Try HiSLIP port
        if hislip_query(ip):
            print(f"📡 Device at {ip} responds on HiSLIP (but *IDN?* failed)")

    print("\nScan complete.")


# ---- run it ----
scan_subnet("10.59.31.")