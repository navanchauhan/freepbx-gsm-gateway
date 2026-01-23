# Asterisk Configuration Files

These configs are mounted into the FreePBX container:

- `dongle.conf` - chan_dongle device configuration
- `quectel.conf` - chan_quectel device configuration (alternative driver)
- `extensions_custom.conf` - Custom dialplan for inbound calls/SMS
- `modules_custom.conf` - Force-load non-FreePBX modules

## SIM7600 Port Mapping

The SIM7600 exposes multiple `/dev/ttyUSB*` interfaces:

| Port | Function |
|------|----------|
| ttyUSB0 | Diagnostic |
| ttyUSB1 | Audio (or NMEA) |
| ttyUSB2 | AT Commands (Data) |
| ttyUSB3 | Modem |
| ttyUSB4 | Reserved |

Default config uses:
- `audio=/dev/ttyUSB1`
- `data=/dev/ttyUSB2`

If dongle0 doesn't initialize, try swapping ports (e.g., `audio=/dev/ttyUSB3`).
