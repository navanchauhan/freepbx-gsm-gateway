# SIM7600 (LTE/VoLTE) Asterisk Gateway

Minimal, reproducible setup for a SIM7600G-H on Unraid using Asterisk 23 + `chan_quectel`.
This configuration matches the working hardware setup we validated.

## What’s included

- `Dockerfile.ast23` builds `chan_quectel` with SIM7600 CLCC-noise patch
- `docker-compose.yml` runs a single Asterisk container (`asterisk-sim7600`)
- `docker-compose.yml` also runs an SMS HTTP API (`sim7600-sms-api`)
- `asterisk/` configs for SIP + dialplan + modem
- `recordings/` bind-mount for call recordings
- `sounds/` bind-mount for custom audio
- `sms-api-data/` bind-mount for persisted chat/message history

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

Validate the SMS API:
```bash
curl http://localhost:${SMS_API_PORT:-8080}/healthz
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

## Dialplan examples (current)

These live in `asterisk/extensions_custom.conf`.

### play-audio
```asterisk
[play-audio]
exten => s,1,Answer()
 same => n,System(/usr/sbin/asterisk -rx "quectel cmd quectel0 AT+CHFA=0")
 same => n,System(/usr/sbin/asterisk -rx "quectel cmd quectel0 AT+CMICGAIN=3")
 same => n,System(/usr/sbin/asterisk -rx "quectel cmd quectel0 AT+COUTGAIN=8")
 same => n,System(/usr/sbin/asterisk -rx "quectel cmd quectel0 AT+CPCMREG=1")
 same => n,Set(AUDIO_FILE=${IF($["${AUDIO_FILE}"=""]?hello-world:${AUDIO_FILE})})
 same => n,Wait(1)
 same => n,Playback(${AUDIO_FILE})
 same => n,Wait(1)
 same => n,System(/usr/sbin/asterisk -rx "quectel cmd quectel0 AT+CPCMREG=0")
 same => n,Hangup()
```

### record-call
```asterisk
[record-call]
exten => s,1,Answer()
 same => n,System(/usr/sbin/asterisk -rx "quectel cmd quectel0 AT+CHFA=0")
 same => n,System(/usr/sbin/asterisk -rx "quectel cmd quectel0 AT+CMICGAIN=3")
 same => n,System(/usr/sbin/asterisk -rx "quectel cmd quectel0 AT+COUTGAIN=8")
 same => n,System(/usr/sbin/asterisk -rx "quectel cmd quectel0 AT+CPCMREG=1")
 same => n,Set(RECFILE=/var/spool/asterisk/monitor/recording-${STRFTIME(${EPOCH},,%Y%m%d-%H%M%S)}.wav)
 same => n,MixMonitor(${RECFILE})
 same => n,Wait(600)
 same => n,System(/usr/sbin/asterisk -rx "quectel cmd quectel0 AT+CPCMREG=0")
 same => n,Hangup()
```

## SIP endpoint (direct config)

Edit `asterisk/pjsip_custom.conf` (default user `pyclient` / `pyclientpass`), then:
```bash
docker exec asterisk-sim7600 asterisk -rx "pjsip reload"
```

Use the `[from-pjsip]` rules in `asterisk/extensions_custom.conf` (PJSIP listens on UDP `5160`).

## SMS HTTP API

The repo now includes a FastAPI service that wraps outbound `quectel sms` and stores chats/messages in SQLite.
It is intentionally SMS-only for now:

- one sender line (`SMS_DEVICE`, default `quectel0`)
- one recipient per chat
- plain text only
- outbound messages are queued through Asterisk AMI
- inbound messages are pushed into the same store from the `[quectel-incoming]` dialplan
- realtime delivery is available through webhooks, server-sent events, and WebSockets

### Auth

Set these in `.env` before exposing the API:

```bash
SMS_API_BEARER_TOKEN=replace-me
SMS_API_INTERNAL_TOKEN=replace-me-too
```

If you change `SMS_API_INTERNAL_TOKEN`, update `SMS_API_INTERNAL_TOKEN` in `asterisk/extensions_custom.conf` to match before reloading the dialplan.

Browser clients can also use `access_token=<SMS_API_BEARER_TOKEN>` on the SSE and WebSocket endpoints when they cannot set an `Authorization` header directly.

### Endpoints

- `GET /healthz`
- `GET /v3/phone_numbers`
- `GET /v3/chats`
- `POST /v3/chats`
- `GET /v3/chats/{chatId}`
- `GET /v3/chats/{chatId}/messages`
- `POST /v3/chats/{chatId}/messages`
- `GET /v3/webhooks`
- `POST /v3/webhooks`
- `DELETE /v3/webhooks/{webhookId}`
- `GET /v3/events/stream`
- `GET /v3/events/ws` (WebSocket)

Interactive docs:

```bash
open http://localhost:${SMS_API_PORT:-8080}/docs
```

### Example: list phone numbers

```bash
curl http://localhost:${SMS_API_PORT:-8080}/v3/phone_numbers \
  -H "Authorization: Bearer ${SMS_API_BEARER_TOKEN}"
```

### Example: create a chat and send the first SMS

```bash
curl http://localhost:${SMS_API_PORT:-8080}/v3/chats \
  -H "Authorization: Bearer ${SMS_API_BEARER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+17203454122",
    "to": ["+17208828227"],
    "message": {
      "parts": [
        { "type": "text", "value": "hello from the SIM7600 gateway" }
      ],
      "idempotency_key": "demo-chat-1"
    }
  }'
```

### Example: send a follow-up SMS

```bash
curl http://localhost:${SMS_API_PORT:-8080}/v3/chats/<chat-id>/messages \
  -H "Authorization: Bearer ${SMS_API_BEARER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "parts": [
        { "type": "text", "value": "follow-up message" }
      ],
      "idempotency_key": "demo-chat-2"
    }
  }'
```

### Example: subscribe a webhook for live message events

Supported event types are:

- `message.inbound`
- `message.outbound`

If `event_types` is omitted, the subscription receives both.

```bash
curl http://localhost:${SMS_API_PORT:-8080}/v3/webhooks \
  -H "Authorization: Bearer ${SMS_API_BEARER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://example.com/hooks/sms",
    "event_types": ["message.inbound"],
    "secret": "replace-me"
  }'
```

Webhook deliveries are `POST`ed as JSON and include:

- `X-SMS-API-Event-Id`
- `X-SMS-API-Event-Type`
- `X-SMS-API-Signature-256: sha256=<hex>` when a secret is configured

### Example: stream events over SSE

If `events` is omitted, the stream includes both supported message event types.

```bash
curl -N "http://localhost:${SMS_API_PORT:-8080}/v3/events/stream?access_token=${SMS_API_BEARER_TOKEN}&events=message.inbound"
```

SSE payloads use standard event framing:

```text
id: <event-id>
event: message.inbound
data: {"id":"<event-id>","type":"message.inbound","occurred_at":"...","chat":{...},"message":{...}}
```

### Example: stream events over WebSocket

```bash
python3 - <<'PY'
import asyncio
import json
import websockets

async def main():
    uri = "ws://localhost:8080/v3/events/ws?access_token=change-me&events=message.inbound"
    async with websockets.connect(uri) as websocket:
        while True:
            print(json.loads(await websocket.recv()))

asyncio.run(main())
PY
```

WebSocket clients receive the same JSON event envelope as webhooks/SSE, plus periodic `system.keepalive` messages when the stream is idle.

### Notes

- The API normalizes 10-digit US numbers to `+1XXXXXXXXXX`.
- Outbound send currently supports single-line text only.
- `GET /v3/chats` and `GET /v3/chats/{chatId}/messages` use simple offset cursors.
- Message history persists in `./sms-api-data/sms_api.db`.
- Webhooks, SSE, and WebSocket streams fire for both inbound and outbound stored messages unless filtered with `event_types` / `events`.

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
