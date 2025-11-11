# SIP Trunk and Extension Setup Guide

This guide explains how to set up SIP connectivity to make and receive calls through your GSM dongle.

## Overview

You have two main options:
1. **Local Extensions** - SIP phones/softphones register to FreePBX
2. **External SIP Trunk** - Expose FreePBX as a SIP trunk to another PBX

## Option 1: SIP Extensions (Recommended)

This allows you to connect SIP softphones or desk phones to FreePBX and make calls through the GSM dongle.

### Step 1: Access FreePBX Web UI

Navigate to: http://YOUR_UNRAID_IP:8081/admin

Login with your credentials (username: root, password: Cooldham21)

### Step 2: Create an Extension

1. Click **Applications** → **Extensions** → **Add Extension**
2. Select **Add New Chan_PJSIP Extension** (or Chan_SIP for older clients)
3. Fill in the form:

   **User Extension:**
   - Extension: `100` (or any number)
   - Display Name: `My Phone`

   **Secret:**
   - Secret: Generate a strong password (e.g., `MySecurePassword123!`)

   **Advanced:**
   - Leave most settings default
   - NAT: `Yes` (if connecting from external network)

4. Click **Submit**
5. Click **Apply Config** (red bar at top)

### Step 3: Create Trunk for GSM Dongle

1. Click **Connectivity** → **Trunks** → **Add Trunk** → **Add Custom Trunk**

2. Fill in the form:

   **General:**
   - Trunk Name: `GSM-Dongle`
   - Outbound CallerID: `YOUR_PHONE_NUMBER` (your GSM number)

   **Dialed Number Manipulation Rules:**
   - Leave default or add patterns (e.g., prepend 1 for US numbers)

   **Custom Settings:**

   **Outgoing:**
   ```
   Dongle/dongle0/$OUTNUM$
   ```

   **Incoming:**
   ```
   context=from-trunk
   ```

3. Click **Submit**
4. Click **Apply Config**

### Step 4: Create Outbound Route

1. Click **Connectivity** → **Outbound Routes** → **Add Outbound Route**

2. Fill in the form:

   **Route Settings:**
   - Route Name: `GSM-Outbound`
   - Route Password: (leave empty)
   - Emergency Dialing: (optional)

   **Dial Patterns:**
   Click **Add** and add patterns for calls you want to route through GSM:

   - **US Mobile numbers:**
     - Prefix: (blank)
     - Match Pattern: `NXXXXXXXXX` (10-digit US numbers)

   - **US numbers with 1:**
     - Prefix: (blank)
     - Match Pattern: `1NXXXXXXXXX` (11-digit)

   - **International:**
     - Prefix: (blank)
     - Match Pattern: `011.` (international prefix)

   **Trunk Sequence:**
   - Select `GSM-Dongle` from Available Trunks
   - Click **Submit**

3. Click **Apply Config**

### Step 5: Create Inbound Route (for GSM calls)

1. Click **Connectivity** → **Inbound Routes** → **Add Incoming Route**

2. Fill in the form:

   **General:**
   - Description: `GSM-Incoming`
   - DID Number: `YOUR_PHONE_NUMBER` (your GSM number)

   **Set Destination:**
   - Destination: Select `Extensions` → Choose your extension (e.g., `100`)

3. Click **Submit**
4. Click **Apply Config**

### Step 6: Update Dongle Configuration

We need to ensure the dongle sends calls to the right context:

```bash
docker exec -it freepbx-chan-quectel bash
cat > /etc/asterisk/dongle.conf << 'EOF'
[general]
interval=15

[defaults]
context=from-trunk    ; Changed from 'from-dongle' to 'from-trunk'
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
context=from-trunk
group=1
rxgain=4
txgain=4
autodeletesms=yes
resetdongle=yes
disable=no
initstate=start
EOF

# Reload chan_dongle
asterisk -rx 'module reload chan_dongle.so'
exit
```

### Step 7: Configure Your SIP Client

Now connect a softphone (like Zoiper, Linphone, or Bria) or desk phone:

**SIP Settings:**
- **Username**: `100` (your extension number)
- **Password**: `MySecurePassword123!` (your secret)
- **Domain/Server**: `YOUR_UNRAID_IP` (your Unraid IP)
- **Port**: `5060`
- **Transport**: `UDP` (or TCP)

**Example: Zoiper Configuration**
1. Add Account → SIP
2. Username: `100`
3. Domain: `YOUR_UNRAID_IP`
4. Password: `MySecurePassword123!`
5. Outbound Proxy: (leave blank)
6. Save and register

### Step 8: Test Call

1. From your SIP phone, dial: `TEST_PHONE_NUMBER` (or any US number)
2. The call should route through your GSM dongle
3. You should hear ringing/connection

## Option 2: Remote SIP Trunk Access

To expose FreePBX as a SIP trunk that other systems can use:

### Configure FreePBX for External Access

1. **Security Considerations:**
   - Use strong passwords
   - Enable Fail2Ban
   - Limit IP access if possible

2. **Firewall Rules:**

   For Unraid, you may need to open ports:
   ```bash
   # On Unraid host
   iptables -A INPUT -p udp --dport 5060 -j ACCEPT
   iptables -A INPUT -p udp --dport 10000:10200 -j ACCEPT
   ```

3. **NAT Configuration:**

   In FreePBX:
   - Navigate to **Settings** → **Asterisk SIP Settings**
   - Set **External Address**: Your public IP or domain
   - Set **Local Networks**: `100.0.0.0/8` (for Tailscale)

4. **Create Trunk (on remote PBX):**

   ```
   [gsm-trunk]
   type=friend
   host=YOUR_UNRAID_IP
   port=5060
   username=gsm-trunk
   secret=YourStrongPassword
   context=from-external
   insecure=port,invite
   ```

## Testing & Verification

### Check Extension Status
```bash
docker exec freepbx-chan-quectel asterisk -rx 'pjsip show endpoints'
# or for chan_sip:
docker exec freepbx-chan-quectel asterisk -rx 'sip show peers'
```

### Check Active Calls
```bash
docker exec freepbx-chan-quectel asterisk -rx 'core show channels'
```

### Monitor Call Progress
```bash
docker exec freepbx-chan-quectel asterisk -rvvv
# Then watch console output while making a call
```

### Test Audio
```bash
# From Asterisk CLI
docker exec -it freepbx-chan-quectel asterisk -rvvv
*CLI> console dial 100@from-internal  # Dial extension 100
```

## Network Requirements

### Ports to Open

**For Local Network (Tailscale):**
- Already accessible, no firewall changes needed

**For Public Internet:**
- `5060/udp` - SIP signaling
- `5060/tcp` - SIP signaling (optional)
- `10000-10200/udp` - RTP (voice media)

### Tailscale Access

Your setup is already on Tailscale, so any device on your Tailscale network can connect:

```
SIP Server: YOUR_UNRAID_IP:5060
```

## Softphone Recommendations

**Desktop:**
- **Zoiper** (Windows/Mac/Linux) - Free version available
- **MicroSIP** (Windows) - Free, lightweight
- **Bria** (Cross-platform) - Commercial, feature-rich

**Mobile:**
- **Zoiper** (iOS/Android)
- **Linphone** (iOS/Android) - Open source
- **Bria Mobile** (iOS/Android)

**Web-based:**
- **JsSIP** - Browser-based WebRTC
- **SIPjs** - JavaScript library

## Advanced Configuration

### Voicemail Setup

1. Navigate to **Applications** → **Voicemail** → **Add Voicemail**
2. Voicemail ID: `100` (match extension)
3. Email: your@email.com
4. Attach Recording: `Yes`
5. Submit and Apply Config

### IVR (Auto Attendant)

1. Navigate to **Applications** → **IVR** → **Add IVR**
2. Configure menu options (Press 1 for Sales, etc.)
3. Record prompts
4. Route to extensions or queues

### Call Recording

1. Navigate to **Admin** → **Call Recording**
2. Set recording mode per extension
3. Recordings saved to `/var/spool/asterisk/monitor/`

### Ring Groups

1. Navigate to **Applications** → **Ring Groups**
2. Add multiple extensions
3. Choose ring strategy (Ring All, Hunt, etc.)

## Security Best Practices

### 1. Strong Passwords
```bash
# Generate secure password
openssl rand -base64 32
```

### 2. Fail2Ban (Already enabled in tiredofit image)
```bash
docker exec freepbx-chan-quectel fail2ban-client status asterisk
```

### 3. Restrict by IP

In FreePBX:
- **Settings** → **Asterisk SIP Settings**
- **Security** tab
- Add permitted IPs under "Permit"

### 4. Use TLS/SRTP

For encrypted calls:
1. Enable TLS in SIP settings
2. Configure certificates
3. Change port to 5061
4. Enable SRTP in extensions

### 5. Regular Updates
```bash
# Update container
docker compose pull
docker compose up -d
```

## Troubleshooting SIP

### Extension Won't Register

```bash
# Check if extension exists
docker exec freepbx-chan-quectel asterisk -rx 'pjsip show endpoints'

# Check for auth failures
docker exec freepbx-chan-quectel tail -50 /var/log/asterisk/full | grep -i auth

# Enable SIP debug
docker exec freepbx-chan-quectel asterisk -rx 'pjsip set logger on'
```

### No Audio on Calls

```bash
# Check RTP ports
docker exec freepbx-chan-quectel asterisk -rx 'rtp show settings'

# Common causes:
# - Firewall blocking RTP ports (10000-10200)
# - NAT issues
# - Codec mismatch

# Check codecs
docker exec freepbx-chan-quectel asterisk -rx 'core show codecs'
```

### Calls Don't Route to GSM

```bash
# Check trunk status
docker exec freepbx-chan-quectel asterisk -rx 'core show channels'

# Check dongle availability
docker exec freepbx-chan-quectel asterisk -rx 'dongle show devices'

# Enable dialplan debug
docker exec freepbx-chan-quectel asterisk -rx 'dialplan set debug on'
```

## Example: Complete Call Flow

**Outbound Call (Extension → GSM):**
1. SIP phone dials `TEST_PHONE_NUMBER`
2. FreePBX receives call on extension `100`
3. Outbound route matches pattern `1NXXXXXXXXX`
4. Routes to trunk `GSM-Dongle`
5. Trunk dials via `Dongle/dongle0/TEST_PHONE_NUMBER`
6. GSM modem places cellular call
7. Call connected

**Inbound Call (GSM → Extension):**
1. Cellular call arrives at GSM number `YOUR_PHONE_NUMBER`
2. chan_dongle receives call in context `from-trunk`
3. Inbound route matches DID `YOUR_PHONE_NUMBER`
4. Routes to extension `100`
5. SIP phone rings
6. User answers

## Next Steps

1. ✅ Set up first extension
2. ✅ Connect softphone
3. ✅ Make test call
4. Configure voicemail
5. Set up IVR menu
6. Add more extensions
7. Configure ring groups
8. Set up call recording

## Resources

- [FreePBX Wiki](https://wiki.freepbx.org/)
- [Asterisk Dialplan](https://wiki.asterisk.org/wiki/display/AST/Dialplan)
- [PJSIP Configuration](https://wiki.asterisk.org/wiki/display/AST/Configuring+res_pjsip)
- [SIP Debugging](https://wiki.asterisk.org/wiki/display/AST/SIP+Debugging)
