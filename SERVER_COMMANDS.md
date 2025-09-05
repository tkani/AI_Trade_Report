# Server Deployment Commands

Run these commands on your server `141.136.36.151` after SSH login.

## 🔐 SSH Connection

```bash
ssh root@141.136.36.151
# Password: Password
```

## 📋 Step-by-Step Commands

### 1. Navigate to the project directory

```bash
cd /var/www/AI_Trade_Report
```

### 2. Update system and install dependencies

```bash
apt update && apt upgrade -y
apt install -y nginx python3 python3-pip python3-venv certbot python3-certbot-nginx ufw
```

### 3. Set up Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn uvicorn[standard]
```

### 4. Configure environment

```bash
cp .env_example .env
echo "OPENAI_API_KEY=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" > .env
```

### 5. Create Nginx configuration

```bash
cat > /etc/nginx/sites-available/aitrade.ai-being.com << 'EOF'
server {
    listen 80;
    server_name aitrade.ai-being.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name aitrade.ai-being.com;

    ssl_certificate /etc/letsencrypt/live/aitrade.ai-being.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/aitrade.ai-being.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location /static/ {
        alias /var/www/AI_Trade_Report/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /reports/ {
        alias /var/www/AI_Trade_Report/reports/;
        expires 1h;
        add_header Cache-Control "public";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    client_max_body_size 10M;
}
EOF
```

### 6. Create systemd service

```bash
cat > /etc/systemd/system/ai-trade-report.service << 'EOF'
[Unit]
Description=AI Trade Report FastAPI Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/AI_Trade_Report
Environment="PATH=/var/www/AI_Trade_Report/venv/bin"
ExecStart=/var/www/AI_Trade_Report/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 127.0.0.1:8000 --access-logfile /var/log/ai-trade-report/access.log --error-logfile /var/log/ai-trade-report/error.log
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

### 7. Set up directories and permissions

```bash
mkdir -p /var/log/ai-trade-report
chown www-data:www-data /var/log/ai-trade-report
chown -R www-data:www-data /var/www/AI_Trade_Report
chmod -R 755 /var/www/AI_Trade_Report
chmod -R 777 /var/www/AI_Trade_Report/reports
```

### 8. Get SSL certificate

```bash
certbot certonly --webroot -w /var/www/html -d aitrade.ai-being.com --non-interactive --agree-tos --email support@aibeing.com
```

### 9. Start services

```bash
systemctl daemon-reload
systemctl enable ai-trade-report
systemctl start ai-trade-report
ln -sf /etc/nginx/sites-available/aitrade.ai-being.com /etc/nginx/sites-enabled/
nginx -t
systemctl start nginx
systemctl enable nginx
```

### 10. Configure firewall

```bash
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'
```

### 11. Check status

```bash
systemctl status ai-trade-report
systemctl status nginx
```

## 🎯 Quick One-Line Deployment

If you want to run everything at once, copy and paste this:

```bash
cd /var/www/AI_Trade_Report && apt update && apt install -y nginx python3 python3-pip python3-venv certbot python3-certbot-nginx ufw && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && pip install gunicorn uvicorn[standard] && cp .env_example .env && echo "OPENAI_API_KEY=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" > .env && cat > /etc/nginx/sites-available/aitrade.ai-being.com << 'EOF'
server {
    listen 80;
    server_name aitrade.ai-being.com;
    return 301 https://$server_name$request_uri;
}
server {
    listen 443 ssl http2;
    server_name aitrade.ai-being.com;
    ssl_certificate /etc/letsencrypt/live/aitrade.ai-being.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/aitrade.ai-being.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    location /static/ {
        alias /var/www/AI_Trade_Report/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    location /reports/ {
        alias /var/www/AI_Trade_Report/reports/;
        expires 1h;
        add_header Cache-Control "public";
    }
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    client_max_body_size 10M;
}
EOF
&& cat > /etc/systemd/system/ai-trade-report.service << 'EOF'
[Unit]
Description=AI Trade Report FastAPI Application
After=network.target
[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/AI_Trade_Report
Environment="PATH=/var/www/AI_Trade_Report/venv/bin"
ExecStart=/var/www/AI_Trade_Report/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 127.0.0.1:8000 --access-logfile /var/log/ai-trade-report/access.log --error-logfile /var/log/ai-trade-report/error.log
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
[Install]
WantedBy=multi-user.target
EOF
&& mkdir -p /var/log/ai-trade-report && chown www-data:www-data /var/log/ai-trade-report && chown -R www-data:www-data /var/www/AI_Trade_Report && chmod -R 755 /var/www/AI_Trade_Report && chmod -R 777 /var/www/AI_Trade_Report/reports && certbot certonly --webroot -w /var/www/html -d aitrade.ai-being.com --non-interactive --agree-tos --email support@aibeing.com && systemctl daemon-reload && systemctl enable ai-trade-report && systemctl start ai-trade-report && ln -sf /etc/nginx/sites-available/aitrade.ai-being.com /etc/nginx/sites-enabled/ && nginx -t && systemctl start nginx && systemctl enable nginx && ufw --force enable && ufw default deny incoming && ufw default allow outgoing && ufw allow ssh && ufw allow 'Nginx Full' && echo "✅ Deployment completed! Visit https://aitrade.ai-being.com"
```

## 🔍 Verification

After deployment, check:

1. **Service status**:

   ```bash
   systemctl status ai-trade-report
   systemctl status nginx
   ```

2. **Test the application**:

   ```bash
   curl http://localhost:8000
   curl https://aitrade.ai-being.com
   ```

3. **Check logs**:
   ```bash
   tail -f /var/log/ai-trade-report/error.log
   tail -f /var/log/nginx/error.log
   ```

## 🎉 Expected Result

- **Main domain**: Your existing Apache + Flask app (unchanged)
- **Subdomain**: `https://aitrade.ai-being.com` → FastAPI app (new)
- **API docs**: `https://aitrade.ai-being.com/docs`
