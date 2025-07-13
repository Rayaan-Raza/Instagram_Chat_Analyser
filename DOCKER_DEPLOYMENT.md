# 🐳 Docker Deployment Guide

This guide will help you deploy your Instagram Message Analyzer backend using Docker on various cloud platforms.

## 🎯 **Architecture**

- **Frontend**: Vercel (React + Vite)
- **Backend**: Docker container on cloud platform
- **Database**: In-memory sessions (can be upgraded to Redis/PostgreSQL)

## 🚀 **Quick Start**

### **1. Build Docker Image Locally**

```bash
# Navigate to backend directory
cd backend

# Build the Docker image
docker build -t instagram-analyzer-backend .

# Test locally
docker run -p 5000:5000 instagram-analyzer-backend
```

### **2. Test with Docker Compose**

```bash
# From project root
docker-compose up --build

# Test the API
curl http://localhost:5000/api/health
```

## ☁️ **Cloud Deployment Options**

### **Option 1: Google Cloud Run (Recommended)**

#### **Setup Google Cloud**
```bash
# Install Google Cloud CLI
# https://cloud.google.com/sdk/docs/install

# Initialize and authenticate
gcloud init
gcloud auth configure-docker
```

#### **Deploy to Cloud Run**
```bash
# Build and push to Google Container Registry
docker build -t gcr.io/YOUR_PROJECT_ID/instagram-analyzer-backend ./backend
docker push gcr.io/YOUR_PROJECT_ID/instagram-analyzer-backend

# Deploy to Cloud Run
gcloud run deploy instagram-analyzer-backend \
  --image gcr.io/YOUR_PROJECT_ID/instagram-analyzer-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10
```

### **Option 2: AWS ECS/Fargate**

#### **Create ECR Repository**
```bash
# Create ECR repository
aws ecr create-repository --repository-name instagram-analyzer-backend

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
```

#### **Build and Push**
```bash
# Build image
docker build -t instagram-analyzer-backend ./backend

# Tag for ECR
docker tag instagram-analyzer-backend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/instagram-analyzer-backend:latest

# Push to ECR
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/instagram-analyzer-backend:latest
```

#### **Deploy with ECS Task Definition**
```json
{
  "family": "instagram-analyzer-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::YOUR_ACCOUNT_ID:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/instagram-analyzer-backend:latest",
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "FLASK_ENV",
          "value": "production"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/instagram-analyzer-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### **Option 3: DigitalOcean App Platform**

#### **Deploy via DigitalOcean CLI**
```bash
# Install doctl
# https://docs.digitalocean.com/reference/doctl/how-to/install/

# Authenticate
doctl auth init

# Deploy app
doctl apps create --spec app.yaml
```

#### **Create app.yaml**
```yaml
name: instagram-analyzer-backend
services:
- name: backend
  source_dir: /backend
  dockerfile_path: /backend/Dockerfile
  http_port: 5000
  instance_count: 1
  instance_size_slug: basic-xxs
  routes:
  - path: /
  environment_slug: python
  envs:
  - key: FLASK_ENV
    value: production
```

### **Option 4: Azure Container Instances**

#### **Deploy to Azure**
```bash
# Login to Azure
az login

# Create resource group
az group create --name instagram-analyzer-rg --location eastus

# Create container registry
az acr create --resource-group instagram-analyzer-rg --name instagramanalyzeracr --sku Basic

# Build and push
az acr build --registry instagramanalyzeracr --image instagram-analyzer-backend ./backend

# Deploy container instance
az container create \
  --resource-group instagram-analyzer-rg \
  --name instagram-analyzer-backend \
  --image instagramanalyzeracr.azurecr.io/instagram-analyzer-backend:latest \
  --dns-name-label instagram-analyzer-backend \
  --ports 5000 \
  --memory 2 \
  --cpu 2
```

## 🔧 **Environment Configuration**

### **Required Environment Variables**
```bash
FLASK_ENV=production
FLASK_DEBUG=0
```

### **Optional Environment Variables**
```bash
# For session storage (if using Redis)
REDIS_URL=redis://localhost:6379

# For file storage (if using cloud storage)
UPLOAD_FOLDER=/app/uploads
MAX_CONTENT_LENGTH=52428800  # 50MB in bytes
```

## 📊 **Resource Requirements**

### **Minimum Requirements**
- **CPU**: 1 vCPU
- **Memory**: 1GB RAM
- **Storage**: 10GB
- **Network**: Standard

### **Recommended for Production**
- **CPU**: 2 vCPU
- **Memory**: 2GB RAM
- **Storage**: 20GB
- **Network**: Standard

## 🔒 **Security Considerations**

### **Docker Security**
- ✅ Non-root user in container
- ✅ Minimal base image (Python slim)
- ✅ No sensitive data in image
- ✅ Health checks enabled

### **Network Security**
- ✅ CORS configured for frontend domain
- ✅ HTTPS only in production
- ✅ Rate limiting (implement if needed)

## 📈 **Monitoring & Logging**

### **Health Check Endpoint**
```bash
curl https://your-backend-url/api/health
```

### **Expected Response**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000000"
}
```

### **Log Monitoring**
- Application logs via stdout/stderr
- Container logs via cloud platform
- Health check failures
- Memory usage monitoring

## 🔄 **Update Frontend Configuration**

After deploying your backend, update your Vercel environment variables:

1. **Go to Vercel Dashboard**
2. **Project Settings → Environment Variables**
3. **Update `VITE_API_URL`**:
   ```
   VITE_API_URL=https://your-backend-url
   ```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Container won't start**
   - Check logs: `docker logs <container_id>`
   - Verify port binding
   - Check environment variables

2. **Memory issues**
   - Increase memory allocation
   - Check for memory leaks
   - Monitor with `docker stats`

3. **Timeout errors**
   - Increase timeout settings
   - Check network connectivity
   - Verify health check endpoint

### **Debug Commands**
```bash
# Check container status
docker ps

# View logs
docker logs <container_id>

# Execute shell in container
docker exec -it <container_id> /bin/bash

# Check resource usage
docker stats <container_id>
```

## 💰 **Cost Comparison**

| Platform | Monthly Cost | Pros | Cons |
|----------|-------------|------|------|
| Google Cloud Run | $5-20 | Auto-scaling, pay-per-use | Cold starts |
| AWS ECS/Fargate | $10-30 | Fully managed, reliable | More complex setup |
| DigitalOcean App Platform | $5-15 | Simple, predictable | Limited regions |
| Azure Container Instances | $8-25 | Good integration | Less popular |

## 🎉 **Success Checklist**

- [ ] Docker image builds successfully
- [ ] Container runs locally
- [ ] Health check endpoint responds
- [ ] Deployed to cloud platform
- [ ] Frontend can connect to backend
- [ ] File uploads work
- [ ] Analysis completes successfully
- [ ] Monitoring and logging configured

Your backend is now ready for production deployment! 🚀 