# 🚀 Deployment Guide

## Quick Deploy Options

### Option 1: Vercel + Railway (Recommended)

#### Frontend (Vercel)
1. **Push to GitHub**: Upload your code to a GitHub repository
2. **Connect to Vercel**: 
   - Go to [vercel.com](https://vercel.com)
   - Sign up with GitHub
   - Click "New Project"
   - Import your repository
   - Deploy!

#### Backend (Railway)
1. **Push to GitHub**: Make sure your backend code is in the repository
2. **Connect to Railway**:
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Set root directory to `backend`
   - Deploy!

### Option 2: Netlify + Render

#### Frontend (Netlify)
1. **Build locally**: `npm run build`
2. **Deploy to Netlify**:
   - Go to [netlify.com](https://netlify.com)
   - Drag and drop your `dist` folder
   - Or connect GitHub for auto-deploy

#### Backend (Render)
1. **Create Render account**: [render.com](https://render.com)
2. **New Web Service**:
   - Connect GitHub repo
   - Set root directory to `backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`

### Option 3: GitHub Pages + Heroku

#### Frontend (GitHub Pages)
1. **Add to package.json**:
   ```json
   "homepage": "https://yourusername.github.io/your-repo-name",
   "scripts": {
     "predeploy": "npm run build",
     "deploy": "gh-pages -d dist"
   }
   ```
2. **Deploy**: `npm run deploy`

#### Backend (Heroku)
1. **Install Heroku CLI**
2. **Create app**: `heroku create your-app-name`
3. **Deploy**: `git push heroku main`

## Environment Variables

### Frontend (.env)
```env
VITE_API_URL=https://your-backend-url.railway.app
```

### Backend (Railway/Render Environment)
```env
FLASK_ENV=production
```

## File Structure for Deployment

```
your-repo/
├── frontend/          # React app (deploy to Vercel/Netlify)
│   ├── package.json
│   ├── vite.config.js
│   ├── src/
│   └── vercel.json
├── backend/           # Flask API (deploy to Railway/Render)
│   ├── app.py
│   ├── requirements.txt
│   ├── Procfile
│   └── runtime.txt
└── README.md
```

## Troubleshooting

### Common Issues:
1. **CORS errors**: Make sure backend CORS is configured for your frontend domain
2. **Build failures**: Check that all dependencies are in requirements.txt
3. **Port issues**: Ensure backend uses `PORT` environment variable

### Debug Commands:
```bash
# Test backend locally
cd backend
python app.py

# Test frontend locally
npm run dev

# Build frontend
npm run build
```

## Cost Comparison

| Platform | Frontend | Backend | Monthly Cost |
|----------|----------|---------|--------------|
| Vercel + Railway | Free | Free | $0 |
| Netlify + Render | Free | Free | $0 |
| GitHub Pages + Heroku | Free | $7+ | $7+ |
| AWS | $1-5 | $5-20 | $6-25 |

## Security Considerations

1. **File upload limits**: Set appropriate file size limits
2. **Session management**: Use secure session storage in production
3. **CORS**: Configure CORS for your specific domains
4. **Environment variables**: Never commit secrets to Git

## Performance Optimization

1. **Frontend**: Enable gzip compression
2. **Backend**: Use caching for analysis results
3. **Database**: Consider adding Redis for session storage
4. **CDN**: Use CDN for static assets

## Monitoring

1. **Vercel**: Built-in analytics and performance monitoring
2. **Railway**: Logs and metrics dashboard
3. **Uptime**: Set up uptime monitoring with UptimeRobot
4. **Error tracking**: Add Sentry for error monitoring 