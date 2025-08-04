# 🚀 Quick Deploy Guide

## Deploy in 10 Minutes

### Step 1: Prepare Your Repository
```bash
# Make sure you're in the project directory
cd "Art App"

# Initialize git if not already done
git init
git add .
git commit -m "Initial commit"

# Create GitHub repository and push
# (Do this on GitHub.com first, then:)
git remote add origin https://github.com/yourusername/art-app.git
git push -u origin main
```

### Step 2: Deploy Backend (Railway)
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add PostgreSQL service:
   - Click "New" → "Database" → "PostgreSQL"
6. Set environment variables:
   - `SECRET_KEY`: Generate a random string (32+ characters)
   - `CORS_ORIGINS`: Leave empty for now (we'll update after frontend)
7. Copy your Railway URL (e.g., `https://art-app-backend.railway.app`)

### Step 3: Deploy Frontend (Vercel)
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click "New Project" → Import your repository
4. Configure build settings:
   - Framework Preset: `Vite`
   - Root Directory: `./` (leave default)
   - Build Command: `cd frontend && npm run build`
   - Output Directory: `frontend/dist`
5. Add environment variable:
   - Name: `VITE_API_URL`
   - Value: Your Railway URL from Step 2
6. Deploy!

### Step 4: Update CORS
1. Go back to Railway dashboard
2. Add environment variable:
   - Name: `CORS_ORIGINS`
   - Value: Your Vercel URL (e.g., `https://art-app.vercel.app`)

### Step 5: Test Your App
1. Visit your Vercel URL
2. Register a new user
3. Try liking some artworks
4. Check the gallery

## Troubleshooting

### Common Issues:
- **CORS Error**: Make sure `CORS_ORIGINS` includes your Vercel URL
- **Database Error**: Check Railway logs for connection issues
- **Build Error**: Verify Node.js version in Vercel (should be 18+)

### Quick Fixes:
```bash
# If you need to update environment variables
# Vercel: Go to Project Settings → Environment Variables
# Railway: Go to Variables tab
```

## Cost
- **Vercel**: Free (100GB/month)
- **Railway**: Free ($5 credit/month)
- **Total**: $0/month for testing

## Share Your App
Once deployed, share your Vercel URL with users:
```
https://your-app-name.vercel.app
```

## Monitor Usage
- **Vercel**: Check Analytics tab
- **Railway**: Check Usage tab
- **Database**: Check Railway PostgreSQL logs

## Scale Up (If Needed)
- **Vercel Pro**: $20/month (unlimited bandwidth)
- **Railway**: Pay-as-you-use
- **Custom Domain**: Add in Vercel/Netlify settings 