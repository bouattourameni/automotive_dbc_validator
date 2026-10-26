import json

import cantools

from core.parser import LogParser
from core.signal_decoder import SignalDecoder
from core.validator import ProtocolValidator


def run_pipeline(dbc_path: str, log_path: str):
    print("[INFO] Initializing pipeline...")

    # 1. Load Database
    db = cantools.database.load_file(dbc_path)
    decoder = SignalDecoder(db)
    validator = ProtocolValidator(db)

    telemetry_output = []
    validation_reports = []

    print(f"[INFO] Processing log file: {log_path}\n")

    # 2. Iterate through parsed log frames
    for frame in LogParser.parse_file(log_path):
        msg_name, signals = decoder.decode_frame(
            frame.arbitration_id, frame.data)

        if not msg_name:
            continue  # Ignore unmapped CAN IDs

        # Collect Telemetry record
        telemetry_record = {
            "timestamp": frame.timestamp,
            "can_id": hex(frame.arbitration_id),
            "message": msg_name,
            "signals": signals
        }
        telemetry_output.append(telemetry_record)

        # Run Validations if signals decoded successfully without errors
        if isinstance(signals, dict) and "_decode_error" not in signals:
            bound_anomalies = validator.validate_boundaries(msg_name, signals)
            timing_anomalies = validator.validate_timing(
                msg_name, frame.timestamp)

            if bound_anomalies or timing_anomalies:
                validation_reports.extend(bound_anomalies + timing_anomalies)

    # 3. Print Summary & Save Reports
    print(
        f"\n[SUMMARY] Successfully processed and decoded {len(telemetry_output)} frames.")
    print(
        f"[SUMMARY] Protocol validator flagged {len(validation_reports)} anomalies/violations.")

    with open("decoded_telemetry.json", "w") as f:
        json.dump(telemetry_output, f, indent=2)

    with open("validation_report.json", "w") as f:
        json.dump(validation_reports, f, indent=2)

    print("[INFO] Reports saved successfully to 'decoded_telemetry.json' and 'validation_report.json'.")


if __name__ == "__main__":
    DBC_FILE = "dbcs/toyota_adas.dbc"     # Update to your actual DBC path
    LOG_FILE = "oem/sample_can_log.txt"   # Update to your actual log path

    run_pipeline(DBC_FILE, LOG_FILE)
