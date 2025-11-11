#!/bin/bash
echo "Monitoring FreePBX installation..."
echo "This will take 20-30 minutes. Checking every 30 seconds..."
echo ""

while true; do
    # Check if web server is running
    if docker exec freepbx-chan-quectel pgrep apache2 >/dev/null 2>&1; then
        echo ""
        echo "✅ FreePBX is ready! Starting configuration..."
        echo ""
        break
    fi
    
    # Show progress from logs
    LAST_LINE=$(docker logs freepbx-chan-quectel 2>&1 | tail -1)
    echo "$(date '+%H:%M:%S') - $LAST_LINE"
    
    sleep 30
done

# Now run all configuration
echo "Step 1: Fixing TTY permissions..."
docker exec freepbx-chan-quectel chmod 666 /dev/ttyUSB*
echo "Done"
echo ""

echo "Step 2: Creating chan_dongle config..."
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

echo "Step 3: Creating SIP extension 100..."
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

echo "Step 4: Creating dialplan..."
docker exec freepbx-chan-quectel bash -c 'cat > /etc/asterisk/extensions_custom.conf << "EOFDIALPLAN"
[from-dongle]
exten => sms,1,NoOp(Incoming SMS from ${CALLERID(num)})
exten => sms,n,NoOp(Message: ${SMS})
exten => sms,n,System(echo "$(date) - From: ${CALLERID(num)} - Message: ${SMS}" >> /var/log/asterisk/sms.log)
exten => sms,n,Verbose(1,SMS from ${CALLERID(num)}: ${SMS})
exten => sms,n,Hangup()

exten => _X.,1,NoOp(Incoming call from ${CALLERID(num)})
exten => _X.,n,Dial(SIP/100,30,tr)
exten => _X.,n,Hangup()

[from-internal-custom]
exten => _NXXXXXXXXX,1,NoOp(Outbound call to ${EXTEN})
exten => _NXXXXXXXXX,n,Set(CALLERID(num)=YOUR_PHONE_NUMBER)
exten => _NXXXXXXXXX,n,Dial(Dongle/dongle0/${EXTEN},60,tr)
exten => _NXXXXXXXXX,n,Hangup()

exten => _1NXXXXXXXXX,1,NoOp(Outbound call to ${EXTEN})
exten => _1NXXXXXXXXX,n,Set(CALLERID(num)=YOUR_PHONE_NUMBER)
exten => _1NXXXXXXXXX,n,Dial(Dongle/dongle0/${EXTEN},60,tr)
exten => _1NXXXXXXXXX,n,Hangup()

exten => _011.,1,NoOp(International call to ${EXTEN})
exten => _011.,n,Set(CALLERID(num)=YOUR_PHONE_NUMBER)
exten => _011.,n,Dial(Dongle/dongle0/${EXTEN},60,tr)
exten => _011.,n,Hangup()
EOFDIALPLAN
'
echo "Done"
echo ""

echo "Step 5: Reloading Asterisk modules..."
sleep 3
docker exec freepbx-chan-quectel asterisk -rx 'sip reload'
docker exec freepbx-chan-quectel asterisk -rx 'dialplan reload'
echo "Done"
echo ""

echo "Step 6: Loading chan_dongle..."
docker exec freepbx-chan-quectel asterisk -rx 'module load chan_dongle.so' || echo "Already loaded"
sleep 3
echo "Done"
echo ""

echo "Step 7: Restarting dongle..."
docker exec freepbx-chan-quectel asterisk -rx 'dongle restart now dongle0'
sleep 10
echo "Done"
echo ""

echo "=========================================="
echo "🎉 ALL CONFIGURATION COMPLETE!"
echo "=========================================="
echo ""
echo "Dongle Status:"
docker exec freepbx-chan-quectel asterisk -rx 'dongle show devices'
echo ""
echo "SIP Peers:"
docker exec freepbx-chan-quectel asterisk -rx 'sip show peers'
echo ""
echo "Connect your softphone:"
echo "  Server: YOUR_UNRAID_IP:5160"
echo "  Username: 100"
echo "  Password: CallMe2024!"
echo ""
