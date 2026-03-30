#!/usr/bin/env python3
import argparse
import audioop
import ipaddress
import math
import signal
import subprocess
import sys
import struct
import threading
import time
import wave

try:
    import pyVoIP
    import pyVoIP.RTP as RTP
    from pyVoIP.VoIP import CallState, VoIPPhone
except Exception as exc:
    sys.stderr.write(
        "pyVoIP is required. Run with:\n"
        "  uv run --with pyVoIP scripts/pyvoip_call.py ...\n"
    )
    raise


def detect_tailscale_ip() -> str | None:
    try:
        output = subprocess.check_output(["/sbin/ifconfig"], text=True)
    except Exception:
        return None

    ts_net = ipaddress.ip_network("100.64.0.0/10")
    for line in output.splitlines():
        line = line.strip()
        if not line.startswith("inet "):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        ip = parts[1]
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            continue
        if addr in ts_net:
            return ip
    return None


def build_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Place a SIP call to Asterisk via pyVoIP."
    )
    parser.add_argument("--server", required=True, help="Asterisk host/IP")
    parser.add_argument("--port", type=int, default=5160, help="SIP port")
    parser.add_argument("--user", default="pyclient", help="SIP username")
    parser.add_argument(
        "--password", default="pyclientpass", help="SIP password"
    )
    parser.add_argument("--number", required=True, help="Dialed number")
    parser.add_argument(
        "--audio-file",
        default="",
        help="Optional WAV file to stream to the call",
    )
    parser.add_argument(
        "--sine",
        action="store_true",
        help="Generate and stream a sine tone instead of a WAV file",
    )
    parser.add_argument(
        "--sine-hz",
        type=int,
        default=1000,
        help="Sine tone frequency (Hz)",
    )
    parser.add_argument(
        "--sine-seconds",
        type=float,
        default=5.0,
        help="Sine tone duration (seconds)",
    )
    parser.add_argument(
        "--audio-delay",
        type=float,
        default=1.5,
        help="Seconds to wait after answer before streaming audio",
    )
    parser.add_argument(
        "--prefill",
        action="store_true",
        help="Write all audio frames immediately to avoid RTP underflow",
    )
    parser.add_argument(
        "--record-file",
        default="",
        help="Optional WAV file to save inbound audio (8kHz, 8-bit mono)",
    )
    parser.add_argument(
        "--no-register",
        action="store_true",
        help="Skip SIP REGISTER and rely on INVITE auth challenge",
    )
    parser.add_argument(
        "--local-ip",
        default="",
        help="Local IP to bind (defaults to Tailscale IP if found)",
    )
    parser.add_argument(
        "--sip-port",
        type=int,
        default=5062,
        help="Local SIP port to bind",
    )
    parser.add_argument(
        "--rtp-low", type=int, default=10000, help="Local RTP low port"
    )
    parser.add_argument(
        "--rtp-high", type=int, default=10200, help="Local RTP high port"
    )
    parser.add_argument(
        "--connect-timeout",
        type=int,
        default=30,
        help="Seconds to wait for answer",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Seconds to keep call up after answer",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable pyVoIP debug output"
    )
    return parser.parse_args()


def load_wav_audio(path: str, target_rate: int = 8000) -> bytes:
    with wave.open(path, "rb") as wf:
        channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        frames = wf.readframes(wf.getnframes())

    # Convert to 16-bit signed mono, resample, then encode as PCMU (ulaw).
    if sampwidth != 2:
        frames = audioop.lin2lin(frames, sampwidth, 2)
        sampwidth = 2

    if channels != 1:
        frames = audioop.tomono(frames, sampwidth, 0.5, 0.5)
        channels = 1

    if framerate != target_rate:
        frames, _state = audioop.ratecv(
            frames, sampwidth, channels, framerate, target_rate, None
        )

    frames = audioop.lin2ulaw(frames, 2)
    return frames


def generate_sine_ulaw(
    seconds: float, freq_hz: int, rate: int = 8000, amplitude: float = 0.4
) -> bytes:
    total_samples = max(0, int(seconds * rate))
    amp = int(32767 * amplitude)
    pcm = bytearray(total_samples * 2)
    for i in range(total_samples):
        sample = int(amp * math.sin(2 * math.pi * freq_hz * i / rate))
        struct.pack_into("<h", pcm, i * 2, sample)
    return audioop.lin2ulaw(bytes(pcm), 2)


def stream_audio(call, data: bytes, rate: int = 8000, prefill: bool = False) -> None:
    frame_size = 160  # 20ms at 8kHz, 8-bit
    frame_time = frame_size / rate
    pad = b"\xff" * frame_size  # ulaw silence
    idx = 0
    if prefill:
        while idx < len(data):
            chunk = data[idx : idx + frame_size]
            if len(chunk) < frame_size:
                chunk = chunk + pad[: frame_size - len(chunk)]
            call.write_audio(chunk)
            idx += frame_size
        return
    while call.state == CallState.ANSWERED and idx < len(data):
        chunk = data[idx : idx + frame_size]
        if len(chunk) < frame_size:
            chunk = chunk + pad[: frame_size - len(chunk)]
        call.write_audio(chunk)
        idx += frame_size
        time.sleep(frame_time)


def record_audio(call, path: str, rate: int = 8000) -> None:
    try:
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(1)
            wf.setframerate(rate)
            while call.state == CallState.ANSWERED:
                data = call.read_audio(160, blocking=True)
                wf.writeframes(data)
    except Exception:
        return


def enable_ulaw_passthrough() -> None:
    def _passthrough(self, packet: bytes) -> bytes:
        return packet

    RTP.RTPClient.encode_pcmu = _passthrough


def main() -> None:
    args = build_args()

    if args.debug:
        pyVoIP.DEBUG = True

    local_ip = args.local_ip.strip()
    if not local_ip:
        local_ip = detect_tailscale_ip() or ""
    if not local_ip:
        sys.stderr.write(
            "Could not detect a Tailscale IP. Provide --local-ip.\n"
        )
        sys.exit(1)

    phone = VoIPPhone(
        args.server,
        args.port,
        args.user,
        args.password,
        myIP=local_ip,
        sipPort=args.sip_port,
        rtpPortLow=args.rtp_low,
        rtpPortHigh=args.rtp_high,
    )

    def handle_sigint(_sig, _frame):
        try:
            phone.stop()
        finally:
            sys.exit(0)

    signal.signal(signal.SIGINT, handle_sigint)

    def ensure_blocking():
        # pyVoIP leaves sockets non-blocking after REGISTER; invite expects blocking.
        try:
            phone.sip.s.setblocking(True)
            phone.sip.out.setblocking(True)
        except Exception:
            pass

    if args.no_register:
        phone.sip.register = lambda: True
    phone.start()
    ensure_blocking()

    try:
        ensure_blocking()
        call = phone.call(args.number)
    except BlockingIOError:
        time.sleep(0.2)
        ensure_blocking()
        call = phone.call(args.number)
    print(f"Calling {args.number} via {args.server}:{args.port}...")

    start = time.time()
    while call.state == CallState.DIALING:
        if time.time() - start > args.connect_timeout:
            print("Call not answered before timeout.")
            break
        time.sleep(0.2)

    if call.state == CallState.ANSWERED:
        print("Call answered.")
        answered_at = time.time()
        if args.audio_file or args.sine:
            enable_ulaw_passthrough()
        record_thread = None
        if args.record_file:
            record_thread = threading.Thread(
                target=record_audio, args=(call, args.record_file), daemon=True
            )
            record_thread.start()
        audio_data = None
        if args.sine:
            audio_data = generate_sine_ulaw(args.sine_seconds, args.sine_hz)
        elif args.audio_file:
            audio_data = load_wav_audio(args.audio_file)
        if audio_data:
            if args.audio_delay > 0:
                time.sleep(args.audio_delay)
            start = time.time()
            while (
                call.state == CallState.ANSWERED
                and not call.RTPClients
                and (time.time() - start) < 5
            ):
                time.sleep(0.05)
            stream_audio(call, audio_data, prefill=args.prefill)
        remaining = max(0, args.duration - int(time.time() - answered_at))
        if remaining:
            end = time.time() + remaining
            while time.time() < end and call.state == CallState.ANSWERED:
                time.sleep(0.5)
        try:
            call.hangup()
        except Exception:
            pass
        if record_thread:
            record_thread.join(timeout=2)
    else:
        print(f"Call state: {call.state}")

    phone.stop()


if __name__ == "__main__":
    main()
