#!/usr/bin/env python3
"""
Simple SIP registration test client with qop support
"""
import socket
import hashlib
import random

def generate_call_id():
    return f"{random.randint(1000000, 9999999)}@testclient"

def generate_tag():
    return f"{random.randint(1000000, 9999999)}"

def generate_cnonce():
    return hashlib.md5(str(random.random()).encode()).hexdigest()[:16]

def calculate_md5_response(username, realm, password, method, uri, nonce, qop=None, nc=None, cnonce=None):
    """Calculate MD5 digest response for SIP authentication"""
    ha1 = hashlib.md5(f"{username}:{realm}:{password}".encode()).hexdigest()
    ha2 = hashlib.md5(f"{method}:{uri}".encode()).hexdigest()
    
    if qop:
        response = hashlib.md5(f"{ha1}:{nonce}:{nc}:{cnonce}:{qop}:{ha2}".encode()).hexdigest()
    else:
        response = hashlib.md5(f"{ha1}:{nonce}:{ha2}".encode()).hexdigest()
    
    return response

def send_register(server, port, username, password, display_name="Test Client"):
    """Send SIP REGISTER request"""
    
    call_id = generate_call_id()
    from_tag = generate_tag()
    cseq = 1
    
    # Initial REGISTER without auth
    register_msg = (
        f"REGISTER sip:{server} SIP/2.0\r\n"
        f"Via: SIP/2.0/UDP 127.0.0.1:5160;branch=z9hG4bK{random.randint(100000, 999999)}\r\n"
        f"From: \"{display_name}\" <sip:{username}@{server}>;tag={from_tag}\r\n"
        f"To: \"{display_name}\" <sip:{username}@{server}>\r\n"
        f"Call-ID: {call_id}\r\n"
        f"CSeq: {cseq} REGISTER\r\n"
        f"Contact: <sip:{username}@127.0.0.1:5160>\r\n"
        f"Max-Forwards: 70\r\n"
        f"Expires: 3600\r\n"
        f"User-Agent: Python SIP Test Client\r\n"
        f"Content-Length: 0\r\n"
        f"\r\n"
    )
    
    print("=" * 70)
    print("SENDING INITIAL REGISTER:")
    print("=" * 70)
    print(register_msg)
    
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    
    try:
        # Send initial REGISTER
        sock.sendto(register_msg.encode(), (server, port))
        
        # Receive response
        response, addr = sock.recvfrom(4096)
        response_str = response.decode('utf-8', errors='ignore')
        
        print("\n" + "=" * 70)
        print("RECEIVED RESPONSE:")
        print("=" * 70)
        print(response_str)
        
        # Parse 401 Unauthorized response
        if "401" in response_str or "407" in response_str:
            print("\n" + "=" * 70)
            print("AUTH CHALLENGE RECEIVED - Sending authenticated REGISTER")
            print("=" * 70)
            
            # Extract auth parameters
            realm = None
            nonce = None
            opaque = None
            qop = None
            
            for line in response_str.split('\r\n'):
                if 'WWW-Authenticate:' in line or 'Proxy-Authenticate:' in line:
                    if 'realm=' in line:
                        realm = line.split('realm="')[1].split('"')[0]
                    if 'nonce=' in line:
                        nonce = line.split('nonce="')[1].split('"')[0]
                    if 'opaque=' in line:
                        opaque = line.split('opaque="')[1].split('"')[0]
                    if 'qop=' in line:
                        qop_val = line.split('qop="')[1].split('"')[0]
                        qop = 'auth' if 'auth' in qop_val else None
            
            if realm and nonce:
                print(f"\nRealm: {realm}")
                print(f"Nonce: {nonce}")
                print(f"Opaque: {opaque}")
                print(f"QoP: {qop}")
                print(f"Username: {username}")
                print(f"Password: {password}")
                
                # Calculate response
                uri = f"sip:{server}"
                nc = "00000001"
                cnonce = generate_cnonce()
                
                print(f"NC: {nc}")
                print(f"CNonce: {cnonce}")
                
                auth_response = calculate_md5_response(username, realm, password, "REGISTER", uri, nonce, qop, nc, cnonce)
                
                print(f"\nCalculated MD5 Response: {auth_response}")
                
                # Build Authorization header
                auth_header = (
                    f'Authorization: Digest username="{username}", realm="{realm}", '
                    f'nonce="{nonce}", uri="{uri}", response="{auth_response}", algorithm=MD5'
                )
                
                if opaque:
                    auth_header += f', opaque="{opaque}"'
                if qop:
                    auth_header += f', qop={qop}, nc={nc}, cnonce="{cnonce}"'
                
                auth_header += "\r\n"
                
                # Send authenticated REGISTER
                cseq += 1
                auth_register_msg = (
                    f"REGISTER sip:{server} SIP/2.0\r\n"
                    f"Via: SIP/2.0/UDP 127.0.0.1:5160;branch=z9hG4bK{random.randint(100000, 999999)}\r\n"
                    f"From: \"{display_name}\" <sip:{username}@{server}>;tag={from_tag}\r\n"
                    f"To: \"{display_name}\" <sip:{username}@{server}>\r\n"
                    f"Call-ID: {call_id}\r\n"
                    f"CSeq: {cseq} REGISTER\r\n"
                    f"Contact: <sip:{username}@127.0.0.1:5160>\r\n"
                    f"{auth_header}"
                    f"Max-Forwards: 70\r\n"
                    f"Expires: 3600\r\n"
                    f"User-Agent: Python SIP Test Client\r\n"
                    f"Content-Length: 0\r\n"
                    f"\r\n"
                )
                
                print("\n" + "=" * 70)
                print("SENDING AUTHENTICATED REGISTER:")
                print("=" * 70)
                print(auth_register_msg)
                
                sock.sendto(auth_register_msg.encode(), (server, port))
                
                # Receive final response
                response2, addr2 = sock.recvfrom(4096)
                response2_str = response2.decode('utf-8', errors='ignore')
                
                print("\n" + "=" * 70)
                print("FINAL RESPONSE:")
                print("=" * 70)
                print(response2_str)
                
                if "200 OK" in response2_str:
                    print("\n✅ SUCCESS! Registration successful!")
                    return True
                else:
                    print("\n❌ FAILED! Registration failed!")
                    return False
            else:
                print("\n❌ ERROR: Could not extract realm or nonce from challenge")
                return False
        elif "200 OK" in response_str:
            print("\n✅ SUCCESS! Registration successful (no auth required)!")
            return True
        else:
            print(f"\n❌ UNEXPECTED RESPONSE!")
            return False
            
    except socket.timeout:
        print("\n❌ ERROR: Connection timeout - server not responding")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        sock.close()

if __name__ == "__main__":
    # Configuration
    SERVER = "YOUR_UNRAID_IP"
    PORT = 5160
    USERNAME = "100"
    PASSWORD = "CallMe2024!"
    
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║              SIP REGISTRATION TEST CLIENT                        ║
╚══════════════════════════════════════════════════════════════════╝

Server:   {SERVER}:{PORT}
Username: {USERNAME}
Password: {PASSWORD}

Testing SIP REGISTER...
""")
    
    result = send_register(SERVER, PORT, USERNAME, PASSWORD)
    
    if result:
        print("\n🎉 Test completed successfully!")
        exit(0)
    else:
        print("\n😞 Test failed - check configuration")
        exit(1)
