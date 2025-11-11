#!/bin/bash
# Post-installation script to configure chan_dongle and SIP
# Run this after FreePBX finishes initialization

set -e

echo "Post-Installation Configuration Script"
echo "======================================="
echo ""

# Wait for FreePBX to be ready
echo "Waiting for FreePBX web server..."
while ! docker exec freepbx-chan-quectel pgrep apache2 >/dev/null 2>&1; do
    echo -n "."
    sleep 5
done
echo " Ready!"
echo ""

# Fix TTY permissions
echo "Fixing TTY device permissions..."
docker exec freepbx-chan-quectel chmod 666 /dev/ttyUSB* 2>/dev/null
echo "Done"
echo ""

# Create chan_dongle config
echo "Creating chan_dongle configuration..."
docker exec freepbx-chan-quectel bash -c 'cat > /etc/asterisk/dongle.conf << "EOFDONGLE"
[general]
interval=15

[defaults]
context=from-dongle
group=0
rxgain=0
txgain=0
autodeletesms=yes
resetdongle=yes
u2diag=-1
usecallingpres=yes
callingpres=allowed_passed_screen
disablesms=no
language=en
smsaspdu=yes

[dongle0]
audio=/dev/ttyUSB3
data=/dev/ttyUSB2
context=from-dongle
group=1
rxgain=4
txgain=4
autodeletesms=yes
resetdongle=yes
disable=no
initstate=start
EOFDONGLE
'
echo "Done"
echo ""

# Create SIP extension
echo "Creating SIP extension 100..."
docker exec freepbx-chan-quectel bash -c 'cat > /etc/asterisk/sip_custom.conf << "EOFSIP"

[100]
type=friend
context=from-internal
host=dynamic
secret=CallMe2024!
dtmfmode=rfc2833
canreinvite=no
nat=yes
disallow=all
allow=ulaw
allow=alaw
allow=g722
qualify=yes
directmedia=no
EOFSIP
'
echo "Done"
echo ""

# Create dialplan for SMS and calls
echo "Creating dialplan..."
docker exec freepbx-chan-quectel bash -c 'cat > /etc/asterisk/extensions_custom.conf << "EOFDIALPLAN"
[from-dongle]
; Handle incoming SMS messages
exten => sms,1,NoOp(Incoming SMS from ${CALLERID(num)})
exten => sms,n,NoOp(Message: ${SMS})
exten => sms,n,System(echo "$(date) - From: ${CALLERID(num)} - Message: ${SMS}" >> /var/log/asterisk/sms.log)
exten => sms,n,Verbose(1,SMS from ${CALLERID(num)}: ${SMS})
exten => sms,n,Hangup()

; Handle incoming voice calls - ring extension 100
exten => _X.,1,NoOp(Incoming call from ${CALLERID(num)})
exten => _X.,n,Dial(SIP/100,30,tr)
exten => _X.,n,Hangup()

[from-internal-custom]
; Outbound calls through GSM dongle
; Match 10-digit US numbers
exten => _NXXXXXXXXX,1,NoOp(Outbound call to ${EXTEN})
exten => _NXXXXXXXXX,n,Set(CALLERID(num)=YOUR_PHONE_NUMBER)
exten => _NXXXXXXXXX,n,Dial(Dongle/dongle0/${EXTEN},60,tr)
exten => _NXXXXXXXXX,n,Hangup()

; Match 11-digit US numbers (1+area code)
exten => _1NXXXXXXXXX,1,NoOp(Outbound call to ${EXTEN})
exten => _1NXXXXXXXXX,n,Set(CALLERID(num)=YOUR_PHONE_NUMBER)
exten => _1NXXXXXXXXX,n,Dial(Dongle/dongle0/${EXTEN},60,tr)
exten => _1NXXXXXXXXX,n,Hangup()

; International calls
exten => _011.,1,NoOp(International call to ${EXTEN})
exten => _011.,n,Set(CALLERID(num)=YOUR_PHONE_NUMBER)
exten => _011.,n,Dial(Dongle/dongle0/${EXTEN},60,tr)
exten => _011.,n,Hangup()
EOFDIALPLAN
'
echo "Done"
echo ""

# Reload Asterisk modules
echo "Reloading Asterisk configuration..."
docker exec freepbx-chan-quectel asterisk -rx 'sip reload'
docker exec freepbx-chan-quectel asterisk -rx 'dialplan reload'
echo "Done"
echo ""

# Load chan_dongle
echo "Loading chan_dongle module..."
docker exec freepbx-chan-quectel asterisk -rx 'module load chan_dongle.so' || echo "Module already loaded"
sleep 3
echo "Done"
echo ""

# Restart dongle
echo "Restarting dongle..."
docker exec freepbx-chan-quectel asterisk -rx 'dongle restart now dongle0'
sleep 5
echo "Done"
echo ""

# Check status
echo "Checking dongle status..."
docker exec freepbx-chan-quectel asterisk -rx 'dongle show devices'
echo ""

echo "Checking SIP peers..."
docker exec freepbx-chan-quectel asterisk -rx 'sip show peers'
echo ""

echo "======================================="
echo "Configuration Complete!"
echo "======================================="
echo ""
echo "SIP Extension Created:"
echo "  Extension: 100"
echo "  Password: CallMe2024!"
echo "  Server: YOUR_UNRAID_IP:5160"
echo ""
echo "Connect your softphone with these settings!"
echo ""
