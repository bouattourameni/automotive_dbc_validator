import re
from collections.abc import Generator
from dataclasses import dataclass


@dataclass
class CANFrame:
    timestamp: float
    arbitration_id: int
    dlc: int
    data: bytes


class LogParser:
    """Parses raw text CAN trace logs into structured CANFrame objects."""

    # Regex breakdown:
    # 1. Timestamp: ([0-9]+\.[0-9]+) -> e.g., 10.000000
    # 2. CAN ID: ([0-9a-fA-F]+) -> e.g., 210
    # 3. Direction/Type: \w+\s+\w+ -> matches 'Rx d'
    # 4. DLC: (\d+) -> e.g., 8
    # 5. Data Bytes: (.+) -> e.g., 0A 10 20 30 40 50 60 01
    LOG_LINE_REGEX = re.compile(
        r"^\s*([0-9]+\.[0-9]+)\s+([0-9a-fA-F]+)\s+\w+\s+\w+\s+(\d+)\s+(.+)$"
    )

    @classmethod
    def parse_file(cls, filepath: str) -> Generator[CANFrame, None, None]:
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                # Strip whitespace
                line = line.strip()

                # Skip empty lines or comment lines starting with '#'
                if not line or line.startswith("#"):
                    continue

                match = cls.LOG_LINE_REGEX.match(line)
                if not match:
                    print(
                        f"[WARNING] Skipping unparsed format on line {line_num}: {line}")
                    continue

                ts_str, id_str, dlc_str, data_str = match.groups()

                try:
                    timestamp = float(ts_str)
                    # Convert hex ID (e.g., '210') to integer (528)
                    arbitration_id = int(id_str, 16)
                    dlc = int(dlc_str)

                    # Convert space-separated hex bytes string (e.g., "0A 10 20") into actual bytes
                    data_bytes = bytes([int(b, 16) for b in data_str.split()])

                    yield CANFrame(
                        timestamp=timestamp,
                        arbitration_id=arbitration_id,
                        dlc=dlc,
                        data=data_bytes
                    )
                except (ValueError, IndexError) as e:
                    print(
                        f"[ERROR] Malformed data on line {line_num}: {e} (Line: {line})")
