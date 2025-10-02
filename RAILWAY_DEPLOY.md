# Railway Deployment Instructions

## Quick Deploy to Railway

### Step 1: Prepare Your Repository
Your project is already Railway-ready! I've added:
- ✅ `Procfile` (Railway auto-detects this)
- ✅ `requirements.txt` (Railway installs dependencies)
- ✅ `railway.json` (Optional configuration)

### Step 2: Deploy to Railway

#### Option A: GitHub Integration (Recommended)
1. **Push your code to GitHub** (if not already there):
   ```bash
   git init
   git add .
   git commit -m "Initial commit - VnExpress News API"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

2. **Deploy on Railway**:
   - Go to [railway.app](https://railway.app)
   - Click "Login with GitHub"
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Click "Deploy Now"

#### Option B: Railway CLI (Advanced)
1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and deploy**:
   ```bash
   railway login
   railway init
   railway up
   ```

### Step 3: Configure Environment (Optional)
In Railway dashboard:
- Go to your project
- Click "Variables" tab
- Add any environment variables if needed

### Step 4: Get Your Live URL
- Railway automatically provides a URL like: `https://your-app-name.up.railway.app`
- Test your API: `https://your-app-name.up.railway.app/docs`

## Expected Results
- ✅ API deployed in ~2-3 minutes
- ✅ HTTPS enabled automatically
- ✅ Custom domain available
- ✅ Auto-redeploy on git push
- ✅ Built-in monitoring

## Cost Estimation
- **Free tier**: 500 hours/month (plenty for testing)
- **Paid**: ~$5-10/month for production use
- **Database**: +$5/month for PostgreSQL (if needed)

## Troubleshooting
If deployment fails:
1. Check Railway logs in dashboard
2. Ensure all dependencies are in `requirements.txt`
3. Verify `Procfile` syntax
4. Check for any hard-coded localhost references

## Alternative Quick Deploy Commands

### For Render:
```bash
# Build command: pip install -r requirements.txt
# Start command: gunicorn -c gunicorn.conf.py main:app
```

### For DigitalOcean App Platform:
```bash
# Run command: gunicorn -c gunicorn.conf.py main:app
# HTTP port: 8000
```