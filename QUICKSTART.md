# Quick Start Guide

## Prerequisites

- Unraid server with Docker
- SIM7600G-H USB modem plugged in
- Active SIM card

## 5-Minute Setup

### 1. Deploy

```bash
cd /mnt/cache/exp/
git clone <your-repo> call-me-maybe
cd call-me-maybe
./setup.sh
```

### 2. Access Web UI

Open: http://YOUR_SERVER_IP:8081/admin

Create admin account when prompted.

### 3. Send Test SMS

```bash
docker exec freepbx-chan-quectel asterisk -rx 'dongle sms dongle0 +1XXXXXXXXXX "Hello World"'
```

### 4. Check Received SMS

```bash
docker exec freepbx-chan-quectel cat /var/log/asterisk/sms.log
```

## Essential Commands

### Status Checks
```bash
# Dongle status
docker exec freepbx-chan-quectel asterisk -rx 'dongle show devices'

# Container status
docker ps | grep freepbx

# View logs
docker logs -f freepbx-chan-quectel
```

### SMS Operations
```bash
# Send SMS
docker exec freepbx-chan-quectel asterisk -rx 'dongle sms dongle0 +1XXXXXXXXXX "message"'

# View SMS log
docker exec freepbx-chan-quectel cat /var/log/asterisk/sms.log

# Real-time SMS monitoring
docker exec freepbx-chan-quectel tail -f /var/log/asterisk/full | grep -i sms
```

### Troubleshooting
```bash
# Fix permissions (after reboot)
docker exec freepbx-chan-quectel chmod 666 /dev/ttyUSB*

# Restart dongle
docker exec freepbx-chan-quectel asterisk -rx 'dongle restart now dongle0'

# Reload configuration
docker exec freepbx-chan-quectel asterisk -rx 'module reload chan_dongle.so'
```

### Maintenance
```bash
# Restart container
docker compose restart

# View container logs
docker logs freepbx-chan-quectel

# Update and rebuild
docker compose down
docker compose up -d --build

# Backup data
docker run --rm -v call-me-maybe_freepbx-data:/data -v $(pwd):/backup ubuntu tar czf /backup/backup.tar.gz /data
```

## Next Steps

1. **Configure Trunks** - Set up outbound calling
2. **Add Extensions** - Create SIP extensions for phones
3. **Set up Inbound Routes** - Route calls to extensions/IVR
4. **Voicemail** - Configure voicemail boxes
5. **Auto-attendant** - Create IVR menus

See README.md for detailed instructions.

## Need Help?

- Check TROUBLESHOOTING.md
- View logs: `docker logs freepbx-chan-quectel`
- Join FreePBX community forums
