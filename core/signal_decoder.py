from typing import Any, Dict, Tuple  # noqa: UP035


class SignalDecoder:
    """Decodes raw CAN frame payloads into engineering signals using the DBC database."""

    def __init__(self, db):
        self.db = db

    def decode_frame(self, arbitration_id: int, data: bytes) -> Tuple[str | None, Dict[str, Any] | None]:  # noqa: UP006
        """
        Looks up a message by its CAN ID and decodes its raw bytes.
        Returns: (message_name, dictionary_of_signals)
        """
        try:
            # Look up message definition by its hex/decimal arbitration ID
            message = self.db.get_message_by_frame_id(arbitration_id)
        except KeyError:
            # ID not found in database (e.g. unknown ID 0x7FE)
            return None, None

        try:
            # cantools handles the bit-shifting, scaling factors, and offsets automatically
            decoded_signals = message.decode(data)
            return message.name, decoded_signals
        except Exception as e:
            # Gracefully catch payload errors (e.g., DLC length mismatches or truncated bytes)
            return message.name, {"_decode_error": str(e)}
