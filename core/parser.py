import cantools

db = cantools.database.load_file(
    'dbcs/toyota_adas.dbc', database_format='dbc')
print(f"[INFO] Total messages found in this DBC: {len(db.messages)}\n")
print("=" * 50)

print("Let's look at the first 5 messages in detail:")
print("=" * 50)

for msg in db.messages[:5]:
    print(f"Message Name : {msg.name}")
    print(f"CAN ID (Hex) : {hex(msg.frame_id)}")
    print(f"Data Length  : {msg.length} bytes")
    print("Signals Inside:")

    # Each message contains one or more 'signals' (the actual data points)
    for signal in msg.signals:
        print(
            f"   -> Signal: {signal.name} (Bits: {signal.start} to {signal.start + signal.length - 1}, Unit: {signal.unit})")

    print("-" * 50)
