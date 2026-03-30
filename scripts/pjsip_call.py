#!/usr/bin/env python3
import argparse
import gc
import signal
import sys
import time

try:
    import pjsua2 as pj
except Exception as exc:
    sys.stderr.write(
        "pjsua2 is required (PJSIP Python bindings).\n"
        "Build PJSIP with Python support, then run this script again.\n"
    )
    sys.exit(1)


class SipAccount(pj.Account):
    def onRegState(self, prm):
        info = self.getInfo()
        reason = getattr(info, "regReason", None)
        if reason is None:
            reason = getattr(info, "regStatusText", "")
        print(f"Registration: {info.regStatus} {reason}")


class SipCall(pj.Call):
    def __init__(self, account, play_file="", record_file=""):
        super().__init__(account)
        self.disconnected = False
        self.play_file = play_file
        self.record_file = record_file
        self.player = None
        self.recorder = None

    def onCallState(self, prm):
        info = self.getInfo()
        print(
            f"Call state: {info.stateText} "
            f"({info.lastStatusCode} {info.lastReason})"
        )
        if info.state == pj.PJSIP_INV_STATE_DISCONNECTED:
            self.disconnected = True

    def onCallMediaState(self, prm):
        info = self.getInfo()
        for idx, media in enumerate(info.media):
            if media.type != pj.PJMEDIA_TYPE_AUDIO:
                continue
            if media.status != pj.PJSUA_CALL_MEDIA_ACTIVE:
                continue
            try:
                am = self.getAudioMedia(idx)
            except pj.Error:
                continue

            if self.play_file and self.player is None:
                self.player = pj.AudioMediaPlayer()
                self.player.createPlayer(self.play_file)
                self.player.startTransmit(am)

            if self.record_file and self.recorder is None:
                self.recorder = pj.AudioMediaRecorder()
                self.recorder.createRecorder(self.record_file)
                am.startTransmit(self.recorder)


def build_args():
    parser = argparse.ArgumentParser(
        description="Call into Asterisk PJSIP and dial out via SIM7600."
    )
    parser.add_argument("--server", required=True, help="Asterisk host/IP")
    parser.add_argument("--port", type=int, default=5160, help="PJSIP UDP port")
    parser.add_argument("--user", default="pyclient", help="SIP username")
    parser.add_argument("--password", default="pyclientpass", help="SIP password")
    parser.add_argument("--number", required=True, help="Destination phone number")
    parser.add_argument(
        "--audio-file",
        default="",
        help="Optional Asterisk sound name (e.g. custom/intro)",
    )
    parser.add_argument(
        "--play-file",
        default="",
        help="Local WAV file to stream over RTP (client-side audio)",
    )
    parser.add_argument(
        "--record-file",
        default="",
        help="Local WAV file to record inbound audio",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Hang up after N seconds (0 = no timeout)",
    )
    return parser.parse_args()


def main():
    args = build_args()

    ep = pj.Endpoint()
    ep.libCreate()

    ep_cfg = pj.EpConfig()
    ep_cfg.logConfig.level = 3
    ep_cfg.logConfig.consoleLevel = 3
    ep.libInit(ep_cfg)

    tcfg = pj.TransportConfig()
    tcfg.port = 0
    transport_id = ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, tcfg)
    ep.libStart()

    ep.audDevManager().setNullDev()

    acc_cfg = pj.AccountConfig()
    acc_cfg.idUri = f"sip:{args.user}@{args.server}"
    acc_cfg.regConfig.registrarUri = f"sip:{args.server}:{args.port}"
    acc_cfg.regConfig.registerOnAdd = False
    acc_cfg.sipConfig.transportId = transport_id
    acc_cfg.sipConfig.authCreds.append(
        pj.AuthCredInfo("digest", "*", args.user, 0, args.password)
    )

    account = SipAccount()
    account.create(acc_cfg)

    call = SipCall(
        account, play_file=args.play_file, record_file=args.record_file
    )
    call_prm = pj.CallOpParam(True)
    call_prm.opt.audioCount = 1
    call_prm.opt.videoCount = 0

    if args.audio_file:
        tx_opt = pj.SipTxOption()
        hdr = pj.SipHeader()
        hdr.hName = "X-Audio-File"
        hdr.hValue = args.audio_file
        tx_opt.headers.append(hdr)
        call_prm.txOption = tx_opt

    dest_uri = f"sip:{args.number}@{args.server}:{args.port}"
    call.makeCall(dest_uri, call_prm)

    def handle_sigint(_sig, _frame):
        if not call.disconnected:
            call.hangup(pj.CallOpParam())
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_sigint)

    start = time.time()
    try:
        while not call.disconnected:
            time.sleep(0.2)
            if args.timeout and (time.time() - start) > args.timeout:
                call.hangup(pj.CallOpParam())
                break
    finally:
        if call and not call.disconnected:
            try:
                call.hangup(pj.CallOpParam())
            except pj.Error:
                pass
        call = None
        account = None
        gc.collect()
        ep.libDestroy()


if __name__ == "__main__":
    main()
