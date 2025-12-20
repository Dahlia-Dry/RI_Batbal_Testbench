import pyvisa
import time

rm = pyvisa.ResourceManager()
inst = rm.open_resource("TCPIP::10.59.31.166::5025::SOCKET")
inst.read_termination = "\n"
inst.write_termination = "\n"
inst.timeout = 10000

# HARD RESET OF EXECUTION STATE
inst.write("abort")
time.sleep(0.2)
inst.write("reset()")
inst.write("errorqueue.clear()")

# Force trigger model idle
inst.write("smu.trigger.abort()")

# Configure
inst.write("smu.source.func = smu.FUNC_DC_VOLTAGE")
inst.write("smu.source.level = 1.0")
inst.write("smu.source.ilimit = 0.01")
inst.write("smu.measure.func = smu.FUNC_DC_CURRENT")
inst.write("smu.output = smu.ON")

# 🔑 CRITICAL: force trigger idle again
inst.write("smu.trigger.abort()")

# Measure
inst.write("print(smu.measure.read())")
print("Reply:", inst.read())

inst.write("smu.output = smu.OFF")
