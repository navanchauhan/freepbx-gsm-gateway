# Troubleshooting Guide

## Common Issues and Solutions

### 1. USB Modem Not Detected

**Symptoms:**
- `lsusb` doesn't show the modem
- No `/dev/ttyUSB*` devices

**Solutions:**
```bash
# Check if modem is recognized by kernel
dmesg | tail -50 | grep -i usb

# Check USB devices
lsusb

# For Unraid: Enable USB passthrough in VM/Docker settings
# Navigate to: Settings → VM Manager → USB Devices
```

### 2. Permission Denied on TTY Devices

**Symptoms:**
```
WARNING chan_dongle.c: unable to open /dev/ttyUSB2: Permission denied
```

**Solution:**
```bash
# Fix permissions (temporary - lost on reboot)
docker exec freepbx-chan-quectel chmod 666 /dev/ttyUSB*

# Restart dongle
docker exec freepbx-chan-quectel asterisk -rx 'dongle restart now dongle0'

# For permanent fix, add to startup script
echo "docker exec freepbx-chan-quectel chmod 666 /dev/ttyUSB*" >> /boot/config/go
```

### 3. Module Won't Load

**Symptoms:**
```
Unable to load module chan_dongle.so
```

**Solutions:**
```bash
# Check for errors
docker exec freepbx-chan-quectel tail -100 /var/log/asterisk/full | grep -i dongle

# Check library dependencies
docker exec freepbx-chan-quectel ldd /usr/lib/asterisk/modules/chan_dongle.so

# Try manual load with verbose output
docker exec freepbx-chan-quectel asterisk -rvvv
*CLI> module load chan_dongle.so

# Rebuild container
docker compose down
docker compose up -d --build
```

### 4. Dongle Shows "Not connected"

**Symptoms:**
```
dongle0      1     Not connec 0    0    0       NONE
```

**Solutions:**
```bash
# Test AT commands manually
docker exec freepbx-chan-quectel bash -c 'echo AT | timeout 2 cat > /dev/ttyUSB2 && timeout 2 cat < /dev/ttyUSB2'
# Should return: AT\nOK

# Check for permission errors
docker exec freepbx-chan-quectel tail -50 /var/log/asterisk/full | grep -i 'permission\|denied'

# Fix permissions and restart
docker exec freepbx-chan-quectel chmod 666 /dev/ttyUSB*
docker exec freepbx-chan-quectel asterisk -rx 'dongle restart now dongle0'

# Check SIM card
docker exec freepbx-chan-quectel asterisk -rx 'dongle cmd dongle0 AT+CPIN?'
# Should return: +CPIN: READY
```

### 5. FreePBX Web UI Not Accessible

**Symptoms:**
- Cannot access http://SERVER_IP:8081
- Connection timeout

**Solutions:**
```bash
# Check if container is running
docker ps | grep freepbx

# Check if web server is running
docker exec freepbx-chan-quectel pgrep apache2

# Check logs
docker logs freepbx-chan-quectel | tail -50

# Check port binding
netstat -tuln | grep 8081

# Port already in use? Change in docker-compose.yml:
# ports:
#   - "8082:80"  # Use 8082 instead

# Restart container
docker compose restart
```

### 6. SMS Not Sending

**Symptoms:**
- SMS command returns but message not received

**Solutions:**
```bash
# Check signal strength
docker exec freepbx-chan-quectel asterisk -rx 'dongle show devices'
# RSSI should be > 0 (typically 15-31)

# Check if SIM has SMS capability
docker exec freepbx-chan-quectel asterisk -rx 'dongle cmd dongle0 AT+CMGF=1'

# Check SMS center number
docker exec freepbx-chan-quectel asterisk -rx 'dongle cmd dongle0 AT+CSCA?'

# Send test SMS with verbose logging
docker exec freepbx-chan-quectel asterisk -rvvv
*CLI> dongle sms dongle0 +1XXXXXXXXXX "test"

# Check for errors in logs
docker exec freepbx-chan-quectel tail -100 /var/log/asterisk/full | grep -i sms
```

### 7. SMS Not Received / Can't See Content

**Symptoms:**
- SMS arrives but content is empty or garbled

**Solutions:**
```bash
# Check SMS log
docker exec freepbx-chan-quectel cat /var/log/asterisk/sms.log

# Check if dialplan is loaded
docker exec freepbx-chan-quectel asterisk -rx 'dialplan show from-dongle'

# Reload dialplan
docker exec freepbx-chan-quectel asterisk -rx 'dialplan reload'

# Enable verbose logging
docker exec freepbx-chan-quectel asterisk -rx 'core set verbose 5'

# Watch logs in real-time
docker exec freepbx-chan-quectel tail -f /var/log/asterisk/full | grep -i sms
```

### 8. Container Keeps Restarting

**Symptoms:**
- `docker ps` shows container constantly restarting

**Solutions:**
```bash
# Check container logs
docker logs freepbx-chan-quectel

# Common causes:
# - Port already in use (change port in docker-compose.yml)
# - Insufficient memory (increase Docker memory limit)
# - Corrupted volume (remove and recreate)

# Remove and recreate:
docker compose down
docker volume rm call-me-maybe_freepbx-data
docker compose up -d
```

### 9. After Host Reboot

**Symptoms:**
- Dongle not connecting after server restart

**Solutions:**
```bash
# Fix permissions (they're reset on reboot)
docker exec freepbx-chan-quectel chmod 666 /dev/ttyUSB*

# Reload module
docker exec freepbx-chan-quectel asterisk -rx 'module reload chan_dongle.so'

# Restart dongle
docker exec freepbx-chan-quectel asterisk -rx 'dongle restart now dongle0'

# Create startup script for Unraid
# Add to /boot/config/go:
#!/bin/bash
sleep 30
docker exec freepbx-chan-quectel chmod 666 /dev/ttyUSB* 2>/dev/null
docker exec freepbx-chan-quectel asterisk -rx 'dongle restart now dongle0' 2>/dev/null
```

### 10. Build Fails

**Symptoms:**
- Docker build errors during `docker compose up --build`

**Solutions:**
```bash
# Common: Repository issues
# The Dockerfile uses Debian Buster archive repos
# If they're unavailable, try:

# Build with no cache
docker compose build --no-cache

# Check if archive.debian.org is accessible
ping archive.debian.org

# Alternative: Use pre-built image (if available)
# Or build on another machine and import
```

## Diagnostic Commands

### Check Overall Status
```bash
# Container status
docker ps -a | grep freepbx

# Dongle status
docker exec freepbx-chan-quectel asterisk -rx 'dongle show devices'

# Module status
docker exec freepbx-chan-quectel asterisk -rx 'module show like dongle'

# Asterisk status
docker exec freepbx-chan-quectel asterisk -rx 'core show version'
```

### Check Logs
```bash
# Container logs
docker logs freepbx-chan-quectel

# Asterisk full log
docker exec freepbx-chan-quectel tail -100 /var/log/asterisk/full

# SMS log
docker exec freepbx-chan-quectel cat /var/log/asterisk/sms.log

# Real-time Asterisk console
docker exec -it freepbx-chan-quectel asterisk -rvvv
```

### Test Modem
```bash
# Test AT commands
docker exec freepbx-chan-quectel bash -c 'echo AT | cat > /dev/ttyUSB2 && timeout 2 cat < /dev/ttyUSB2'

# Check SIM status
docker exec freepbx-chan-quectel asterisk -rx 'dongle cmd dongle0 AT+CPIN?'

# Check signal
docker exec freepbx-chan-quectel asterisk -rx 'dongle cmd dongle0 AT+CSQ'

# Check network registration
docker exec freepbx-chan-quectel asterisk -rx 'dongle cmd dongle0 AT+CREG?'

# Check SMS center
docker exec freepbx-chan-quectel asterisk -rx 'dongle cmd dongle0 AT+CSCA?'
```

## Getting Help

If you're still having issues:

1. Check logs: `docker logs freepbx-chan-quectel > freepbx.log`
2. Gather dongle info: `docker exec freepbx-chan-quectel asterisk -rx 'dongle show devices' > dongle-status.txt`
3. Export configuration: `docker exec freepbx-chan-quectel cat /etc/asterisk/dongle.conf > dongle.conf.current`
4. Check kernel messages: `dmesg | grep -i 'usb\|tty' > dmesg.log`

## Reset Everything

If all else fails, complete reset:

```bash
# Stop and remove everything
docker compose down
docker volume rm call-me-maybe_freepbx-data
docker system prune -a

# Start fresh
docker compose up -d --build

# Wait for initialization (20-30 minutes)
# Then run post-setup commands
docker exec freepbx-chan-quectel chmod 666 /dev/ttyUSB*
docker exec freepbx-chan-quectel asterisk -rx 'module load chan_dongle.so'
docker exec freepbx-chan-quectel asterisk -rx 'dongle restart now dongle0'
```
