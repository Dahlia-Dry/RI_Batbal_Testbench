from pymeasure.instruments.ni import VirtualBench

class NIVirtualBench:
    """
    NI VirtualBench wrapper using PyMeasure.

    Supported subsystems:
      - Power Supply (PSU)
      - Digital IO (DIO)
    """

    def __init__(self, resource):
        self.resource = resource
        self.vb = None

    # ============================================================
    # Session / common
    # ============================================================

    def connect(self):
        self.vb = VirtualBench(self.resource)
        return self.resource

    def close(self):
        if self.vb:
            self.vb.shutdown()
            self.vb = None

    def vb_identify(self):
        return {
            "model": self.vb.model,
            "serial": self.vb.serial_number,
        }

    # ============================================================
    # Power Supply (PSU)
    # ============================================================

    def vb_psu_configure(self, channel, voltage=None, current_limit=None, output_enabled=False):
        psu = self.vb.PowerSupply
        psu.channel = channel

        if voltage is not None:
            psu.voltage = voltage

        if current_limit is not None:
            psu.current_limit = current_limit

        psu.enabled = output_enabled

        return {
            "channel": channel,
            "voltage": psu.voltage,
            "current_limit": psu.current_limit,
            "output_enabled": psu.enabled,
        }

    def vb_psu_set_power(self, channel, voltage, current_limit):
        psu = self.vb.PowerSupply
        psu.channel = channel

        psu.voltage = voltage
        psu.current_limit = current_limit
        psu.enabled = True

        return {
            "channel": channel,
            "voltage": voltage,
            "current_limit": current_limit,
            "output_enabled": True,
        }

    def vb_psu_enable(self, channel, enable=True):
        psu = self.vb.PowerSupply
        psu.channel = channel
        psu.enabled = enable

        return {
            "channel": channel,
            "output_enabled": enable,
        }

    # ============================================================
    # Digital IO
    # ============================================================
    def _format_dio_lines(self, lines):
        """
        Convert list of DIO line indices into NI channel string.
        Example: [0,1,2,3] -> 'dig/0:3'
        """
        if isinstance(lines, str):
            return lines

        if not isinstance(lines, (list, tuple)):
            raise ValueError("DIO lines must be list, tuple, or string")

        if not lines:
            raise ValueError("DIO lines list cannot be empty")

        lines = sorted(lines)

        if lines == list(range(lines[0], lines[-1] + 1)):
            return f"dig/{lines[0]}:{lines[-1]}"
        else:
            joined = ",".join(str(i) for i in lines)
            return f"dig/{joined}"

    def vb_dio_configure(self, lines, direction):
        line_str = self._format_dio_lines(lines)
        self.vb.acquire_digital_input_output(line_str, reset=False)
        return {
            "lines": lines,
            "direction": direction,
        }

    def vb_dio_write(self, lines, values):
        line_str = self._format_dio_lines(lines)

        if not isinstance(values, (list, tuple)):
            raise ValueError("DIO write values must be a list or tuple")

        if len(values) != len(lines):
            raise ValueError(
                f"DIO write length mismatch: {len(values)} values for {len(lines)} lines"
            )

        # Convert to booleans, preserve order
        bool_values = [bool(int(v)) for v in values]

        self.vb.dio.write(line_str, bool_values)

        return {
            "lines": lines,
            "values": bool_values,
        }


    def vb_dio_read(self, lines):
        line_str = self._format_dio_lines(lines)

        values = self.vb.dio.read(line_str)

        # values is already ordered
        return {
            "lines": lines,
            "values": list(values),
        }

