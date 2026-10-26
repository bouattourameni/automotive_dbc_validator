

from core.parser import LogParser


def test_log_parser_valid_line():
    """Test that valid log lines parse into correct CANFrame attributes."""
    # Create a temporary mock log content or test a string parser approach
    log_content = "10.000000 210 Rx d 8 0A 10 20 30 40 50 60 01\n"

    # Write a temporary file for testing
    temp_file = "tests/temp_test_log.txt"
    with open(temp_file, "w") as f:
        f.write(log_content)

    frames = list(LogParser.parse_file(temp_file))

    assert len(frames) == 1
    assert frames[0].timestamp == 10.0
    assert frames[0].arbitration_id == 0x210
    assert frames[0].dlc == 8
    assert frames[0].data == b'\x0a\x10\x20\x30\x40\x50\x60\x01'


def test_log_parser_skips_comments_and_handles_errors():
    """Test that comments are ignored and malformed lines don't crash the generator."""
    log_content = (
        "# This is a comment\n"
        "\n"
        "11.750000 210 Rx d 8 ZZ YY XX WW VV UU TT SS\n"  # Malformed hex
        "11.800000 7FE Rx d 8 11 22 33 44 55 66 77\n"    # Valid frame after error
    )

    temp_file = "tests/temp_error_log.txt"
    with open(temp_file, "w") as f:
        f.write(log_content)

    frames = list(LogParser.parse_file(temp_file))

    # The malformed line should be skipped, and the valid line should pass through
    assert len(frames) == 1
    assert frames[0].arbitration_id == 0x7FE
