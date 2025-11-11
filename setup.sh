#!/bin/bash
# FreePBX GSM Gateway Setup Script
# This script automates the deployment and configuration

set -e

echo "======================================"
echo "FreePBX GSM Gateway Setup"
echo "======================================"
echo ""

# Check if running on Unraid/Linux
if [ ! -e /dev/ttyUSB0 ]; then
    echo "Warning: /dev/ttyUSB0 not found. Make sure the USB modem is connected."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Step 1: Verifying USB modem..."
lsusb | grep -i 'quectel\|simcom' || echo "USB modem not detected!"
ls -la /dev/ttyUSB* 2>/dev/null || echo "No ttyUSB devices found!"
echo ""

echo "Step 2: Building and starting Docker containers..."
docker compose up -d --build
echo ""

echo "Step 3: Waiting for FreePBX to initialize (this may take 20-30 minutes on first run)..."
echo "Checking container status..."
docker compose ps
echo ""

echo "Waiting for web server to start..."
timeout=600
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker exec freepbx-chan-quectel pgrep apache2 > /dev/null 2>&1; then
        echo "Web server is running!"
        break
    fi
    echo -n "."
    sleep 10
    elapsed=$((elapsed + 10))
done
echo ""

if [ $elapsed -ge $timeout ]; then
    echo "Warning: Timed out waiting for web server. Check logs with: docker logs freepbx-chan-quectel"
fi

echo "Step 4: Fixing TTY device permissions..."
docker exec freepbx-chan-quectel chmod 666 /dev/ttyUSB* 2>/dev/null || echo "Could not set permissions"
echo ""

echo "Step 5: Loading chan_dongle module..."
sleep 5
docker exec freepbx-chan-quectel asterisk -rx 'module load chan_dongle.so' || echo "Module already loaded"
echo ""

echo "Step 6: Restarting dongle to establish connection..."
sleep 2
docker exec freepbx-chan-quectel asterisk -rx 'dongle restart now dongle0'
echo ""

echo "Step 7: Waiting for dongle to connect..."
sleep 10
echo ""

echo "Step 8: Checking dongle status..."
docker exec freepbx-chan-quectel asterisk -rx 'dongle show devices'
echo ""

echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "FreePBX Web UI: http://$(hostname -I | awk '{print $1}'):8081/admin"
echo ""
echo "Next steps:"
echo "1. Access the web UI and create an admin account"
echo "2. Test SMS: docker exec freepbx-chan-quectel asterisk -rx 'dongle sms dongle0 +1XXXXXXXXXX \"test\"'"
echo "3. View SMS log: docker exec freepbx-chan-quectel cat /var/log/asterisk/sms.log"
echo ""
echo "Useful commands:"
echo "  Check status: docker exec freepbx-chan-quectel asterisk -rx 'dongle show devices'"
echo "  View logs: docker logs -f freepbx-chan-quectel"
echo "  Restart: docker compose restart"
echo ""
