# Art App Deployment Guide

## Quick Deployment Options

### Option 1: Vercel + Railway (Recommended)

#### Frontend (Vercel)
1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Deploy to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Sign up with GitHub
   - Import your repository
   - Set build settings:
     - Framework Preset: Vite
     - Build Command: `cd frontend && npm run build`
     - Output Directory: `frontend/dist`
   - Add environment variable: `VITE_API_URL=https://your-backend-url.railway.app`

#### Backend (Railway)
1. **Deploy to Railway**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Create new project
   - Add PostgreSQL service
   - Deploy from GitHub repository
   - Set environment variables:
     - `DATABASE_URL` (from PostgreSQL service)
     - `SECRET_KEY` (generate a random string)
     - `CORS_ORIGINS` (your Vercel frontend URL)

2. **Update Frontend API URL**
   - Copy your Railway backend URL
   - Update Vercel environment variable `VITE_API_URL`

### Option 2: Netlify + Fly.io

#### Frontend (Netlify)
1. **Deploy to Netlify**
   - Go to [netlify.com](https://netlify.com)
   - Connect GitHub repository
   - Set build settings:
     - Build command: `cd frontend && npm run build`
     - Publish directory: `frontend/dist`

#### Backend (Fly.io)
1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Deploy to Fly**
   ```bash
   fly launch
   fly postgres create
   fly secrets set DATABASE_URL="postgresql://..."
   fly deploy
   ```

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=https://your-frontend-url.vercel.app
```

### Frontend (Vercel/Netlify)
```env
VITE_API_URL=https://your-backend-url.railway.app
```

## Database Setup

### Railway PostgreSQL
- Automatically provided with Railway
- Connection string available in Railway dashboard

### Fly.io PostgreSQL
```bash
fly postgres create art-app-db
fly postgres attach art-app-db
```

## Testing Your Deployment

1. **Test Backend**
   ```bash
   curl https://your-backend-url.railway.app/health
   ```

2. **Test Frontend**
   - Visit your Vercel/Netlify URL
   - Try registering a user
   - Test liking artworks

## Troubleshooting

### Common Issues
1. **CORS Errors**: Check CORS_ORIGINS environment variable
2. **Database Connection**: Verify DATABASE_URL format
3. **Build Errors**: Check Node.js version in Vercel/Netlify

### Debugging
- Check Railway/Verel logs for backend errors
- Check browser console for frontend errors
- Verify environment variables are set correctly

## Cost Estimation

### Free Tiers
- **Vercel**: Free (100GB bandwidth/month)
- **Railway**: Free ($5 credit/month)
- **Netlify**: Free (100GB bandwidth/month)
- **Fly.io**: Free (3 shared-cpu-1x 256mb VMs)

### Paid Options (if needed)
- **Vercel Pro**: $20/month
- **Railway**: Pay-as-you-use
- **Netlify Pro**: $19/month
- **Fly.io**: Pay-as-you-use

## Next Steps

1. **Deploy to staging** first
2. **Test thoroughly** with a few users
3. **Monitor performance** and costs
4. **Scale up** if needed 