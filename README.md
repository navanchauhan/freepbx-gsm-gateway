# FreePBX GSM Gateway with SIM7600G-H on Unraid

Complete setup for running FreePBX with chan_dongle to use a SIM7600G-H USB GSM modem for SMS and voice calls.

## Hardware Requirements

- Unraid server
- Waveshare SIM7600G-H USB dongle (or compatible Quectel/Simcom modem)
- Active SIM card (tested with Tello)

## System Information

- **Unraid Server IP**: YOUR_UNRAID_IP (Tailscale)
- **FreePBX Web UI**: http://YOUR_UNRAID_IP:8081/admin
- **Phone Number**: +1 (720) 345-4122
- **Provider**: Tello
- **Modem Model**: SIMCOM SIM7600
- **Firmware**: LE20B04SIM

## Quick Start

### 1. Clone and Deploy

```bash
cd /mnt/cache/exp/
git clone <this-repo> call-me-maybe
cd call-me-maybe
```

### 2. Verify USB Modem

```bash
lsusb | grep -i 'quectel\|simcom'
# Should show: Bus 002 Device XXX: ID 1e0e:9011 Qualcomm / Option SimTech, Incorporated

ls -la /dev/ttyUSB*
# Should show: /dev/ttyUSB0 through /dev/ttyUSB4
```

### 3. Deploy Stack

```bash
docker compose up -d --build
```

Initial setup takes 20-30 minutes for FreePBX installation.

### 4. Access FreePBX

Navigate to: http://YOUR_UNRAID_IP:8081/admin

**First login**: Create admin account (username: root, password: your-password)

### 5. Fix Permissions and Load Module

```bash
# Fix TTY permissions
docker exec freepbx-chan-quectel chmod 666 /dev/ttyUSB*

# Load chan_dongle module
docker exec freepbx-chan-quectel asterisk -rx 'module load chan_dongle.so'

# Restart dongle to connect
docker exec freepbx-chan-quectel asterisk -rx 'dongle restart now dongle0'
```

### 6. Verify Operation

```bash
docker exec freepbx-chan-quectel asterisk -rx 'dongle show devices'
```

Should show:
```
ID           Group State      RSSI Mode Submode Provider Name  Model      Firmware          IMEI             IMSI             Number
dongle0      1     Free       31   0    0       Tello          SIMCOM_SIM +CGMR: LE20B04SIM YOUR_IMEI YOUR_SIM_ID  YOUR_PHONE_NUMBER
```

## Usage

### Send SMS

```bash
docker exec freepbx-chan-quectel asterisk -rx 'dongle sms dongle0 +1XXXXXXXXXX "Your message here"'
```

### View SMS Log

```bash
docker exec freepbx-chan-quectel cat /var/log/asterisk/sms.log
```

### Check Dongle Status

```bash
docker exec freepbx-chan-quectel asterisk -rx 'dongle show devices'
```

### Restart Dongle

```bash
docker exec freepbx-chan-quectel asterisk -rx 'dongle restart now dongle0'
```

### View Asterisk Logs

```bash
docker exec freepbx-chan-quectel tail -f /var/log/asterisk/full
```

## Configuration Files

### Core Files

- `docker-compose.yml` - Docker Compose configuration
- `Dockerfile` - Container build instructions
- `configs/dongle.conf` - Chan_dongle configuration
- `configs/extensions_custom.conf` - Asterisk dialplan for SMS

### Device Mapping

The SIM7600G-H creates 5 TTY devices:
- `/dev/ttyUSB0` - Control
- `/dev/ttyUSB1` - Reserved
- `/dev/ttyUSB2` - **AT Commands (Data port)**
- `/dev/ttyUSB3` - **Audio port**
- `/dev/ttyUSB4` - Reserved

## Troubleshooting

### Module Won't Load

```bash
# Check for errors
docker exec freepbx-chan-quectel tail -50 /var/log/asterisk/full | grep -i dongle

# Reload module
docker exec freepbx-chan-quectel asterisk -rx 'module unload chan_dongle.so'
docker exec freepbx-chan-quectel asterisk -rx 'module load chan_dongle.so'
```

### Permission Denied on TTY

```bash
docker exec freepbx-chan-quectel chmod 666 /dev/ttyUSB*
docker exec freepbx-chan-quectel asterisk -rx 'dongle restart now dongle0'
```

### Dongle Not Connecting

```bash
# Test AT commands directly
docker exec freepbx-chan-quectel bash -c 'echo AT | timeout 2 cat > /dev/ttyUSB2 && timeout 2 cat < /dev/ttyUSB2'
# Should return: AT OK

# Check signal strength
docker exec freepbx-chan-quectel asterisk -rx 'dongle show devices'
```

### Container Won't Start

```bash
# Check logs
docker logs freepbx-chan-quectel

# Check port conflicts
netstat -tuln | grep 8081

# Restart container
docker compose restart
```

### SMS Not Received

SMS messages are automatically logged to `/var/log/asterisk/sms.log` and deleted from the modem.

To view received messages:
```bash
docker exec freepbx-chan-quectel tail -20 /var/log/asterisk/sms.log
```

## Architecture

### Container Components

1. **FreePBX 15.0.16.56** - Web-based PBX management
2. **Asterisk 17.9.3** - VoIP/telephony engine
3. **chan_dongle** - GSM modem channel driver (compiled from wdoekes fork)
4. **MariaDB** - Embedded database
5. **Apache** - Web server

### Network Ports

- `8081` - FreePBX Web UI (HTTP)
- `5060` - SIP (TCP/UDP)
- `5061` - SIP TLS
- `10000-10200` - RTP (voice media)

## Advanced Configuration

### Setting Up Outbound Calling

1. Log into FreePBX web UI
2. Navigate to **Connectivity → Trunks**
3. Add Custom Trunk with dial string: `Dongle/dongle0/$OUTNUM$`

### Setting Up Inbound Routes

1. Navigate to **Connectivity → Inbound Routes**
2. Add route for DID: `YOUR_PHONE_NUMBER`
3. Route to extension or IVR

### Automated SMS Responses

Edit `configs/extensions_custom.conf` to add custom SMS handling logic.

## Backup

### Essential Files to Backup

```bash
# Configuration
/mnt/cache/exp/call-me-maybe/docker-compose.yml
/mnt/cache/exp/call-me-maybe/Dockerfile
/mnt/cache/exp/call-me-maybe/configs/

# FreePBX Data (in Docker volume)
docker run --rm -v call-me-maybe_freepbx-data:/data -v $(pwd):/backup ubuntu tar czf /backup/freepbx-backup.tar.gz /data
```

### Restore

```bash
# Extract backup
docker run --rm -v call-me-maybe_freepbx-data:/data -v $(pwd):/backup ubuntu bash -c "cd /data && tar xzf /backup/freepbx-backup.tar.gz --strip 1"
```

## Build Notes

### Chan_dongle Compilation

The chan_dongle module is compiled from source during container build:
- Fork: wdoekes/asterisk-chan-dongle
- Asterisk Version: 17.9.3
- Required libraries: libsqlite3-dev, autoconf, automake, libtool

### Permissions Fix

TTY devices must be readable/writable by the `asterisk` user inside the container:
```bash
chmod 666 /dev/ttyUSB*
```

## Known Issues

1. **Auto-delete SMS**: Messages are automatically deleted after receipt. This is by design (`autodeletesms=yes`).
2. **TTY Permissions**: Need to be fixed after container restart or host reboot.
3. **First Boot**: FreePBX takes 20-30 minutes to initialize on first run.

## Resources

- [Chan_dongle Fork (Asterisk 18-23)](https://github.com/navanchauhan/asterisk-chan-dongle)
- [Chan_dongle Upstream](https://github.com/wdoekes/asterisk-chan-dongle)
- [FreePBX Documentation](https://wiki.freepbx.org/)
- [Asterisk Documentation](https://wiki.asterisk.org/)
- [SIM7600 AT Commands](https://www.waveshare.com/wiki/SIM7600G-H)

## License

This configuration is provided as-is for personal/educational use.

## Credits

- FreePBX: [tiredofit/freepbx](https://github.com/tiredofit/docker-freepbx) Docker image
- chan_dongle: [navanchauhan/asterisk-chan-dongle](https://github.com/navanchauhan/asterisk-chan-dongle) (Asterisk 18-23 compatible fork)
- Original chan_dongle: bg111, maintained by wdoekes
- Hardware: Waveshare SIM7600G-H
