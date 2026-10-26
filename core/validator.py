from typing import Any, Dict, List  # noqa: UP035


class ProtocolValidator:
    """Validates decoded signals against DBC physical limits and CAN bus timing rules."""

    def __init__(self, db):
        self.db = db
        # Dictionary to keep track of the last seen timestamp for each message name
        self.last_seen_timestamps: Dict[str, float] = {}

    def validate_boundaries(self, message_name: str, signals: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Checks if decoded signals are within the min/max physical limits defined in the DBC."""
        anomalies = []
        try:
            message = self.db.get_message_by_name(message_name)
        except KeyError:
            return anomalies

        for signal_name, value in signals.items():
            # Skip internal error keys
            if signal_name.startswith("_"):
                continue

            try:
                signal_def = message.get_signal_by_name(signal_name)
                min_val = signal_def.minimum
                max_val = signal_def.maximum

                # Check if physical boundaries are defined and violated
                if min_val is not None and max_val is not None and not (min_val <= value <= max_val):
                    anomalies.append({
                        "rule": "OUT_OF_BOUNDS",
                        "message": message_name,
                        "signal": signal_name,
                        "value": value,
                        "allowed_range": (min_val, max_val)
                    })
            except KeyError:
                pass  # Signal definition lookup failed safely

        return anomalies

    def validate_timing(self, message_name: str, current_timestamp: float, max_interval: float = 0.5) -> List[Dict[str, Any]]:
        """Checks if the time gap between consecutive identical messages exceeds the expected interval."""
        anomalies = []

        if message_name in self.last_seen_timestamps:
            delta = current_timestamp - self.last_seen_timestamps[message_name]
            # If the gap is greater than allowed (e.g., 500ms), flag a timing violation
            if delta > max_interval:
                anomalies.append({
                    "rule": "TIMING_VIOLATION",
                    "message": message_name,
                    "interval_seconds": round(delta, 4),
                    "threshold": max_interval
                })

        # Update last seen timestamp for this message
        self.last_seen_timestamps[message_name] = current_timestamp
        return anomalies
