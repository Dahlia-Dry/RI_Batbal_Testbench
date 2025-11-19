import pyvisa

def discover_instruments():
    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()
    found = []

    for res in resources:
        if not res.startswith("TCPIP"):
            continue
        try:
            inst = rm.open_resource(res)
            idn = inst.query("*IDN?").strip()
            found.append((res, idn))
            inst.close()
        except Exception as e:
            print(f"Could not query {res}: {e}")
    return found


def classify_instruments(instruments):
    known = {
        "TEKTRONIX": "Oscilloscope (Tektronix MSO58)",
        "KEYSIGHT": "Power Supply (E36312)",
        "RIGOL": "Waveform Generator (DG1062Z)",
        "NATIONAL INSTRUMENTS": "VirtualBench (VB8034)",
        "KEITHLEY": "Source Meter Unit (2450)",
    }

    result = {v: [] for v in known.values()}

    for res, idn in instruments:
        for key, label in known.items():
            if key in idn.upper():
                result[label].append((res, idn))
                break
        else:
            result.setdefault("Unknown", []).append((res, idn))

    return result


if __name__ == "__main__":
    print("Scanning LAN for instruments...\n")
    instruments = discover_instruments()
    classified = classify_instruments(instruments)

    for category, items in classified.items():
        print(f"\n instrument {category}:")
        if not items:
            print("  (none found)")
        for res, idn in items:
            print(f"  • {idn}  —  {res}")