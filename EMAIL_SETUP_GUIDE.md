# 📧 Email Setup Guide for Password Recovery

## Current Status: Development Mode ✅
Your password recovery system is **working perfectly** but currently in development mode, which means:
- ✅ Reset links are generated and stored in database
- ✅ Users can reset their passwords
- 📝 Reset links are printed to console (not sent via email)

## 🚀 How to Enable Real Email Sending

### Option 1: Gmail Setup (Recommended)

1. **Create a `.env` file** in your project root with these settings:
```env
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
FROM_EMAIL=noreply@aitradereport.com
FROM_NAME=AI Trade Report
```

2. **Enable 2-Factor Authentication** on your Gmail account
3. **Generate App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Enter "AI Trade Report" as the name
   - Copy the generated 16-character password
   - Use this password in `SMTP_PASSWORD` (not your regular Gmail password)

4. **Restart your application** - emails will now be sent automatically!

### Option 2: Other Email Providers

#### Outlook/Hotmail
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your_email@outlook.com
SMTP_PASSWORD=your_password
```

#### Yahoo Mail
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=your_email@yahoo.com
SMTP_PASSWORD=your_app_password
```

#### Custom SMTP Server
```env
SMTP_SERVER=your_smtp_server.com
SMTP_PORT=587
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
```

## 🧪 Testing Email Functionality

### Test 1: Development Mode (Current)
1. Go to `http://127.0.0.1:8000/forgot-password`
2. Enter any email address
3. Check your server console - you'll see:
```
🔐 PASSWORD RESET LINK FOR user@example.com:
   http://127.0.0.1:8000/reset-password?token=abc123...
   (Email service not configured - this is for development only)
```

### Test 2: Production Mode (After Email Setup)
1. Configure your `.env` file with email settings
2. Restart the application
3. Go to `http://127.0.0.1:8000/forgot-password`
4. Enter a real email address
5. Check your email inbox for the reset link!

## 📧 Email Features

### Professional HTML Emails
- **Beautiful Design**: Matches your app's branding
- **Responsive**: Works on all devices
- **Secure Links**: Time-limited reset tokens
- **Clear Instructions**: Easy for users to follow

### Email Content Includes:
- Your app logo and branding
- Clear reset instructions
- Secure reset button
- Fallback text link
- Expiration notice (1 hour)
- Professional footer

## 🔒 Security Features

- **Time-Limited Tokens**: Expire after 1 hour
- **One-Time Use**: Tokens invalidated after successful reset
- **Secure Generation**: Cryptographically secure tokens
- **Email Privacy**: Doesn't reveal if email exists
- **HTTPS Links**: Secure reset URLs

## 🚨 Troubleshooting

### "Email not sending"
- Check your `.env` file has correct SMTP settings
- Verify your email credentials
- Ensure 2FA is enabled and app password is used (Gmail)

### "Invalid credentials"
- Use App Password, not regular password (Gmail)
- Check SMTP server and port settings
- Verify email address is correct

### "Connection refused"
- Check firewall settings
- Verify SMTP server and port
- Try different port (465 for SSL, 587 for TLS)

## 📊 Current Status

✅ **Database**: Password recovery columns added
✅ **Routes**: All endpoints working
✅ **UI**: Professional forgot/reset pages
✅ **Security**: Secure token generation
✅ **Development**: Console output working
🔄 **Production**: Ready for email configuration

## 🎯 Next Steps

1. **For Development**: Keep current setup (console output)
2. **For Production**: Add email configuration to `.env`
3. **For Testing**: Use the test email addresses
4. **For Users**: They'll receive beautiful HTML emails!

Your password recovery system is **100% functional** and ready for real email delivery! 🎉
