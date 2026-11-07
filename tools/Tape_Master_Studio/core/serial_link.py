"""
Tape Master Studio - High-Speed Serial Link Manager
Auto-discovers Raspberry Pi Pico USB CDC serial and handles framed streaming.
Author: Alessio Iodice <alessio67@gmail.com>
License: CC BY-NC-SA 4.0
"""

import threading
import time
import serial
import serial.tools.list_ports
from typing import Optional, Callable, Dict, Any

PICO_VID = 0x2E8A
PICO_PID = 0x000A

class SerialLink:
    def __init__(self):
        self.serial_port: Optional[serial.Serial] = None
        self.port_name: str = ""
        self.is_connected: bool = False
        self._rx_thread: Optional[threading.Thread] = None
        self._running: bool = False
        self._lock = threading.Lock()

        # Callbacks
        self.on_connected: Optional[Callable[[str], None]] = None
        self.on_disconnected: Optional[Callable[[], None]] = None
        self.on_ident_received: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_status_received: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_pulse_received: Optional[Callable[[int], None]] = None
        self.on_azimuth_received: Optional[Callable[[int, int], None]] = None
        self.on_log_message: Optional[Callable[[str], None]] = None

    @staticmethod
    def find_pico_port() -> Optional[str]:
        """Auto-detect port matching Raspberry Pi Pico VID:PID."""
        for port in serial.tools.list_ports.comports():
            if port.vid == PICO_VID and port.pid == PICO_PID:
                return port.device
        # Fallback: check if description mentions 'Pico' or 'RP2040'
        for port in serial.tools.list_ports.comports():
            desc = (port.description or "").lower()
            if "pico" in desc or "rp2040" in desc:
                return port.device
        return None

    def connect(self, port: Optional[str] = None, baudrate: int = 115200) -> bool:
        """Connect to device. If port is None, auto-detects Pico."""
        self.disconnect()

        target_port = port or self.find_pico_port()
        if not target_port:
            if self.on_log_message:
                self.on_log_message("Tape Master non trovato. Verifica il cavo USB.")
            return False

        try:
            self.serial_port = serial.Serial(target_port, baudrate=baudrate, timeout=0.1)
            self.port_name = target_port
            self.is_connected = True
            self._running = True

            self._rx_thread = threading.Thread(target=self._read_loop, daemon=True)
            self._rx_thread.start()

            if self.on_connected:
                self.on_connected(target_port)

            # Query hardware identification
            self.send_command("IDENT")
            return True
        except Exception as e:
            if self.on_log_message:
                self.on_log_message(f"Errore connessione su {target_port}: {e}")
            self.disconnect()
            return False

    def disconnect(self):
        """Disconnect active serial port."""
        self._running = False
        if self._rx_thread and self._rx_thread.is_alive():
            self._rx_thread.join(timeout=0.5)

        with self._lock:
            if self.serial_port and self.serial_port.is_open:
                try:
                    self.serial_port.close()
                except Exception:
                    pass
            self.serial_port = None
            self.is_connected = False

        if self.on_disconnected:
            self.on_disconnected()

    def send_command(self, cmd: str):
        """Send formatted command line."""
        if not self.is_connected or not self.serial_port:
            return
        try:
            with self._lock:
                line = (cmd.strip() + "\r\n").encode("utf-8")
                self.serial_port.write(line)
                self.serial_port.flush()
        except Exception as e:
            if self.on_log_message:
                self.on_log_message(f"Errore invio comando: {e}")

    def _read_loop(self):
        """Background thread continuously parsing incoming lines."""
        buffer = ""
        while self._running:
            try:
                if not self.serial_port or not self.serial_port.is_open:
                    break
                raw = self.serial_port.read(256)
                if not raw:
                    continue

                buffer += raw.decode("utf-8", errors="ignore")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip("\r").strip()
                    if line:
                        self._dispatch_line(line)
            except Exception:
                time.sleep(0.01)

    def _dispatch_line(self, line: str):
        """Parse incoming line from Tape Master firmware."""
        # 1. Pulse stream: "P <us>"
        if line.startswith("P "):
            try:
                us = int(line[2:])
                if self.on_pulse_received:
                    self.on_pulse_received(us)
            except ValueError:
                pass
            return

        # 2. Azimuth stream: "AZ <lvl> <raw_adc>"
        if line.startswith("AZ "):
            try:
                parts = line[3:].split()
                if len(parts) >= 2 and self.on_azimuth_received:
                    self.on_azimuth_received(int(parts[0]), int(parts[1]))
            except ValueError:
                pass
            return

        # 3. IDENT response
        if line.startswith("IDENT "):
            data = self._parse_key_values(line[6:])
            if self.on_ident_received:
                self.on_ident_received(data)
            return

        # 4. STATUS response
        if line.startswith("STATUS "):
            data = self._parse_key_values(line[7:])
            if self.on_status_received:
                self.on_status_received(data)
            return

        # 5. Generic Event / Response
        if self.on_log_message:
            self.on_log_message(line)

    @staticmethod
    def _parse_key_values(text: str) -> Dict[str, Any]:
        """Helper to parse KEY=VALUE pairs, supporting quotes."""
        res = {}
        tokens = []
        cur = ""
        in_quote = False
        for ch in text:
            if ch == '"':
                in_quote = not in_quote
            elif ch == ' ' and not in_quote:
                if cur:
                    tokens.append(cur)
                    cur = ""
                continue
            cur += ch
        if cur:
            tokens.append(cur)

        for tok in tokens:
            if '=' in tok:
                k, v = tok.split('=', 1)
                v = v.strip('"')
                if v.isdigit():
                    res[k] = int(v)
                else:
                    res[k] = v
        return res
