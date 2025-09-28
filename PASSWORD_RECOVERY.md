# Password Recovery System

## Overview
The AI Trade Report application now includes a complete password recovery system that allows users to reset their passwords when forgotten.

## Features
- **Forgot Password Page**: Users can request password reset by entering their email
- **Email Notifications**: Reset links are sent via email (configurable)
- **Secure Tokens**: Time-limited reset tokens (1 hour expiration)
- **Password Validation**: Ensures password strength and confirmation matching
- **Mobile Responsive**: Works on all device sizes

## How It Works

### 1. Forgot Password Request
- User visits `/forgot-password`
- Enters their email address
- System generates a secure reset token
- Reset link is sent to their email (or printed to console in development)

### 2. Password Reset
- User clicks the reset link in their email
- Redirected to `/reset-password?token=...`
- Enters new password and confirmation
- Password is updated and token is invalidated

## Email Configuration

### Development Mode
If email is not configured, reset links will be printed to the console:
```
🔐 PASSWORD RESET LINK FOR user@example.com:
   http://127.0.0.1:8000/reset-password?token=abc123...
   (Email service not configured - this is for development only)
```

### Production Mode
Add these environment variables to your `.env` file:

```env
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
FROM_EMAIL=noreply@aitradereport.com
FROM_NAME=AI Trade Report
```

### Gmail Setup
1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the App Password (not your regular password) in `SMTP_PASSWORD`

## Security Features
- **Token Expiration**: Reset tokens expire after 1 hour
- **One-Time Use**: Tokens are invalidated after successful password reset
- **Secure Generation**: Uses `secrets.token_urlsafe(32)` for cryptographically secure tokens
- **Email Privacy**: Doesn't reveal if email exists or not
- **Password Validation**: Enforces bcrypt's 72-byte limit and strength requirements

## Database Changes
The User model has been updated with new fields:
- `reset_token`: Stores the reset token
- `reset_token_expires`: Token expiration timestamp

## Routes Added
- `GET /forgot-password` - Display forgot password form
- `POST /forgot-password` - Process forgot password request
- `GET /reset-password` - Display reset password form (requires token)
- `POST /reset-password` - Process password reset

## UI Integration
- Added "Forgot your password?" link on login page
- Professional, responsive design matching the app's style
- Loading states and user feedback
- Password strength indicator

## Testing
1. Visit `/forgot-password`
2. Enter a registered email address
3. Check console for reset link (development mode)
4. Click the reset link
5. Enter new password and confirm
6. Login with new password

## Troubleshooting
- **Email not sending**: Check SMTP configuration in `.env`
- **Token expired**: Request a new password reset
- **Invalid token**: Ensure you're using the latest reset link
- **Database errors**: Run the app to create new database columns automatically
