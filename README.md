# FreePBX + SIM7600 GSM Gateway

Docker-based setup for running FreePBX/Asterisk with GSM/LTE modem support via chan_dongle and chan_quectel.

## Setups

This repo contains two Docker setups:

| Setup | Base Image | Asterisk | Use Case |
|-------|-----------|----------|----------|
| **FreePBX** (production) | tiredofit/freepbx | 17.9.3 | Full FreePBX with web UI |
| **Asterisk 23** (dev/CI) | andrius/asterisk:23 | 23.x | Standalone Asterisk for testing |

## Quick Start (FreePBX)

### 1. Clone and Configure

```bash
git clone https://github.com/navanchauhan/freepbx-gsm-gateway.git
cd freepbx-gsm-gateway
cp .env.example .env
# Edit .env with your settings
```

### 2. Verify USB Modem

```bash
lsusb | grep -i 'quectel\|simcom'
# Should show: ID 1e0e:9011 Qualcomm / Option SimTech

ls -la /dev/ttyUSB*
# Should show: /dev/ttyUSB0 through /dev/ttyUSB4
```

### 3. Deploy

```bash
docker compose -f docker-compose.freepbx.yml up -d --build
```

Initial setup takes 15-20 minutes for FreePBX installation.

### 4. Access FreePBX

- **Web UI**: `http://<host-ip>:${HTTP_PORT}/admin` (default: 8080)
- **HTTPS**: `https://<host-ip>:${HTTPS_PORT}/admin` (default: 8443)

### 5. Validate Modem

```bash
docker exec -it freepbx-sim7600 asterisk -rx "module show like chan_dongle"
docker exec -it freepbx-sim7600 asterisk -rx "dongle show devices"
docker exec -it freepbx-sim7600 asterisk -rx "dongle show device state dongle0"
```

To restart the modem channel:
```bash
docker exec -it freepbx-sim7600 asterisk -rx "dongle start dongle0"
```

## Configuration

### Environment Variables (.env)

| Variable | Default | Description |
|----------|---------|-------------|
| TZ | UTC | Timezone |
| HTTP_PORT | 8080 | FreePBX HTTP port |
| HTTPS_PORT | 8443 | FreePBX HTTPS port |
| SIP_PORT_UDP | 5060 | SIP signaling (UDP) |
| SIP_PORT_TCP | 5060 | SIP signaling (TCP) |
| PJSIP_PORT_UDP | 5160 | PJSIP signaling |
| RTP_PORT_START | 18000 | RTP media range start |
| RTP_PORT_END | 20000 | RTP media range end |
| ADMIN_EMAIL | admin@example.com | FreePBX admin email |
| ADMIN_PASSWORD | change-me | FreePBX admin password |

### Asterisk Config Files

Located in `asterisk/`:

| File | Purpose |
|------|---------|
| `dongle.conf` | chan_dongle device config |
| `quectel.conf` | chan_quectel device config |
| `extensions_custom.conf` | Custom dialplan |
| `modules_custom.conf` | Force-load modules |

### SIM7600 Port Mapping

| Port | Function |
|------|----------|
| ttyUSB0 | Diagnostic |
| ttyUSB1 | Audio |
| ttyUSB2 | AT Commands (Data) |
| ttyUSB3 | Modem |
| ttyUSB4 | Reserved |

Default config: `audio=/dev/ttyUSB1`, `data=/dev/ttyUSB2`

## FreePBX Trunk Setup

Create a **Custom Trunk** in FreePBX:

**chan_dongle:**
```
Dongle/dongle0/${OUTNUM}$
```

**chan_quectel:**
```
Quectel/quectel0/${OUTNUM}$
```

Then create an outbound route using that trunk.

## Usage

### Send SMS

```bash
docker exec freepbx-sim7600 asterisk -rx 'dongle sms dongle0 +1XXXXXXXXXX "Your message"'
```

### Check Signal/Status

```bash
docker exec freepbx-sim7600 asterisk -rx 'dongle show devices'
```

### View Logs

```bash
docker exec freepbx-sim7600 tail -f /var/log/asterisk/full
```

## Troubleshooting

### Module Won't Load

```bash
docker exec freepbx-sim7600 asterisk -rx 'module load chan_dongle.so'
docker exec freepbx-sim7600 asterisk -rx 'dongle restart now dongle0'
```

### Permission Denied on TTY

The container includes a startup script that sets permissions, but if needed:
```bash
docker exec freepbx-sim7600 chmod 666 /dev/ttyUSB*
```

### Dongle Shows "Not Connected"

Try swapping audio/data ports in `asterisk/dongle.conf`:
```ini
audio=/dev/ttyUSB3
data=/dev/ttyUSB2
```

### Container Won't Start

Check logs:
```bash
docker logs freepbx-sim7600
```

## Development Setup (Asterisk 23)

For development/testing with standalone Asterisk 23:

```bash
docker compose up -d --build
```

Uses `Dockerfile` with `andrius/asterisk:23` base and chan_dongle compiled from the [navanchauhan fork](https://github.com/navanchauhan/asterisk-chan-dongle) (Asterisk 18-23 compatible).

## Channel Drivers

| Driver | Best For | Notes |
|--------|----------|-------|
| chan_dongle | Classic GSM modems | Confirmed working with SIM7600 |
| chan_quectel | LTE modems with UAC | Better USB Audio Class support |

Both are built and available in the FreePBX image. Enable in `asterisk/modules_custom.conf`.

## Files

```
.
├── Dockerfile              # Asterisk 23 standalone
├── Dockerfile.ast23        # Asterisk 23 CI build
├── Dockerfile.freepbx      # FreePBX production
├── docker-compose.yml      # Asterisk 23 compose
├── docker-compose.freepbx.yml  # FreePBX compose
├── .env.example            # Environment template
├── asterisk/               # Asterisk configs
│   ├── dongle.conf
│   ├── quectel.conf
│   ├── extensions_custom.conf
│   └── modules_custom.conf
├── configs/                # Legacy config location
└── data/                   # FreePBX persistent data
```

## Hardware

- **Modem**: Waveshare SIM7600G-H (or compatible Quectel/Simcom)
- **SIM**: Any active SIM card (tested with Tello/T-Mobile)

## Credits

- FreePBX Docker: [tiredofit/freepbx](https://github.com/tiredofit/docker-freepbx)
- chan_dongle: [wdoekes/asterisk-chan-dongle](https://github.com/wdoekes/asterisk-chan-dongle)
- chan_dongle (Ast 18-23): [navanchauhan/asterisk-chan-dongle](https://github.com/navanchauhan/asterisk-chan-dongle)
- chan_quectel: [IchthysMaranatha/asterisk-chan-quectel](https://github.com/IchthysMaranatha/asterisk-chan-quectel)
