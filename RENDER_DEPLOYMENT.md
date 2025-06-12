# AI Debugger Factory - Render Deployment Guide

## Overview

This guide provides instructions for deploying the AI Debugger Factory to Render. The deployment package includes both the backend API and the frontend UI integrated into a single application.

## Prerequisites

- A Render account (https://render.com)
- Git repository to host your code (GitHub, GitLab, etc.)
- PostgreSQL database (can be provisioned on Render)

## Deployment Steps

### 1. Database Setup

1. Log in to your Render dashboard
2. Create a new PostgreSQL database:
   - Go to "New" > "PostgreSQL"
   - Name: `ai-debugger-factory-db`
   - User: Leave as default
   - Database: `ai_debugger_factory`
   - Select appropriate region and plan
   - Click "Create Database"
3. Once created, note the "Internal Database URL" for the next steps

### 2. Application Deployment

1. Push this codebase to your Git repository
2. Log in to your Render dashboard
3. Create a new Web Service:
   - Go to "New" > "Web Service"
   - Connect your repository
   - Name: `ai-debugger-factory`
   - Runtime: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Select appropriate plan
4. Add the following environment variables:
   - `DATABASE_URL`: Use the Internal Database URL from step 1
   - `ENVIRONMENT`: `production`
   - `SECRET_KEY`: Generate a secure random string
   - `DEBUG`: `False`
   - `LOG_LEVEL`: `INFO`
5. Click "Create Web Service"

### 3. Verify Deployment

1. Once deployed, Render will provide a URL for your application
2. Visit the URL to access the AI Debugger Factory UI
3. Test the following endpoints:
   - `/api/v1/health` - Should return status "healthy"
   - `/api/v1/debug/status` - Should return repository status
   - `/api/v1/build` - For generating code from prompts
   - `/api/v1/voice` - For processing voice input
   - `/api/v1/debug/contract-drift` - For checking contract drift

## Configuration

The application uses the following environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `ENVIRONMENT`: Set to "production" for deployment
- `DEBUG`: Set to "False" for production
- `LOG_LEVEL`: Logging level (INFO, DEBUG, ERROR)
- `SECRET_KEY`: Secret key for security features
- `ALLOWED_ORIGINS`: CORS allowed origins (default: *)

## Troubleshooting

- **Database Connection Issues**: Verify the DATABASE_URL is correct and the database is accessible from the web service
- **Application Errors**: Check the logs in the Render dashboard
- **Static Files Not Loading**: Ensure the static files are properly included in the deployment

## Scaling

To scale the application:
1. Go to your web service in the Render dashboard
2. Under "Settings", adjust the instance type or number of instances
3. For high traffic, consider adding a CDN for static assets

## Monitoring

Render provides built-in monitoring:
1. Go to your web service in the Render dashboard
2. Check the "Metrics" tab for CPU, memory, and request metrics
3. Set up alerts for critical metrics

## Support

For issues with the AI Debugger Factory, please refer to the documentation or contact support.

For Render-specific deployment issues, refer to the [Render documentation](https://render.com/docs).
