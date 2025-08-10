# Railway Deployment Guide

This guide will help you deploy your Art Explorer app to Railway and configure it with your custom domain.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Custom Domain**: You should have a domain name ready

## Step 1: Connect to Railway

1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your Art Explorer repository
4. Choose "Deploy Now"

## Step 2: Configure Backend Service

1. **Service Setup**:
   - Railway will automatically detect the `railway.json` configuration
   - The backend will use the `docker/Dockerfile.backend` for building
   - Service will be named something like `art-explorer-backend`

2. **Environment Variables**:
   Add these environment variables in Railway:
   ```
   DATABASE_URL=your_postgresql_connection_string
   SECRET_KEY=your_secret_key_here
   ENVIRONMENT=production
   CORS_ORIGINS=https://myassemblage.art,https://www.myassemblage.art
   ```

3. **Database Setup**:
   - Add a PostgreSQL service in Railway
   - Copy the connection string to `DATABASE_URL`
   - The app will automatically create tables on first run

4. **Get Your Backend URL**:
   - After deployment, note your backend service URL
   - It will look like: `https://your-service-name.railway.app`
   - This is your API base URL for the frontend

## Step 3: Configure Frontend Service

1. **Create New Service**:
   - In your Railway project, click "New Service" → "GitHub Repo"
   - Select the same repository
   - Set the root directory to `frontend/`

2. **Environment Variables**:
   Add these environment variables:
   ```
   VITE_API_BASE_URL=https://your-backend-service-url.railway.app
   NODE_ENV=production
   ```
   
   **Important**: Replace `your-backend-service-url.railway.app` with the actual URL from your backend service deployment.

3. **Build Configuration**:
   - Railway will use the `railway-frontend.json` configuration
   - The service will build and serve the Vue.js frontend

## Step 4: Custom Domain Configuration

1. **Add Custom Domain**:
   - In your Railway project, go to "Settings" → "Domains"
   - Click "Add Domain"
   - Enter your domain (e.g., `myassemblage.art`)

2. **DNS Configuration**:
   Railway will provide DNS records. Add these to your domain registrar:
   ```
   Type: CNAME
   Name: @
   Value: your-railway-app.railway.app
   ```

3. **SSL Certificate**:
   - Railway automatically provides SSL certificates
   - Wait for DNS propagation (can take up to 48 hours)

## Step 5: Update Frontend Configuration

1. **Production API URL**:
   Update the frontend environment variable:
   ```
   VITE_API_BASE_URL=https://api.myassemblage.art
   ```

2. **CORS Configuration**:
   The backend is already configured to handle CORS for your domain.

## Step 6: Deploy and Test

1. **Deploy Backend**:
   - Push changes to GitHub
   - Railway will automatically redeploy

2. **Deploy Frontend**:
   - Push changes to GitHub
   - Railway will automatically redeploy

3. **Test Your App**:
   - Visit your custom domain
   - Test all functionality
   - Check API endpoints

## Environment Variables Reference

### Backend Service
```
DATABASE_URL=postgresql://username:password@host:port/database
SECRET_KEY=your_32_character_secret_key
ENVIRONMENT=production
CORS_ORIGINS=https://myassemblage.art,https://www.myassemblage.art
```

### Frontend Service
```
VITE_API_BASE_URL=https://api.myassemblage.art
NODE_ENV=production
```

## Troubleshooting

1. **Build Failures**:
   - Check Railway logs for build errors
   - Ensure all dependencies are in requirements.txt/package.json

2. **Database Connection**:
   - Verify DATABASE_URL is correct
   - Check if database service is running

3. **CORS Issues**:
   - Verify CORS_ORIGINS includes your domain
   - Check browser console for CORS errors

4. **Domain Issues**:
   - Wait for DNS propagation
   - Verify DNS records are correct
   - Check SSL certificate status

## Monitoring and Maintenance

1. **Railway Dashboard**:
   - Monitor service health
   - Check resource usage
   - View deployment logs

2. **Custom Domain Health**:
   - Railway provides domain health monitoring
   - Set up alerts for downtime

3. **Database Backups**:
   - Railway PostgreSQL includes automatic backups
   - Consider setting up additional backup strategies

## Cost Optimization

1. **Service Scaling**:
   - Start with minimal resources
   - Scale up based on usage

2. **Database Optimization**:
   - Use connection pooling
   - Monitor query performance

3. **CDN Integration**:
   - Consider adding a CDN for static assets
   - Railway provides edge caching

## Support

- **Railway Documentation**: [docs.railway.app](https://docs.railway.app)
- **Community**: [discord.gg/railway](https://discord.gg/railway)
- **GitHub Issues**: Use your repository's issue tracker
