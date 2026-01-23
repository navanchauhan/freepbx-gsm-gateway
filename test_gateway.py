#!/usr/bin/env python3
"""
Test script for Asterisk + SIM7600 GSM Gateway

Tests:
1. Send SMS via AMI (Asterisk Manager Interface)
2. Originate calls via AMI
3. Check dongle status

Requirements:
    pip install asterisk-ami

Usage:
    python test_gateway.py --host <asterisk-host> --sms +17208828227 "Test message"
    python test_gateway.py --host <asterisk-host> --call +17208828227
    python test_gateway.py --host <asterisk-host> --status
"""

import argparse
import socket
import time
import sys


class AsteriskAMI:
    """Simple Asterisk Manager Interface client"""

    def __init__(self, host: str, port: int = 5038, username: str = "admin",
                 secret: str = "asterisk123"):
        self.host = host
        self.port = port
        self.username = username
        self.secret = secret
        self.sock = None
        self.action_id = 0

    def connect(self) -> bool:
        """Connect to AMI"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10)
            self.sock.connect((self.host, self.port))

            # Read banner
            banner = self._read_response()
            print(f"Connected: {banner.get('banner', 'Unknown')}")

            # Login
            response = self._send_action({
                "Action": "Login",
                "Username": self.username,
                "Secret": self.secret
            })

            if response.get("Response") == "Success":
                print("AMI Login successful")
                return True
            else:
                print(f"AMI Login failed: {response.get('Message', 'Unknown error')}")
                return False

        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from AMI"""
        if self.sock:
            try:
                self._send_action({"Action": "Logoff"})
            except:
                pass
            self.sock.close()
            self.sock = None

    def _send_action(self, action: dict) -> dict:
        """Send an AMI action and get response"""
        self.action_id += 1
        action["ActionID"] = str(self.action_id)

        # Build message
        msg = ""
        for key, value in action.items():
            msg += f"{key}: {value}\r\n"
        msg += "\r\n"

        self.sock.sendall(msg.encode())
        return self._read_response()

    def _read_response(self) -> dict:
        """Read AMI response"""
        response = {}
        buffer = ""

        while True:
            data = self.sock.recv(4096).decode()
            if not data:
                break
            buffer += data

            # Check for end of message (double CRLF)
            if "\r\n\r\n" in buffer:
                break

        # Parse response
        for line in buffer.split("\r\n"):
            if ": " in line:
                key, value = line.split(": ", 1)
                response[key] = value
            elif line.startswith("Asterisk"):
                response["banner"] = line

        return response

    def send_sms(self, number: str, message: str, device: str = "dongle0") -> bool:
        """Send SMS via dongle"""
        print(f"Sending SMS to {number}: {message}")

        response = self._send_action({
            "Action": "DongleSendSMS",
            "Device": device,
            "Number": number,
            "Message": message
        })

        if response.get("Response") == "Success":
            print(f"SMS queued successfully")
            return True
        else:
            print(f"SMS failed: {response.get('Message', 'Unknown error')}")
            return False

    def originate_call(self, number: str, device: str = "dongle0",
                       timeout: int = 30000) -> bool:
        """Originate a call via dongle"""
        print(f"Calling {number} via {device}...")

        # Format number
        if not number.startswith("+"):
            if number.startswith("1") and len(number) == 11:
                pass  # Already has country code
            elif len(number) == 10:
                number = "1" + number
        else:
            number = number[1:]  # Remove +

        response = self._send_action({
            "Action": "Originate",
            "Channel": f"Dongle/{device}/{number}",
            "Context": "from-dongle",
            "Exten": "s",
            "Priority": "1",
            "Timeout": str(timeout),
            "CallerID": f"Gateway <7203454122>",
            "Async": "true"
        })

        if response.get("Response") == "Success":
            print(f"Call originated successfully")
            return True
        else:
            print(f"Call failed: {response.get('Message', 'Unknown error')}")
            return False

    def get_dongle_status(self, device: str = "dongle0") -> dict:
        """Get dongle device status"""
        response = self._send_action({
            "Action": "DongleShowDevices"
        })
        print(f"Dongle status response: {response}")
        return response

    def execute_command(self, command: str) -> str:
        """Execute Asterisk CLI command"""
        response = self._send_action({
            "Action": "Command",
            "Command": command
        })
        return response.get("Output", response.get("Message", "No output"))


def send_sms_direct(host: str, number: str, message: str):
    """Send SMS using docker exec (fallback method)"""
    import subprocess

    cmd = f'docker exec asterisk-sim7600 asterisk -rx \'dongle sms dongle0 {number} "{message}"\''
    print(f"Executing: ssh root@{host} \"{cmd}\"")

    result = subprocess.run(
        ["sshpass", "-p", "Cooldham21", "ssh", "-o", "StrictHostKeyChecking=no",
         f"root@{host}", cmd],
        capture_output=True, text=True
    )

    print(f"Output: {result.stdout}")
    if result.stderr:
        print(f"Error: {result.stderr}")

    return result.returncode == 0


def call_direct(host: str, number: str):
    """Originate call using docker exec (fallback method)"""
    import subprocess

    # Format number
    if number.startswith("+"):
        number = number[1:]

    cmd = f'docker exec asterisk-sim7600 asterisk -rx \'channel originate Dongle/dongle0/{number} application Playback hello-world\''
    print(f"Executing: ssh root@{host} \"{cmd}\"")

    result = subprocess.run(
        ["sshpass", "-p", "Cooldham21", "ssh", "-o", "StrictHostKeyChecking=no",
         f"root@{host}", cmd],
        capture_output=True, text=True
    )

    print(f"Output: {result.stdout}")
    if result.stderr:
        print(f"Error: {result.stderr}")

    return result.returncode == 0


def check_status_direct(host: str):
    """Check dongle status using docker exec"""
    import subprocess

    cmd = 'docker exec asterisk-sim7600 asterisk -rx "dongle show devices"'

    result = subprocess.run(
        ["sshpass", "-p", "Cooldham21", "ssh", "-o", "StrictHostKeyChecking=no",
         f"root@{host}", cmd],
        capture_output=True, text=True
    )

    print("Dongle Status:")
    print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")

    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Test Asterisk GSM Gateway")
    parser.add_argument("--host", default="100.122.93.142",
                        help="Asterisk host (default: 100.122.93.142)")
    parser.add_argument("--ami-port", type=int, default=5038,
                        help="AMI port (default: 5038)")
    parser.add_argument("--ami-user", default="admin",
                        help="AMI username (default: admin)")
    parser.add_argument("--ami-pass", default="asterisk123",
                        help="AMI password (default: asterisk123)")
    parser.add_argument("--sms", nargs=2, metavar=("NUMBER", "MESSAGE"),
                        help="Send SMS to NUMBER with MESSAGE")
    parser.add_argument("--call", metavar="NUMBER",
                        help="Call NUMBER via dongle")
    parser.add_argument("--status", action="store_true",
                        help="Show dongle status")
    parser.add_argument("--direct", action="store_true",
                        help="Use direct SSH/docker exec instead of AMI")

    args = parser.parse_args()

    if not (args.sms or args.call or args.status):
        parser.print_help()
        print("\nExamples:")
        print(f"  {sys.argv[0]} --status")
        print(f"  {sys.argv[0]} --sms +17208828227 'Hello from gateway'")
        print(f"  {sys.argv[0]} --call +17208828227")
        print(f"  {sys.argv[0]} --direct --sms +17208828227 'Test message'")
        sys.exit(1)

    # Use direct SSH method (more reliable)
    if args.direct or True:  # Always use direct for now
        if args.status:
            check_status_direct(args.host)

        if args.sms:
            number, message = args.sms
            send_sms_direct(args.host, number, message)

        if args.call:
            call_direct(args.host, args.call)
    else:
        # Use AMI
        ami = AsteriskAMI(args.host, args.ami_port, args.ami_user, args.ami_pass)

        if not ami.connect():
            print("Failed to connect to AMI")
            sys.exit(1)

        try:
            if args.status:
                ami.get_dongle_status()
                output = ami.execute_command("dongle show devices")
                print(output)

            if args.sms:
                number, message = args.sms
                ami.send_sms(number, message)

            if args.call:
                ami.originate_call(args.call)

        finally:
            ami.disconnect()


if __name__ == "__main__":
    main()
