"""
# 🚀 AI DEBUGGER FACTORY - QUICK START GUIDE
*Get up and running in 5 minutes*

## 🎯 Prerequisites Checklist
- [ ] Python 3.11+ installed
- [ ] PostgreSQL running (or Docker)
- [ ] OpenAI API key (required)
- [ ] GitHub personal access token (required)

## ⚡ Quick Start (Docker - Recommended)

### 1. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
```

### 2. Start All Services
```bash
# Start everything
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app
```

### 3. Access Application
- **Main App**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🛠️ Manual Setup (Development)

### 1. Install Dependencies
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Start PostgreSQL
sudo service postgresql start

# Create database
createdb dreamengine_db

# Run migrations
python -c "
from app.database.db import DatabaseManager
import asyncio
db = DatabaseManager()
asyncio.run(db.run_migrations())
"
```

### 3. Run Application
```bash
# Start server
python run.py

# Or with uvicorn directly
uvicorn main:app --reload
```

## 🔑 Required API Keys

### OpenAI (Required)
1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Add to .env: `OPENAI_API_KEY=sk-your-key`

### GitHub (Required)
1. Go to https://github.com/settings/tokens
2. Generate new token with `repo` scope
3. Add to .env: `GITHUB_TOKEN=ghp_your-token`

### Optional Keys
- **Anthropic**: `ANTHROPIC_API_KEY=your-key`
- **ElevenLabs**: `ELEVENLABS_API_KEY=your-key`

## 🧪 Test Installation

### 1. Health Check
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy", ...}
```

### 2. Test VoiceBotics
1. Visit http://localhost:8000
2. Click "Start AI Cofounder Conversation"
3. Type or speak a business idea
4. Verify AI responds intelligently

### 3. Test Code Generation
1. Go to "Layer 1 Build"
2. Describe an app to build
3. Click "Generate Production Code"
4. Verify files are generated

## 🎯 Next Steps

1. **Create First Project**: Test the complete founder journey
2. **GitHub Integration**: Connect your repositories
3. **Voice Testing**: Try voice conversations
4. **Business Validation**: Test strategy analysis
5. **Deploy**: Use deployment guide for production

## 🆘 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL status
sudo service postgresql status

# Reset database
dropdb dreamengine_db
createdb dreamengine_db
python -c "from app.database.db import DatabaseManager; import asyncio; db = DatabaseManager(); asyncio.run(db.run_migrations())"
```

### API Key Issues
```bash
# Test OpenAI connection
python -c "
import openai
openai.api_key = 'your-key'
print(openai.Model.list())
"
```

### Port Already in Use
```bash
# Kill process on port 8000
sudo lsof -ti:8000 | xargs sudo kill -9
```

## 📖 Full Documentation
- **Deployment Guide**: `deployment_guide.md`
- **API Documentation**: http://localhost:8000/docs
- **Features Overview**: http://localhost:8000/features

🎉 **Welcome to the future of AI-powered development!**