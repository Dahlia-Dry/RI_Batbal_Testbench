# tektronix_mso58_tmdevices.py
"""
Robust Tektronix MSO58 extender that uses tm_devices DeviceManager.
- Uses DeviceManager.add_scope() to create device.
- Detects whether the returned driver exposes high-level `channels` API (recommended)
  and uses that when available.
- Falls back to safe SCPI/binary retrieval when necessary (works for MSO5-style drivers).
- Tries SOCKET fallback if initial add_scope() has VISA buffer problems.

Notes:
- If you want to avoid messing with other PyVISA sessions, prefer passing a
  SOCKET address (e.g. "TCPIP::10.59.133.248::4000::SOCKET").
- If you have the demo image available it lives at:
  sandbox:/mnt/data/b0341784-a299-4b9d-a327-32770acde600.png
"""
from typing import Tuple, Optional
import time
import numpy as np

from tm_devices import DeviceManager
from tm_devices.device_manager import DeviceManager as DMType
import visa


class TekMSO58:
    """Wrapper for Tektronix MSO58 using tm_devices.

    Usage:
        tek = TekMSO58("TCPIP::10.59.133.248::INSTR")
        tek.connect()
        tek.set_channel_on(1)
        t, v = tek.acquire_waveform(1)
        tek.close()
    """

    def __init__(self, address: str, alias: str = "SCOPE1") -> None:
        self.address = address
        self.alias = alias
        self._dm: Optional[DMType] = None
        self._scope = None

    def connect(self, *, retry_socket_fallback: bool = True, timeout_s: int = 10) -> str:
        """Create a DeviceManager and add the scope.

        If the standard add_scope() path fails due to VISA buffer/timeouts, and
        `retry_socket_fallback` is True, the method will retry using the Tek
        raw SCPI socket (port 4000).

        Returns the IDN string on success.
        """
        print(f"Connecting to Tektronix MSO58 at {self.address}...")

        # Create DeviceManager (singleton) — may re-use an existing instance
        self._dm = DeviceManager()

        # Try initial add_scope() — allow exceptions to bubble so caller can see them
        try:
            self._scope = self._dm.add_scope(self.address, alias=self.alias)
        except Exception as e:
            # If socket fallback requested, try using port 4000 SOCKET
            if retry_socket_fallback and "INSTR" in self.address.upper():
                socket_addr = self.address.replace("::INSTR", "::4000::SOCKET")
                try:
                    print("add_scope failed, retrying using SOCKET mode...", socket_addr)
                    self._scope = self._dm.add_scope(
                        socket_addr, alias=self.alias, connection_type="SOCKET", port=4000
                    )
                except Exception:
                    # raise original error to preserve context
                    raise
            else:
                raise

        # Basic IDN via universal SCPI query (works regardless of driver capabilities)
        try:
            idn = self._scope.query("*IDN?")
        except Exception:
            # As a last resort try direct visa_resource if available
            try:
                visa_res = getattr(self._scope, "visa_resource", None)
                if visa_res is not None:
                    old_to = visa_res.timeout
                    visa_res.timeout = int(timeout_s * 1000)
                    visa_res.write("*IDN?")
                    idn = visa_res.read().strip()
                    visa_res.timeout = old_to
                else:
                    idn = "<unknown idn>"
            except Exception:
                idn = "<unknown idn>"

        print("Connected:", idn)
        return idn

    def close(self) -> None:
        """Close the scope and DeviceManager (if present)."""
        if self._scope is not None:
            try:
                self._scope.close()
            except Exception:
                pass
            self._scope = None
        if self._dm is not None:
            try:
                self._dm.close()
            except Exception:
                pass
            self._dm = None

    # ---------------------------
    # Convenience SCPI helpers
    # ---------------------------
    def autoset(self) -> None:
        self._scope.write("AUTOSet EXECute")

    def set_channel_on(self, ch: int) -> None:
        # For modern tm_devices drivers there may be a channels API; otherwise use SCPI
        if hasattr(self._scope, "channels"):
            try:
                self._scope.channels[f"CH{ch}"].state = "ON"
                return
            except Exception:
                pass
        # fallback
        self._scope.write(f"SELECT:CH{ch} ON")

    def set_channel_off(self, ch: int) -> None:
        if hasattr(self._scope, "channels"):
            try:
                self._scope.channels[f"CH{ch}"].state = "OFF"
                return
            except Exception:
                pass
        self._scope.write(f"SELECT:CH{ch} OFF")

    def set_timebase(self, scale_s: float) -> None:
        self._scope.write(f"HORizontal:SCAle {scale_s}")

    def set_vertical_scale(self, ch: int, scale_v: float) -> None:
        # prefer high-level API if present
        if hasattr(self._scope, "channels"):
            try:
                self._scope.channels[f"CH{ch}"].scale = scale_v
                return
            except Exception:
                pass
        self._scope.write(f"CH{ch}:SCAle {scale_v}")

    # ---------------------------
    # Waveform acquisition
    # ---------------------------
    def acquire_waveform(self, ch: int = 1, *, max_bytes: int = 10_000_000) -> Tuple[np.ndarray, np.ndarray]:
        """Acquire waveform from channel `ch` and return (t, volts).

        The method will try, in order:
          1) use tm_devices high-level channel API (channels[].read_waveform())
          2) fallback to SCPI binary transfer using the underlying visa_resource

        The SCPI fallback carefully parses Tektronix definite-length blocks and
        applies waveform preamble scaling.
        """
        if self._scope is None:
            raise RuntimeError("Scope not connected")

        # 1) high-level tm_devices API if available
        if hasattr(self._scope, "channels"):
            try:
                ch_obj = self._scope.channels.get(f"CH{ch}")
                if ch_obj is not None and hasattr(ch_obj, "read_waveform"):
                    wf = ch_obj.read_waveform()
                    # tm_devices waveform object usually exposes .times and .volts
                    return np.asarray(wf.times), np.asarray(wf.volts)
            except Exception:
                # fall through to SCPI fallback
                pass

        # 2) SCPI binary fallback
        visa_res = getattr(self._scope, "visa_resource", None)
        if visa_res is None:
            # Some drivers expose a private _visa_resource
            visa_res = getattr(self._scope, "_visa_resource", None)

        if visa_res is None:
            raise RuntimeError("No VISA/socket resource available for SCPI fallback")

        # Configure data format on scope
        try:
            # Request simple unsigned binary bytes (RI: signed byte is also possible on some scopes)
            self._scope.write("DATa:ENCdg RIBinary")
            self._scope.write("DATa:WIDth 1")
            self._scope.write(f"DATa:SOURCE CH{ch}")

            # Ask for preamble parameters (try multiple names for compatibility)
            def q(cmd):
                try:
                    return visa_res.query(cmd)
                except Exception:
                    # many tm_devices drivers proxy query through .query()
                    try:
                        return self._scope.query(cmd)
                    except Exception:
                        return None

            ym = q("WFMOutpre:YMULT?") or q("WFMPRE:YMULT?")
            yoff = q("WFMOutpre:YOFF?") or q("WFMPRE:YOFF?")
            yzero = q("WFMOutpre:YZERO?") or q("WFMPRE:YZERO?")
            xincr = q("WFMOutpre:XINCR?") or q("WFMPRE:XINCR?")

            # If any are None, try generic query patterns (safe-guard)
            if any(x is None for x in (ym, yoff, yzero, xincr)):
                # Try using ':WFMPRE:...' via scope.query (older variants)
                ym = ym or self._scope.query("WFMPRE:YMULT?")
                yoff = yoff or self._scope.query("WFMPRE:YOFF?")
                yzero = yzero or self._scope.query("WFMPRE:YZERO?")
                xincr = xincr or self._scope.query("WFMPRE:XINCR?")

            ymult = float(ym)
            yoff = float(yoff)
            yzero = float(yzero)
            xincr = float(xincr)
        except Exception as e:
            raise RuntimeError(f"Failed to query waveform preamble: {e}")

        # Retrieve binary curve
        # Use write then read_raw on the underlying resource
        # Note: read_raw / read_binary() behavior differs between VISA backends.
        try:
            # Ask for curve
            visa_res.write("CURVe?")
            # read raw block (definite-length) up to max_bytes
            raw = visa_res.read_raw(max_bytes)
        except Exception as e:
            # fallback to awkward: use scope.query which may try to decode ASCII and fail
            try:
                raw = self._scope.query("CURVe?", )
                # if query returned string, convert to bytes
                if isinstance(raw, str):
                    raw = raw.encode('latin1')
            except Exception as e2:
                raise RuntimeError(f"Failed to read raw binary curve: {e} | {e2}")

        # Parse Tektronix definite-length block: b'#' + digit_count + digits + data
        if not raw or raw[0:1] != b"#":
            # sometimes the driver already returned a CSV ASCII string; try parsing
            try:
                txt = raw.decode('ascii', errors='ignore')
                vals = [float(x) for x in txt.strip().split(',') if x]
                volts = np.array(vals)
                t = np.arange(len(volts)) * xincr
                return t, volts
            except Exception:
                raise RuntimeError("Unexpected waveform block format")

        digits = int(raw[1:2].decode('ascii'))
        header_len = 2 + digits
        data = raw[header_len:header_len + int(raw[2:2+digits].decode('ascii'))]

        # Interpret bytes as unsigned integers (0-255)
        samples = np.frombuffer(data, dtype=np.uint8).astype(np.float64)

        # Convert to volts using Tek preamble
        volts = (samples - yoff) * ymult + yzero
        t = np.arange(len(volts)) * xincr

        return t, volts


# end of file
