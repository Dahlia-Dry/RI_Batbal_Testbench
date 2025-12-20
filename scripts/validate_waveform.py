import csv
import math

# Provided automatically by step dispatcher
data = input_data
print(data)

csv_file = data["file"]
scope_meas = data["measurements"]

scope_vmax = scope_meas["maximum"]
scope_vmin = scope_meas["minimum"]
scope_freq = scope_meas["frequency"]

times = []
values = []

with open(csv_file, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        times.append(float(row["t"]))
        values.append(float(row["CH1"]))

csv_vmax = max(values)
csv_vmin = min(values)


# Tolerances
V_TOL = 0.05   # 50 mV

vmax_ok = abs(csv_vmax - scope_vmax) <= V_TOL
vmin_ok = abs(csv_vmin - scope_vmin) <= V_TOL

print("Scope vs CSV comparison:")
print(f"  Vmax: scope={scope_vmax:.3f}, csv={csv_vmax:.3f}, ok={vmax_ok}")
print(f"  Vmin: scope={scope_vmin:.3f}, csv={csv_vmin:.3f}, ok={vmin_ok}")

if vmax_ok and vmin_ok:
    print("PASS: Waveform validation successful")
    OUTPUT = {"result": 1}
else:
    print("FAIL: Waveform validation failed")
    OUTPUT = {"result": 0}
