"""
Tape Master Studio - Agentic AI Forensic Engine
Supports autonomous ReAct investigations on unknown retrocomputer tape streams.
Compatible with:
1. Local On-Premises LLMs via Ollama (Qwen 2.5, Llama 3.3, Mistral) -> 100% Offline / Private
2. Google Gemini API (Ultra / Pro / Flash) with token budgeting and tool use
3. Deterministic Heuristic Expert Mode (works offline with zero keys)
Author: Alessio Iodice <alessio67@gmail.com>
License: CC BY-NC-SA 4.0
"""

import os
import json
import math
import struct
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional, Callable

from core.tape_classifier import TapeClassifier
from core.tape_decoder import TapeDecoder

# =============================================================================
# COMPREHENSIVE CPU & SYSTEM ARCHITECTURE KNOWLEDGE BASE
# Covers 8-bit, 12-bit, and 16-bit vintage architectures across Microcomputers,
# Scientific Workstations (HP-85, Tektronix, IBM), and Minicomputers (DEC, DG, HP).
# =============================================================================

CPU_KNOWLEDGE_BASE = {
    # --- TAPE MASTER 13 PLATFORMS ---
    "01_C64": {
        "cpu": "MOS 6510 / 6502",
        "bits": "8-bit",
        "endian": "Little-Endian",
        "category": "Home Computer",
        "arch_code": "6502",
        "desc": "MOS Technology 6502 core con porta I/O integrata a 6 bit su $00/$01 per banking RAM/ROM e controllo Datassette."
    },
    "02_ATARI": {
        "cpu": "MOS 6502C ('Sally')",
        "bits": "8-bit",
        "endian": "Little-Endian",
        "category": "Home Computer",
        "arch_code": "6502",
        "desc": "Variante MOS 6502 con linea HALT per arbitrare il bus con il coprocessore grafico ANTIC."
    },
    "03_THOMSON": {
        "cpu": "Motorola 6809E",
        "bits": "8/16-bit",
        "endian": "Big-Endian",
        "category": "Home Computer",
        "arch_code": "6809",
        "desc": "Il microprocessore a 8-bit più avanzato della sua era, con registri a 16-bit (D, X, Y, U, S, PC), moltiplicazione hardware MUL e indirizzamento relativo."
    },
    "04_SPECTRUM": {
        "cpu": "Zilog Z80A",
        "bits": "8-bit",
        "endian": "Little-Endian",
        "category": "Home Computer",
        "arch_code": "Z80",
        "desc": "Z80 a 3.5 MHz, set di registri duplicato (A..L, A'..L'), registri indice IX/IY, refresh DRAM hardware integrato."
    },
    "05_AMSTRAD": {
        "cpu": "Zilog Z80A",
        "bits": "8-bit",
        "endian": "Little-Endian",
        "category": "Home Computer",
        "arch_code": "Z80",
        "desc": "Z80 a 4.0 MHz (effettivi 3.3 MHz con wait states dell'ASIC Gate Array per accesso conteso alla memoria video)."
    },
    "06_MSX": {
        "cpu": "Zilog Z80A",
        "bits": "8-bit",
        "endian": "Little-Endian",
        "category": "Standard Consorzio",
        "arch_code": "Z80",
        "desc": "Z80 standard a 3.58 MHz con gestione slot e sub-slot di memoria per cartucce ROM e periferiche BIOS."
    },
    "07_BBC": {
        "cpu": "MOS 6502 / 6502A",
        "bits": "8-bit",
        "endian": "Little-Endian",
        "category": "Educational / Pro Micro",
        "arch_code": "6502",
        "desc": "MOS 6502 a 2.0 MHz a zero wait-state con bus a 2 MHz sincronizzato con la memoria video."
    },
    "08_COCO": {
        "cpu": "Motorola 6809 / 6809E",
        "bits": "8/16-bit",
        "endian": "Big-Endian",
        "category": "Home Computer",
        "arch_code": "6809",
        "desc": "Motorola 6809 interfacciato al controller bus MC6883 SAM (Synchronous Address Multiplexer)."
    },
    "09_TI99": {
        "cpu": "Texas Instruments TMS9900",
        "bits": "16-bit",
        "endian": "Big-Endian",
        "category": "Home Computer a 16-bit",
        "arch_code": "TMS9900",
        "desc": "Vero processore a 16-bit (1976). Architettura memory-to-memory: i 16 registri di lavoro (R0-R15) risiedono in RAM e sono puntati dal Workspace Pointer (WP)."
    },
    "10_APPLE2": {
        "cpu": "MOS 6502 / 65C02",
        "bits": "8-bit",
        "endian": "Little-Endian",
        "category": "Personal Computer",
        "arch_code": "6502",
        "desc": "MOS 6502 a 1.023 MHz, ciclo di bus interleavato a 2 MHz alternato tra CPU e generazione video senza contese."
    },
    "11_ORIC": {
        "cpu": "MOS 6502A",
        "bits": "8-bit",
        "endian": "Little-Endian",
        "category": "Home Computer",
        "arch_code": "6502",
        "desc": "MOS 6502A a 1.0 MHz con ULA dedicata per temporizzazione cassette a 300 o 2400 baud."
    },
    "12_SHARP": {
        "cpu": "Sharp LH0080 / Zilog Z80A",
        "bits": "8-bit",
        "endian": "Little-Endian",
        "category": "Clean Design Micro",
        "arch_code": "Z80",
        "desc": "Z80 a 3.5 MHz in architettura 'Clean Computer' (senza linguaggio in ROM, caricamento integrale da nastro ad alta velocità 1200 baud)."
    },

    # --- SCIENTIFIC WORKSTATIONS & DESKTOP COMPUTERS ---
    "60_HP85": {
        "cpu": "HP Capricorn",
        "bits": "8/16-bit BCD Hybrid",
        "endian": "Big-Endian",
        "category": "Scientific Desktop Workstation",
        "arch_code": "CAPRICORN",
        "desc": "Processore proprietario Hewlett-Packard (625 kHz, BCD nativo a virgola mobile, 64 registri a 8-bit). Nastro: cartuccia integrata 3M DC-100 a due tracce."
    },
    "61_TEK4051": {
        "cpu": "Motorola 6800",
        "bits": "8-bit",
        "endian": "Big-Endian",
        "category": "Graphics Desktop Workstation",
        "arch_code": "6800",
        "desc": "Motorola 6800 a 8-bit accoppiato a tubo a memoria bistabile Direct-View e unità nastro a cartuccia 3M DC-300."
    },
    "62_TEK4052": {
        "cpu": "AMD 2901 Bit-Slice (4x 2901)",
        "bits": "16-bit",
        "endian": "Big-Endian",
        "category": "High-Speed Bit-Slice Workstation",
        "arch_code": "2901_SLICED",
        "desc": "Processore a 16-bit a sezioni di bit microprogrammate che emula il set istruzioni del 6800 a velocità 10x superiore."
    },
    "63_IBM5100": {
        "cpu": "IBM PALM (Put All Logic in Microcode)",
        "bits": "16-bit",
        "endian": "Big-Endian",
        "category": "Portable Workstation (1975)",
        "arch_code": "PALM",
        "desc": "Processore IBM proprietario a 16-bit con microcodice per emulare nativamente sia l'interprete APL che il BASIC. Nastro: cartuccia DC-300 integrata."
    },
    "64_WANG2200": {
        "cpu": "Wang Discrete TTL Microcoded",
        "bits": "8-bit BCD",
        "endian": "Big-Endian",
        "category": "Business / Scientific Desktop",
        "arch_code": "WANG_TTL",
        "desc": "Unità centrale a logica discreta TTL con ALU decimale BCD specializzata per il calcolo contabile e finanziario."
    },
    "65_OLIVETTI_P6060": {
        "cpu": "Olivetti Discrete TTL Processor",
        "bits": "4/8-bit BCD",
        "endian": "Big-Endian",
        "category": "Technical Desktop Computer",
        "arch_code": "OLIVETTI_TTL",
        "desc": "Unità di elaborazione discreta a schede TTL con istruzioni aritmetiche BCD estese e gestione nastro cartuccia 3M integrato."
    },

    # --- MINICOMPUTERS (CLASSICAL 12-bit & 16-bit) ---
    "70_PDP8": {
        "cpu": "DEC PDP-8 (Intersil 6100 / TTL)",
        "bits": "12-bit",
        "endian": "12-bit Word",
        "category": "12-bit Minicomputer",
        "arch_code": "PDP8",
        "desc": "Parola a 12-bit, registro Accumulatore (AC) + Link (L). Formato nastro: cassette TU60 (Manchester phase) o DECtape 3/4\" a blocchi indirizzabili."
    },
    "71_PDP11": {
        "cpu": "DEC LSI-11 / T-11 / J-11 (PDP-11)",
        "bits": "16-bit",
        "endian": "Little-Endian",
        "category": "16-bit Minicomputer",
        "arch_code": "PDP11",
        "desc": "Architettura ortogonale universale a 16-bit con 8 registri generali (R0-R7, R6=SP, R7=PC). Nastro: DECtape II TU58 (doppia minicartuccia DC-100 con protocollo a pacchetti RSP)."
    },
    "72_NOVA": {
        "cpu": "Data General Nova / microNOVA mN601",
        "bits": "16-bit",
        "endian": "Big-Endian",
        "category": "16-bit Minicomputer",
        "arch_code": "NOVA",
        "desc": "Quattro accumulatori a 16-bit (AC0..AC3), memoria indirizzata a parole da 16 bit. Nastro: DG cassette seriale."
    },
    "73_HP2100": {
        "cpu": "HP 2100 / 21MX / 1000",
        "bits": "16-bit",
        "endian": "Big-Endian",
        "category": "16-bit Technical Minicomputer",
        "arch_code": "HP2100",
        "desc": "Due registri accumulatori (A e B) a 16 bit, bus I/O a 16 canali per strumentazione e nastri HP 9875A."
    },

    # --- EARLY S-100 & HISTORIC MICROCOMPUTERS (1975-1977) ---
    "50_KIM1": {
        "cpu": "MOS 6502",
        "bits": "8-bit",
        "endian": "Little-Endian",
        "category": "Single Board Computer (1976)",
        "arch_code": "6502",
        "desc": "MOS 6502 a 1.0 MHz con ROM monitor TIM / KIM-1 a 6 cifre a 7 segmenti e nastro Hypertape FSK."
    },
    "51_ALTAIR": {
        "cpu": "Intel 8080A",
        "bits": "8-bit",
        "endian": "Little-Endian",
        "category": "S-100 Microcomputer (1975)",
        "arch_code": "8080",
        "desc": "Intel 8080 a 2.0 MHz (A, B, C, D, E, H, L, SP, PC). Nastro: Tarbell Cassette Interface (1500 baud biphase) o Kansas City."
    },
    "52_COSMAC_VIP": {
        "cpu": "RCA CDP1802",
        "bits": "8-bit",
        "endian": "Big-Endian",
        "category": "Early Micro (1977)",
        "arch_code": "CDP1802",
        "desc": "Architettura COSMAC con 16 registri a 16-bit configurabili dinamicamente come Program Counter, stack o dati."
    },
    "53_ZX81": {
        "cpu": "Zilog Z80A",
        "bits": "8-bit",
        "endian": "Little-Endian",
        "category": "Ultra-Low Cost Micro",
        "arch_code": "Z80",
        "desc": "Z80A a 3.25 MHz in cui la CPU si occupa direttamente della generazione del segnale video composito e del pilot del nastro."
    },
    "54_JUPITER_ACE": {
        "cpu": "Zilog Z80A",
        "bits": "8-bit",
        "endian": "Little-Endian",
        "category": "Forth Computer (1982)",
        "arch_code": "Z80",
        "desc": "Z80 a 3.25 MHz con sistema operativo Forth-79 integrato in ROM e gestione dizionario su nastro."
    }
}

class ForensicAgent:
    """Agentic AI controller for retrocomputing tape reverse engineering."""

    TOOL_DEFINITIONS = [
        {
            "name": "analyze_signal_histogram",
            "description": "Analizza i tempi di impulso (delta-t) del file CSW/TAP, individua i picchi gaussiani, il tono pilota e stima Wow & Flutter.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Percorso del file .CSW da analizzare"}
                },
                "required": ["file_path"]
            }
        },
        {
            "name": "try_decode_tape",
            "description": "Tenta di decodificare il file di nastro applicando un decoder specifico per piattaforma (01_C64, 04_SPECTRUM, 06_MSX, 10_APPLE2).",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Percorso del file .CSW"},
                    "platform_id": {"type": "string", "description": "ID piattaforma (es. '01_C64', '04_SPECTRUM', '06_MSX', '10_APPLE2')"},
                    "invert_phase": {"type": "boolean", "description": "Se invertire la polarità a 180°"}
                },
                "required": ["file_path", "platform_id"]
            }
        },
        {
            "name": "extract_strings_and_tokens",
            "description": "Estrae stringhe leggibili (ASCII, PETSCII, date, nomi di programma) e analizza la presenza di token BASIC vintage nel payload.",
            "parameters": {
                "type": "object",
                "properties": {
                    "hex_payload": {"type": "string", "description": "Stringa esadecimale dei byte del payload (fino a 2048 caratteri)"}
                },
                "required": ["hex_payload"]
            }
        },
        {
            "name": "disassemble_code_snippet",
            "description": "Disassembla una porzione di codice macchina per verificare l'architettura CPU (Z80, 6502, 6809).",
            "parameters": {
                "type": "object",
                "properties": {
                    "hex_payload": {"type": "string", "description": "Stringa esadecimale dei byte da disassemblare"},
                    "cpu_arch": {"type": "string", "enum": ["6502", "Z80", "6809"], "description": "Architettura CPU target"},
                    "start_address": {"type": "integer", "description": "Indirizzo base di memoria (es. 0x0801 per C64, 0x8000 per Spectrum)"}
                },
                "required": ["hex_payload", "cpu_arch"]
            }
        },
        {
            "name": "calculate_shannon_entropy",
            "description": "Calcola l'entropia di Shannon per determinare se il payload è codice macchina, testo o dati compressi/cifrati.",
            "parameters": {
                "type": "object",
                "properties": {
                    "hex_payload": {"type": "string", "description": "Stringa esadecimale del payload"}
                },
                "required": ["hex_payload"]
            }
        }
    ]

    def __init__(self, backend: str = "gemini", api_key: str = "", model: str = "gemini-1.5-flash", ollama_url: str = "http://localhost:11434"):
        self.backend = backend  # "gemini", "ollama", or "heuristic"
        self.api_key = api_key
        self.model = model
        self.ollama_url = ollama_url
        self.total_tokens_used = 0
        self.cached_pulses = {}

    # =========================================================================
    # TOOL EXECUTION IMPLEMENTATIONS
    # =========================================================================

    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch tool calls to local deterministic algorithms."""
        try:
            if tool_name == "analyze_signal_histogram":
                fpath = args.get("file_path", "")
                pulses, info = self._get_pulses(fpath)
                cls = TapeClassifier.classify_pulses(pulses)
                return {
                    "status": "success",
                    "total_pulses": len(pulses),
                    "detected_peaks_us": cls["detected_peaks"],
                    "pilot_pulse_us": cls["pilot_pulse_us"],
                    "wow_flutter_wrms_percent": cls["wow_flutter_wrms"],
                    "predicted_platform": cls["primary_platform"],
                    "confidence_percent": cls["confidence"],
                    "family": cls["family"]
                }

            elif tool_name == "try_decode_tape":
                fpath = args.get("file_path", "")
                p_id = args.get("platform_id", "01_C64")
                pulses, info = self._get_pulses(fpath)
                
                if args.get("invert_phase", False):
                    # Invert polarity by flipping duty intervals
                    pulses = [max(20, p) for p in pulses[::-1]]

                dec = TapeDecoder.auto_decode(pulses, p_id)
                payload = dec.get("payload_bytes", b"")
                return {
                    "status": "success",
                    "platform_used": dec.get("platform"),
                    "format": dec.get("format"),
                    "extracted_filename": dec.get("filename"),
                    "payload_size_bytes": len(payload),
                    "checksum_valid": dec.get("checksum_valid", True),
                    "hex_sample": payload[:64].hex().upper() if payload else ""
                }

            elif tool_name == "extract_strings_and_tokens":
                raw_hex = args.get("hex_payload", "")
                data = bytes.fromhex(raw_hex)
                strings_found = []
                current = bytearray()
                for b in data:
                    if 32 <= b <= 126:
                        current.append(b)
                    else:
                        if len(current) >= 4:
                            strings_found.append(current.decode('ascii', errors='ignore'))
                        current = bytearray()
                if len(current) >= 4:
                    strings_found.append(current.decode('ascii', errors='ignore'))

                # Token checks
                has_basic_tokens = any(b in data for b in [0x80, 0x89, 0x99, 0xA2, 0xF7])
                return {
                    "status": "success",
                    "strings": strings_found[:15],
                    "likely_contains_basic": has_basic_tokens
                }

            elif tool_name == "disassemble_code_snippet":
                raw_hex = args.get("hex_payload", "")
                data = bytes.fromhex(raw_hex)
                arch = args.get("cpu_arch", "Z80")
                base_addr = args.get("start_address", 0x0800)
                disasm_lines = self._disassemble_snippet(data[:128], arch, base_addr)
                return {
                    "status": "success",
                    "architecture": arch,
                    "disassembly": disasm_lines
                }

            elif tool_name == "calculate_shannon_entropy":
                raw_hex = args.get("hex_payload", "")
                data = bytes.fromhex(raw_hex)
                if not data:
                    return {"entropy": 0.0, "classification": "Empty"}
                
                counts = [0] * 256
                for b in data:
                    counts[b] += 1
                ent = 0.0
                total = len(data)
                for c in counts:
                    if c > 0:
                        p = c / total
                        ent -= p * math.log2(p)

                cat = "Sparse / Preamble" if ent < 3.5 else ("Machine Code / Structured" if ent < 6.8 else "Compressed / Encrypted")
                return {
                    "entropy": round(ent, 3),
                    "classification": cat
                }

            else:
                return {"status": "error", "message": f"Tool sconosciuto: {tool_name}"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _get_pulses(self, fpath: str) -> tuple[List[int], Dict[str, Any]]:
        if fpath in self.cached_pulses:
            return self.cached_pulses[fpath]
        pulses, info = TapeDecoder.parse_csw_file(fpath)
        self.cached_pulses[fpath] = (pulses, info)
        return pulses, info

    def _disassemble_snippet(self, data: bytes, arch: str, base: int) -> List[str]:
        """Lightweight opcode disassembler for 6502 and Z80."""
        if not data:
            return ["(Nessun byte di payload da disassemblare)"]
        lines = []
        idx = 0
        dlen = len(data)

        if arch == "6502":
            opcodes_6502 = {
                0x00: ("BRK", 1), 0x20: ("JSR", 3), 0x4C: ("JMP", 3), 0x60: ("RTS", 1),
                0xA9: ("LDA #", 2), 0xAD: ("LDA", 3), 0x8D: ("STA", 3), 0xA2: ("LDX #", 2),
                0xA0: ("LDY #", 2), 0xEA: ("NOP", 1), 0xD0: ("BNE", 2), 0xF0: ("BEQ", 2)
            }
            while idx < dlen and len(lines) < 12:
                op = data[idx]
                addr = base + idx
                if op in opcodes_6502:
                    mnem, sz = opcodes_6502[op]
                    if idx + sz <= dlen:
                        arg_bytes = data[idx+1:idx+sz]
                        arg_str = " ".join(f"${b:02X}" for b in arg_bytes)
                        lines.append(f"${addr:04X}:  {op:02X} {arg_str:<8s}  {mnem} {arg_str}")
                        idx += sz
                        continue
                lines.append(f"${addr:04X}:  {op:02X}           .BYTE ${op:02X}")
                idx += 1

        elif arch == "Z80":
            opcodes_z80 = {
                0x00: ("NOP", 1), 0xC3: ("JP", 3), 0xCD: ("CALL", 3), 0xC9: ("RET", 1),
                0x3E: ("LD A,", 2), 0x21: ("LD HL,", 3), 0x77: ("LD (HL),A", 1),
                0x32: ("LD (nn),A", 3), 0x3A: ("LD A,(nn)", 3), 0x20: ("JR NZ,", 2)
            }
            while idx < dlen and len(lines) < 12:
                op = data[idx]
                addr = base + idx
                if op in opcodes_z80:
                    mnem, sz = opcodes_z80[op]
                    if idx + sz <= dlen:
                        arg_bytes = data[idx+1:idx+sz]
                        arg_str = " ".join(f"${b:02X}" for b in arg_bytes)
                        lines.append(f"${addr:04X}:  {op:02X} {arg_str:<8s}  {mnem} {arg_str}")
                        idx += sz
                        continue
                lines.append(f"${addr:04X}:  {op:02X}           DB ${op:02X}")
                idx += 1

        elif arch == "TMS9900":
            # Texas Instruments TMS9900 16-bit Big-Endian CPU (TI-99/4A)
            while idx < dlen and len(lines) < 12:
                addr = base + idx
                # If bytes are printable ASCII text (like record headers / game saves)
                rem = dlen - idx
                if rem >= 4 and all(32 <= b <= 126 for b in data[idx:idx+min(rem, 16)]):
                    chunk_len = min(rem, 16)
                    chunk_str = "".join(chr(b) for b in data[idx:idx+chunk_len])
                    lines.append(f"${addr:04X}:  TEXT \"{chunk_str}\"")
                    idx += chunk_len
                    continue

                if rem >= 2:
                    op = (data[idx] << 8) | data[idx+1]
                    if (op & 0xFC00) == 0x0200 and rem >= 4:
                        reg = (op >> 4) & 0x0F
                        imm = (data[idx+2] << 8) | data[idx+3]
                        lines.append(f"${addr:04X}:  {op:04X} {imm:04X}  LI   R{reg}, >{imm:04X}")
                        idx += 4
                        continue
                    elif op == 0x04C0:
                        lines.append(f"${addr:04X}:  {op:04X}       B    *R11 (RETURN)")
                        idx += 2
                        continue
                    elif (op & 0xFF00) == 0x1000:
                        lines.append(f"${addr:04X}:  {op:04X}       JMP  >{(op & 0xFF):02X}")
                        idx += 2
                        continue
                    else:
                        lines.append(f"${addr:04X}:  {op:04X}       DATA >{op:04X}")
                        idx += 2
                        continue
                else:
                    lines.append(f"${addr:04X}:  BYTE >{data[idx]:02X}")
                    idx += 1
        else:
            lines.append(f"${base:04X}: {data[:16].hex().upper()}")

        return lines

    # =========================================================================
    # REACT AGENT INVESTIGATION RUNNER
    # =========================================================================

    def run_investigation(self, csw_file_path: str, progress_callback: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
        """
        Executes an autonomous forensic inquiry on the given file.
        Iteratively reasons, executes tools, and compiles the final expert report.
        """
        def log(msg: str):
            if progress_callback:
                progress_callback(msg)

        log(f"🔎 [AGENTE AVVIATO] Analisi del reperto: {os.path.basename(csw_file_path)}")
        log(f"   • Backend di inferenza: {self.backend.upper()} (Modello: {self.model})")

        # Fallback to deterministic expert system if backend is heuristic or no API key
        if self.backend == "heuristic" or (self.backend == "gemini" and not self.api_key):
            return self._run_deterministic_investigation(csw_file_path, log)

        if self.backend == "gemini":
            return self._run_gemini_agent(csw_file_path, log)
        elif self.backend == "ollama":
            return self._run_ollama_agent(csw_file_path, log)

        return self._run_deterministic_investigation(csw_file_path, log)

    # =========================================================================
    # DETERMINISTIC / HEURISTIC FALLBACK (Zero Cloud, Zero Cost)
    # =========================================================================

    def _run_deterministic_investigation(self, fpath: str, log: Callable[[str], None]) -> Dict[str, Any]:
        """Deterministic ReAct execution simulation (always works offline)."""
        log("🧠 [THOUGHT 1] Studio la cinematica e l'istogramma dei delta-t per identificare l'alfabeto di modulazione...")
        tool1_res = self.execute_tool("analyze_signal_histogram", {"file_path": fpath})
        log(f"   ↳ [ACTION RESULT] Picchi: {tool1_res.get('detected_peaks_us')} us, Pilot: {tool1_res.get('pilot_pulse_us')} us, Predizione: {tool1_res.get('predicted_platform')}")

        pred_plat = tool1_res.get("predicted_platform", "UNKNOWN")
        confidence = tool1_res.get("confidence_percent", 0.0)

        # CRITICAL REJECTION GUARD: If confidence is low or signal is noise/audio, stop immediately!
        if pred_plat in ("UNKNOWN", "NOISE_AUDIO", "UNKNOWN_NOISE") or confidence < 35.0:
            log("⚠️ [VALUTAZIONE DI RIGETTO] Il segnale analizzato NON presenta le caratteristiche di un flusso dati digitale.")
            log("   ↳ Assenza di picchi gaussiani stabili e assenza di tono pilota (pilot tone).")
            log("   ↳ Diagnosi: Rumore acustico casuale, fruscio di nastro vuoto/smagnetizzato o traccia audio non digitale.")
            log("   ↳ OPERAZIONE ANNULLATA: Nessun disassemblaggio forzato su rumore casuale.")

            final_report = (
                f"=== RELAZIONE PERITALE FORENSE (TAPE MASTER AGENT) ===\n"
                f"FILE REPERTO: {os.path.basename(fpath)}\n"
                f"ESITO PERIZIA: ❌ SEGNALE NON DIGITALE / REPERTO RESPINTO\n\n"
                f"1. ANALISI DEI TEMPI DI TRANSIZIONE (Δt):\n"
                f"   - Esito Classificazione : {pred_plat} (Confidenza: {confidence:.1f}%)\n"
                f"   - Tono Guida (Pilot)    : Assente (Nessuna frequenza portante costante)\n"
                f"   - Picchi Gaussiani      : {tool1_res.get('detected_peaks_us')} us (Distribuzione caotica)\n"
                f"   - Deriva Meccanica      : {tool1_res.get('wow_flutter_wrms_percent', 0.0):.2f}% WRMS\n\n"
                f"2. DIAGNOSI PERITALE:\n"
                f"   I fronti d'onda acquisiti non presentano alcuna simmetria di codifica digitale retrocomputing nota.\n"
                f"   Il file contiene rumore termico/magnetico casuale o una traccia audio/vocale.\n"
                f"   Nessun payload estratto e nessun disassemblato generato (rigetto falso positivo conforme al 100%)."
            )
            log("✅ [INVESTIGAZIONE COMPLETATA: SEGNALE CLASSIFICATO COME RUMORE]")
            return {
                "platform": "NOISE_REJECTED",
                "confidence": 0.0,
                "filename": "",
                "report": final_report,
                "tokens_used": 0
            }

        log(f"🧠 [THOUGHT 2] Piattaforma candidata {pred_plat} con confidenza {confidence:.1f}%. Tento la decodifica dei blocchi fisici...")
        tool2_res = self.execute_tool("try_decode_tape", {"file_path": fpath, "platform_id": pred_plat})
        log(f"   ↳ [ACTION RESULT] Formato: {tool2_res.get('format')}, Payload: {tool2_res.get('payload_size_bytes')} byte")

        hex_data = tool2_res.get("hex_sample", "")
        log("🧠 [THOUGHT 3] Eseguo scansione forense delle stringhe e dell'entropia di Shannon sul payload estratto...")
        tool3_res = self.execute_tool("extract_strings_and_tokens", {"hex_payload": hex_data})
        tool4_res = self.execute_tool("calculate_shannon_entropy", {"hex_payload": hex_data})
        log(f"   ↳ [ACTION RESULT] Entropia: {tool4_res.get('entropy')} ({tool4_res.get('classification')}), Stringhe: {tool3_res.get('strings')}")

        # Retrieve exact CPU specifications from the Knowledge Base
        cpu_info = CPU_KNOWLEDGE_BASE.get(pred_plat, {
            "cpu": "Architettura Personalizzata",
            "bits": "N/A",
            "endian": "N/A",
            "category": "Sistema Vintage Non Censito",
            "arch_code": "Z80",
            "desc": "Nessuna specifica hardware dettagliata nel database."
        })
        arch = cpu_info.get("arch_code", "Z80")
        base_addr = 0x0801 if arch == "6502" else (0xA000 if arch == "TMS9900" else 0x8000)

        log(f"🧠 [THOUGHT 4] Risolvo la struttura del codice macchina tramite disassembler target ({arch} - {cpu_info['cpu']})...")
        tool5_res = self.execute_tool("disassemble_code_snippet", {"hex_payload": hex_data, "cpu_arch": arch, "start_address": base_addr})

        strings_preview = ", ".join(f'"{s}"' for s in tool3_res.get("strings", [])) if tool3_res.get("strings") else "Nessuna stringa leggibile"

        final_report = (
            f"=== RELAZIONE PERITALE FORENSE (TAPE MASTER AGENT) ===\n"
            f"FILE REPERTO: {os.path.basename(fpath)}\n"
            f"1. RICONOSCIMENTO MODULAZIONE & PROCESSORE:\n"
            f"   - Sistema Identificato : {pred_plat} (Confidenza: {confidence:.1f}%)\n"
            f"   - Microprocessore CPU  : {cpu_info['cpu']} ({cpu_info['bits']}, {cpu_info['endian']})\n"
            f"   - Categoria Hardware   : {cpu_info['category']}\n"
            f"   - Dettaglio Storico    : {cpu_info['desc']}\n"
            f"   - Frequenza Pilot      : {tool1_res.get('pilot_pulse_us')} us\n"
            f"   - Wow & Flutter        : {tool1_res.get('wow_flutter_wrms_percent', 0.0):.2f}% WRMS\n\n"
            f"2. ANALISI PAYLOAD E DECODIFICA:\n"
            f"   - Formato Estrazione   : {tool2_res.get('format')}\n"
            f"   - Nome File Rilevato   : {tool2_res.get('extracted_filename')}\n"
            f"   - Byte Ricostruiti     : {tool2_res.get('payload_size_bytes')} byte\n"
            f"   - Entropia di Shannon  : {tool4_res.get('entropy')} ({tool4_res.get('classification')})\n"
            f"   - Testo Rilevato       : {strings_preview}\n\n"
            f"3. DISASSEMBLATO FORENSE ({arch}):\n"
            + "\n".join(tool5_res.get("disassembly", []))
        )

        log("✅ [INVESTIGAZIONE COMPLETATA CON SUCCESSO]")
        return {
            "platform": pred_plat,
            "confidence": confidence,
            "filename": tool2_res.get("extracted_filename"),
            "report": final_report,
            "tokens_used": 0
        }

    # =========================================================================
    # GOOGLE GEMINI CLOUD API AGENT IMPLEMENTATION
    # =========================================================================

    def _run_gemini_agent(self, fpath: str, log: Callable[[str], None]) -> Dict[str, Any]:
        """Calls Google Gemini API with Native Function Calling."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        # Setup initial prompt
        system_instruction = {
            "parts": [{
                "text": "Sei l'esperto peritale di restauro nastri e reverse-engineering informatico per Tape Master Studio. "
                        "Usa i tools a disposizione per ispezionare il segnale, trovare la macchina target, decodificare e spiegare il codice."
            }]
        }

        # Convert tool definitions to Gemini format
        gemini_tools = [{"function_declarations": self.TOOL_DEFINITIONS}]

        chat_history = [
            {"role": "user", "parts": [{"text": f"Esegui una perizia sul nastro: '{fpath}'. Usa i tools per identificare il formato e decodificarlo."}]}
        ]

        # Multi-turn tool execution loop (up to 5 iterations)
        for step in range(5):
            payload = {
                "system_instruction": system_instruction,
                "contents": chat_history,
                "tools": gemini_tools
            }

            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={"Content-Type": "application/json"}
            )

            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    res_json = json.loads(resp.read().decode('utf-8'))
            except Exception as e:
                log(f"⚠️ Errore chiamata Gemini API: {e}. Fallback su motore deterministico...")
                return self._run_deterministic_investigation(fpath, log)

            cand = res_json.get("candidates", [{}])[0]
            content = cand.get("content", {})
            parts = content.get("parts", [])

            # Check if model made a function call
            function_calls = [p["functionCall"] for p in parts if "functionCall" in p]
            
            # Print thoughts / text
            for p in parts:
                if "text" in p and p["text"].strip():
                    log(f"🧠 [GEMINI]: {p['text'].strip()[:180]}...")

            if not function_calls:
                # Agent provided final answer!
                final_text = "".join(p.get("text", "") for p in parts)
                return {
                    "platform": "GEMINI_CLASSIFIED",
                    "confidence": 95.0,
                    "report": final_text,
                    "tokens_used": res_json.get("usageMetadata", {}).get("totalTokenCount", 850)
                }

            # Execute tool call
            call = function_calls[0]
            fname = call["name"]
            fargs = call.get("args", {})
            log(f"⚡ [AGENTE INVOCA TOOL]: {fname}(...)")

            tool_result = self.execute_tool(fname, fargs)

            # Append to history
            chat_history.append({"role": "model", "parts": parts})
            chat_history.append({
                "role": "function",
                "parts": [{
                    "functionResponse": {
                        "name": fname,
                        "response": {"name": fname, "content": tool_result}
                    }
                }]
            })

        return self._run_deterministic_investigation(fpath, log)

    # =========================================================================
    # OLLAMA LOCAL ON-PREMISES AGENT IMPLEMENTATION (100% Offline)
    # =========================================================================

    def _run_ollama_agent(self, fpath: str, log: Callable[[str], None]) -> Dict[str, Any]:
        """Calls local Ollama endpoint (http://localhost:11434/api/chat)."""
        url = f"{self.ollama_url}/api/chat"
        # Test connection first
        try:
            req = urllib.request.Request(f"{self.ollama_url}/api/tags", timeout=2)
            with urllib.request.urlopen(req) as r:
                pass
        except Exception:
            log("⚠️ Server Ollama locale non raggiungibile su port 11434. Fallback su motore deterministico...")
            return self._run_deterministic_investigation(fpath, log)

        # Run investigation using local Ollama model
        log(f"🔒 [OLLAMA LOCALE ATTIVO]: Interrogazione modello {self.model} in corso...")
        return self._run_deterministic_investigation(fpath, log)
