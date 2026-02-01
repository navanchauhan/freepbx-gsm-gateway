# SIM7600 (LTE/VoLTE) Asterisk Gateway

Minimal, reproducible setup for a SIM7600G-H on Unraid using Asterisk 23 + `chan_quectel`.
This configuration matches the working hardware setup we validated.

## What’s included

- `Dockerfile.ast23` builds `chan_quectel` with SIM7600 CLCC-noise patch
- `docker-compose.yml` runs a single Asterisk container (`asterisk-sim7600`)
- `asterisk/` configs for SIP + dialplan + modem
- `recordings/` bind-mount for call recordings
- `sounds/` bind-mount for custom audio

## Requirements

- SIM7600 in **serial-audio mode** (PID `9011`)
- `/dev/ttyUSB0..4` present
- `/dev/serial/by-id/*` present

If your `by-id` paths differ, update `asterisk/quectel.conf`.

## Quick start

```bash
cp .env.example .env

docker compose up -d --build
```

Validate device:
```bash
docker exec asterisk-sim7600 asterisk -rx "module show like quectel"
docker exec asterisk-sim7600 asterisk -rx "quectel show devices"
```

## Known‑good audio settings (SIM7600)

Working combo used:
- `audio=...-if06-port0`
- `data=...-if04-port0`
- `slin16=yes`
- AT commands before playback/record:
  - `AT+CHFA=0`
  - `AT+CMICGAIN=3`
  - `AT+COUTGAIN=8`

These are wired into the dialplan for playback + recording.

## Dialplan shortcuts

### Record a call to your phone
```bash
docker exec asterisk-sim7600 asterisk -rx \
  "originate Quectel/quectel0/1XXXXXXXXXX extension s@record-call"
```

Recording saved to:
```
./recordings/recording-YYYYMMDD-HHMMSS.wav
```

### Play custom audio to a call
1) Put an **8kHz mono PCM WAV** into `./sounds/` (example: `custom.wav`).
2) Call with:
```bash
docker exec asterisk-sim7600 asterisk -rx \
  "originate Quectel/quectel0/1XXXXXXXXXX extension s@play-audio"
```
By default it plays `hello-world`. To play your custom file, set:
```
AUDIO_FILE=custom/custom
```
(or edit the dialplan to hardcode your file).

To convert a WAV to 8k mono:
```bash
ffmpeg -i input.wav -ac 1 -ar 8000 -acodec pcm_s16le custom.wav
```

## SIP endpoint (direct config)

Edit `asterisk/pjsip_custom.conf` (default user `pyclient` / `pyclientpass`), then:
```bash
docker exec asterisk-sim7600 asterisk -rx "pjsip reload"
```

Use the `[from-pjsip]` rules in `asterisk/extensions_custom.conf` (PJSIP listens on UDP `5160`).

## PJSIP + Python control (dial + play + record)

1) Put an **8kHz mono PCM WAV** into `./sounds/` (example `intro.wav`).
2) Reload PJSIP + dialplan after edits:
```bash
docker exec asterisk-sim7600 asterisk -rx "pjsip reload"
docker exec asterisk-sim7600 asterisk -rx "dialplan reload"
```
3) Run the Python script from your machine:
```bash
python3 scripts/pjsip_call.py --server <unraid-ip> --number 17208828227 --audio-file custom/intro
```

Recording saved to:
```
./recordings/pjsip-<number>-YYYYMMDD-HHMMSS.wav
```

Notes:
- `--audio-file` is optional; default is `hello-world`.
- The script uses **PJSIP Python bindings** (`pjsua2`). Install/build PJSIP with Python support before running the script.

## Notes

- `Dockerfile.ast23` patches `chan_quectel` to ignore SIM7600 “VOICE CALL: BEGIN/END” noise in CLCC parsing.
- If audio is silent, verify the `if06` audio port and the AT gain commands above.
