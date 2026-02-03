#!/usr/bin/env python3
"""
Instagram Session Generator (with 2FA support)
Run this locally to login and generate a session string.
"""

import json
import base64
from instagrapi import Client
from instagrapi.exceptions import TwoFactorRequired

def main():
    print("=" * 50)
    print("Instagram Session Generator (2FA Supported)")
    print("=" * 50)
    
    username = input("\nEnter Instagram username: ").strip()
    password = input("Enter Instagram password: ").strip()
    
    cl = Client()
    cl.delay_range = [2, 5]
    
    print("\nLogging in...")
    
    try:
        cl.login(username, password)
        export_session(cl, username)
        
    except TwoFactorRequired as e:
        print("\n🔐 Two-Factor Authentication required!")
        verification_code = input("Enter 2FA code from your authenticator app: ").strip()
        
        try:
            cl.login(username, password, verification_code=verification_code)
            export_session(cl, username)
        except Exception as e2:
            print(f"❌ 2FA login failed: {e2}")
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Login failed: {error_msg}")
        
        if "blacklist" in error_msg.lower() or "ip" in error_msg.lower():
            print("\n🔧 Your IP might be blocked. Try:")
            print("  1. Use a VPN or mobile hotspot")
            print("  2. Wait a few hours and try again")
        elif "challenge" in error_msg.lower():
            print("\n🔧 Instagram needs verification:")
            print("  1. Open Instagram app on your phone")
            print("  2. Check for security alerts")

def export_session(cl, username):
    print("✅ Login successful!")
    
    settings = cl.get_settings()
    session_str = base64.b64encode(json.dumps(settings).encode()).decode()
    
    print("\n" + "=" * 50)
    print("🔐 YOUR SESSION STRING:")
    print("=" * 50)
    print(session_str)
    print("=" * 50)
    print("\n📋 Add to Railway as: INSTAGRAM_SESSION")
    
    # Save to file
    with open("instagram_session.txt", "w") as f:
        f.write(session_str)
    print("📁 Also saved to: instagram_session.txt")

if __name__ == "__main__":
    main()
