#!/usr/bin/env python3
"""
Test Email Script for Hosted Environment
This script tests SMTP connection on the hosted server to debug email issues.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_smtp_connection():
    """Test SMTP connection with detailed debugging"""
    
    print("🔧 HOSTED EMAIL SMTP TEST")
    print("=" * 50)
    
    # Get environment variables
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("FROM_EMAIL", "noreply@aitradereport.com")
    from_name = os.getenv("FROM_NAME", "AI Trade Report")
    
    # Test email
    test_email = "tkani1337@gmail.com"
    
    print(f"📧 SMTP Configuration:")
    print(f"   Server: {smtp_server}")
    print(f"   Port: {smtp_port}")
    print(f"   Username: {smtp_username}")
    print(f"   From Email: {from_email}")
    print(f"   From Name: {from_name}")
    print(f"   Test Email: {test_email}")
    print()
    
    # Check if credentials are available
    if not smtp_username or not smtp_password:
        print("❌ ERROR: SMTP credentials not found in environment variables")
        print("   Make sure SMTP_USERNAME and SMTP_PASSWORD are set in Render dashboard")
        return False
    
    # Create test message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Test Email - AI Trade Report Hosted Server"
    msg['From'] = f"{from_name} <{from_email}>"
    msg['To'] = test_email
    
    # Create test content
    text_content = f"""This is a test email from your AI Trade Report hosted server.

If you receive this email, the SMTP configuration is working correctly!

Server Details:
- SMTP Server: {smtp_server}
- Port: {smtp_port}
- Username: {smtp_username}

Best regards,
AI Trade Report System
"""
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Test Email - AI Trade Report</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1>🧪 Test Email - AI Trade Report</h1>
        </div>
        <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px;">
            <h2>✅ SMTP Configuration Working!</h2>
            <p>This is a test email from your AI Trade Report hosted server.</p>
            <p>If you receive this email, the SMTP configuration is working correctly!</p>
            
            <div style="background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3>Server Details:</h3>
                <ul>
                    <li><strong>SMTP Server:</strong> {smtp_server}</li>
                    <li><strong>Port:</strong> {smtp_port}</li>
                    <li><strong>Username:</strong> {smtp_username}</li>
                </ul>
            </div>
            
            <p>Best regards,<br>AI Trade Report System</p>
        </div>
    </div>
</body>
</html>"""
    
    # Attach content
    text_part = MIMEText(text_content, 'plain')
    html_part = MIMEText(html_content, 'html')
    
    msg.attach(text_part)
    msg.attach(html_part)
    
    # Test SMTP connection
    print("🔧 Testing SMTP Connection...")
    
    try:
        print(f"   Connecting to {smtp_server}:{smtp_port}...")
        
        # Try SMTP_SSL first (port 465)
        if smtp_port == 465:
            print("   Using SMTP_SSL (port 465)...")
            with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30) as server:
                print("   ✅ SMTP_SSL connection established")
                
                print("   Attempting login...")
                server.login(smtp_username, smtp_password)
                print("   ✅ SMTP login successful")
                
                print("   Sending test email...")
                server.send_message(msg, smtp_username, [test_email])
                print("   ✅ Test email sent successfully")
                
        # Try SMTP with STARTTLS (port 587)
        elif smtp_port == 587:
            print("   Using SMTP with STARTTLS (port 587)...")
            with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
                print("   ✅ SMTP connection established")
                
                print("   Starting TLS...")
                server.starttls()
                print("   ✅ TLS started")
                
                print("   Attempting login...")
                server.login(smtp_username, smtp_password)
                print("   ✅ SMTP login successful")
                
                print("   Sending test email...")
                server.send_message(msg, smtp_username, [test_email])
                print("   ✅ Test email sent successfully")
        
        else:
            print(f"   ❌ Unsupported port: {smtp_port}")
            print("   Supported ports: 465 (SSL) or 587 (TLS)")
            return False
        
        print()
        print("🎉 SUCCESS: Test email sent successfully!")
        print(f"   Check {test_email} for the test email")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"   ❌ SMTP Authentication failed: {e}")
        print("   💡 Check your Gmail App Password")
        return False
        
    except smtplib.SMTPException as e:
        print(f"   ❌ SMTP error: {e}")
        print("   💡 Check your SMTP server and port settings")
        return False
        
    except ConnectionRefusedError as e:
        print(f"   ❌ Connection refused: {e}")
        print("   💡 Check if SMTP port is blocked by hosting provider")
        return False
        
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        print("   💡 Check your environment variables and network connection")
        return False

def test_environment_variables():
    """Test if all required environment variables are set"""
    
    print("🔧 ENVIRONMENT VARIABLES TEST")
    print("=" * 50)
    
    required_vars = [
        "SMTP_SERVER",
        "SMTP_PORT", 
        "SMTP_USERNAME",
        "SMTP_PASSWORD",
        "FROM_EMAIL",
        "FROM_NAME"
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask password for security
            if "PASSWORD" in var:
                masked_value = "*" * len(value)
            else:
                masked_value = value
            print(f"   ✅ {var}: {masked_value}")
        else:
            print(f"   ❌ {var}: Not set")
            missing_vars.append(var)
    
    print()
    
    if missing_vars:
        print("❌ MISSING ENVIRONMENT VARIABLES:")
        for var in missing_vars:
            print(f"   - {var}")
        print()
        print("💡 Add these to your Render dashboard → Environment tab")
        return False
    else:
        print("✅ All environment variables are set!")
        return True

if __name__ == "__main__":
    print("🧪 AI TRADE REPORT - HOSTED EMAIL TEST")
    print("=" * 60)
    print()
    
    # Test environment variables first
    env_ok = test_environment_variables()
    print()
    
    if env_ok:
        # Test SMTP connection
        smtp_ok = test_smtp_connection()
        print()
        
        if smtp_ok:
            print("🎉 ALL TESTS PASSED!")
            print("   Your email service should work on the hosted server.")
        else:
            print("❌ SMTP TEST FAILED!")
            print("   Check the error messages above for troubleshooting.")
    else:
        print("❌ ENVIRONMENT VARIABLES MISSING!")
        print("   Set up environment variables in Render dashboard first.")
    
    print()
    print("=" * 60)
