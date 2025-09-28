import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "465"))  # Use SSL port instead of TLS
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@aitradereport.com")
        self.from_name = os.getenv("FROM_NAME", "AI Trade Report")
    
    def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str):
        """Send password reset email - returns (success: bool, error_message: str)"""
        try:
            # Create reset link - use environment variable or default to hosted URL
            base_url = os.getenv("BASE_URL", "https://ai-trade-report.onrender.com")
            # Ensure no double slashes
            base_url = base_url.rstrip('/')
            reset_link = f"{base_url}/reset-password?token={reset_token}"
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Password Reset - AI Trade Report"
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Create HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Password Reset</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }}
                    .button {{ display: inline-block; background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white !important; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0; font-weight: bold; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2 style="margin: 0 0 15px 0; font-size: 24px; font-weight: bold;">AI Trade Report</h2>
                        <div style="margin-bottom: 15px;">
                            <img src="https://via.placeholder.com/40x40/4ade80/ffffff?text=AI" alt="AI Trade Report" style="height: 40px; width: 40px; margin-right: 10px; border-radius: 8px;">
                            <img src="https://via.placeholder.com/120x40/1e40af/ffffff?text=FEDERITALY" alt="FEDERITALY" style="height: 40px; width: 120px; border-radius: 8px;">
                        </div>
                        <h1>🔐 Password Reset Request</h1>
                    </div>
                    <div class="content">
                        <h2>Hello {user_name}!</h2>
                        <p>We received a request to reset your password for your AI Trade Report account.</p>
                        <p>Click the button below to reset your password:</p>
                        <a href="{reset_link}" class="button">Reset Password</a>
                        <p>If the button doesn't work, copy and paste this link into your browser:</p>
                        <p style="word-break: break-all; background: #e9ecef; padding: 10px; border-radius: 4px; font-family: monospace;">{reset_link}</p>
                        <p><strong>This link will expire in 1 hour for security reasons.</strong></p>
                        <p>If you didn't request this password reset, please ignore this email.</p>
                    </div>
                    <div class="footer">
                        <p>This email was sent by AI Trade Report</p>
                        <p>If you have any questions, please contact our support team.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create text content
            text_content = f"""
            Password Reset - AI Trade Report
            
            Hello {user_name}!
            
            We received a request to reset your password for your AI Trade Report account.
            
            To reset your password, click the following link:
            {reset_link}
            
            This link will expire in 1 hour for security reasons.
            
            If you didn't request this password reset, please ignore this email.
            
            Best regards,
            AI Trade Report Team
            """
            
            # Attach parts
            text_part = MIMEText(text_content, 'plain')
            html_part = MIMEText(html_content, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            if self.smtp_username and self.smtp_password:
                try:
                    print(f"🔧 SMTP Config: Server={self.smtp_server}, Port={self.smtp_port}, Username={self.smtp_username}")
                    print(f"🔧 Attempting SMTP_SSL connection...")
                    
                    # Use the same method that worked in the test
                    with smtplib.SMTP_SSL(self.smtp_server, 465, timeout=10) as server:
                        print(f"🔧 SMTP_SSL connection established")
                        server.login(self.smtp_username, self.smtp_password)
                        print(f"🔧 SMTP login successful")
                        server.send_message(msg, self.smtp_username, [to_email])
                        print(f"🔧 Email message sent")
                    
                    logger.info(f"Password reset email sent to {to_email}")
                    print(f"✅ Email sent successfully to {to_email}")
                    return True, None
                except smtplib.SMTPAuthenticationError as e:
                    error_msg = f"SMTP Authentication failed: {e}"
                    logger.error(error_msg)
                    print(f"❌ {error_msg}")
                    return False, error_msg
                except smtplib.SMTPException as e:
                    error_msg = f"SMTP connection error: {e}"
                    logger.error(error_msg)
                    print(f"❌ {error_msg}")
                    return False, error_msg
                except Exception as e:
                    error_msg = f"Email sending failed: {e}"
                    logger.error(error_msg)
                    print(f"❌ {error_msg}")
                    return False, error_msg
            
            # Fallback: Show reset link in console
            error_msg = "SMTP connection failed - email service not configured properly"
            logger.info(f"Password reset link for {to_email}: {reset_link}")
            print(f"\n🔐 PASSWORD RESET LINK FOR {to_email}:")
            print(f"   {reset_link}")
            print(f"   (SMTP connection failed - using console output)\n")
            return False, error_msg
                
        except Exception as e:
            error_msg = f"Failed to send password reset email: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

# Create global instance
email_service = EmailService()
