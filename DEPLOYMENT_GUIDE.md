# 🚀 FastAPI Deployment Guide - Free Options

This guide covers multiple free deployment options for your AI Trade Report FastAPI application.

## 📋 Prerequisites

- Your FastAPI application is ready
- GitHub repository is set up
- OpenAI API key is configured

## 🌐 Free Deployment Options

### 1. **Railway** (Recommended - Easiest)

#### Why Railway?
- ✅ **Free tier**: $5 credit monthly (enough for small apps)
- ✅ **Zero configuration**: Auto-detects FastAPI
- ✅ **Automatic deployments**: Deploys from GitHub
- ✅ **Custom domains**: Free subdomain + custom domain support
- ✅ **Environment variables**: Easy API key management

#### Steps:
1. **Sign up**: Go to [railway.app](https://railway.app)
2. **Connect GitHub**: Link your repository
3. **Deploy**: Click "Deploy" on your repo
4. **Add Environment Variables**:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
5. **Access**: Get your live URL (e.g., `https://your-app.railway.app`)

#### Railway Configuration:
Create `railway.json` in your project root:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100
  }
}
```

---

### 2. **Render** (Popular Choice)

#### Why Render?
- ✅ **Free tier**: 750 hours/month
- ✅ **Auto-deploy**: From GitHub
- ✅ **Custom domains**: Free subdomain
- ✅ **Easy setup**: Web interface

#### Steps:
1. **Sign up**: Go to [render.com](https://render.com)
2. **New Web Service**: Connect GitHub repo
3. **Configure**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables**:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
5. **Deploy**: Click "Create Web Service"

---

### 3. **Heroku** (Classic Choice)

#### Why Heroku?
- ✅ **Free tier**: 550-1000 dyno hours/month
- ✅ **Mature platform**: Well-established
- ✅ **Add-ons**: Many integrations

#### Steps:
1. **Install Heroku CLI**: [devcenter.heroku.com](https://devcenter.heroku.com)
2. **Login**: `heroku login`
3. **Create app**: `heroku create your-app-name`
4. **Set environment variables**:
   ```bash
   heroku config:set OPENAI_API_KEY=your_openai_api_key_here
   ```
5. **Deploy**: `git push heroku main`

#### Heroku Configuration:
Create `Procfile` in your project root:
```
web: uvicorn app:app --host 0.0.0.0 --port $PORT
```

---

### 4. **PythonAnywhere** (Python-Focused)

#### Why PythonAnywhere?
- ✅ **Free tier**: 1 web app, 512MB RAM
- ✅ **Python-optimized**: Built for Python apps
- ✅ **Easy setup**: Web-based configuration

#### Steps:
1. **Sign up**: Go to [pythonanywhere.com](https://pythonanywhere.com)
2. **Create Web App**: Choose "Manual configuration"
3. **Upload code**: Use GitHub or upload files
4. **Install dependencies**: In Bash console
5. **Configure WSGI**: Point to your FastAPI app
6. **Set environment variables**: In Web tab

---

### 5. **Fly.io** (Modern Platform)

#### Why Fly.io?
- ✅ **Free tier**: 3 shared-cpu VMs
- ✅ **Global deployment**: Edge locations
- ✅ **Docker-based**: Container deployment

#### Steps:
1. **Install Fly CLI**: [fly.io/docs/hands-on/install-flyctl](https://fly.io/docs/hands-on/install-flyctl)
2. **Login**: `fly auth login`
3. **Launch**: `fly launch` (creates `fly.toml`)
4. **Deploy**: `fly deploy`

#### Fly.io Configuration:
Create `fly.toml`:
```toml
app = "your-app-name"
primary_region = "ord"

[build]

[env]
  OPENAI_API_KEY = "your_openai_api_key_here"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
  processes = ["app"]

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

---

### 6. **Vercel** (Serverless)

#### Why Vercel?
- ✅ **Free tier**: 100GB bandwidth/month
- ✅ **Serverless**: Pay-per-use
- ✅ **Fast**: Global CDN

#### Steps:
1. **Install Vercel CLI**: `npm i -g vercel`
2. **Login**: `vercel login`
3. **Deploy**: `vercel`
4. **Configure**: Set environment variables in dashboard

#### Vercel Configuration:
Create `vercel.json`:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ],
  "env": {
    "OPENAI_API_KEY": "@openai_api_key"
  }
}
```

---

## 🔧 Production Optimizations

### 1. **Update requirements.txt**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
jinja2==3.1.2
python-multipart==0.0.6
openai==1.3.0
python-dotenv==1.0.0
gunicorn==21.2.0
```

### 2. **Add Gunicorn for Production**
Create `gunicorn.conf.py`:
```python
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
```

### 3. **Environment Variables**
Always set these in your deployment platform:
```env
OPENAI_API_KEY=your_actual_api_key
PYTHONPATH=/app
ENVIRONMENT=production
```

### 4. **Health Check Endpoint**
Add to your `app.py`:
```python
@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}
```

---

## 🚀 Quick Start (Railway - Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Railway**:
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "Deploy from GitHub repo"
   - Select your repository
   - Add environment variable: `OPENAI_API_KEY`
   - Deploy!

3. **Access your app**:
   - Get your live URL
   - Test: `https://your-app.railway.app`
   - API docs: `https://your-app.railway.app/docs`

---

## 🔍 Monitoring & Maintenance

### 1. **Check Logs**
- Railway: Dashboard → Logs
- Render: Dashboard → Logs
- Heroku: `heroku logs --tail`

### 2. **Monitor Performance**
- Check response times
- Monitor memory usage
- Watch for errors

### 3. **Update Deployment**
- Push changes to GitHub
- Platform auto-deploys
- Check logs for issues

---

## 🆘 Troubleshooting

### Common Issues:

1. **Port Issues**:
   ```python
   # Use environment variable for port
   port = int(os.getenv("PORT", 8000))
   ```

2. **Static Files**:
   ```python
   # Ensure static files are served
   app.mount("/static", StaticFiles(directory="static"), name="static")
   ```

3. **Environment Variables**:
   ```python
   # Load environment variables
   from dotenv import load_dotenv
   load_dotenv()
   ```

4. **CORS Issues**:
   ```python
   # Add CORS middleware
   from fastapi.middleware.cors import CORSMiddleware
   app.add_middleware(CORSMiddleware, allow_origins=["*"])
   ```

---

## 📊 Cost Comparison

| Platform | Free Tier | Pros | Cons |
|----------|-----------|------|------|
| **Railway** | $5 credit/month | Easy setup, auto-deploy | Credit-based |
| **Render** | 750 hours/month | Reliable, good docs | Limited hours |
| **Heroku** | 550-1000 hours/month | Mature, many add-ons | Sleeps after inactivity |
| **PythonAnywhere** | 1 app, 512MB RAM | Python-focused | Limited resources |
| **Fly.io** | 3 VMs | Global, fast | More complex setup |
| **Vercel** | 100GB bandwidth | Serverless, fast | Function limits |

---

## 🎯 Recommendation

**For your AI Trade Report app, I recommend Railway** because:
- ✅ Easiest setup
- ✅ Auto-deploys from GitHub
- ✅ Handles FastAPI perfectly
- ✅ Good free tier
- ✅ Easy environment variable management

Start with Railway, and you can always migrate to other platforms later!
