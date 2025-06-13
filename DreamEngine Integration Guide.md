# DreamEngine Integration Guide

## Overview

DreamEngine is an enterprise-grade Python module that converts founder conversations into deployable code through a structured AI pipeline. This guide provides step-by-step instructions for integrating DreamEngine with your existing AI Debugger Factory.

## Prerequisites

- Existing AI Debugger Factory installation
- Python 3.8+ environment
- FastAPI backend
- Access to LLM APIs (OpenAI, Anthropic, and/or Google)

## One-Command Integration

Follow these steps to integrate DreamEngine with your AI Debugger Factory:

1. **Copy Files to Your Project**

   Copy the following files to your AI Debugger Factory project:

   ```
   app/models/dream_models.py → app/models/dream_models.py
   app/utils/dream_engine.py → app/utils/dream_engine.py
   static/js/dream_client.js → static/js/dream_client.js
   templates/dream_component.html → templates/dream_component.html
   ```

2. **Install Additional Dependencies**

   ```bash
   pip install -r requirements_additional.txt
   ```

3. **Configure Environment Variables**

   Add the following environment variables to your `.env` file:

   ```
   # OpenAI API credentials
   OPENAI_API_KEY=your_openai_api_key_here

   # Anthropic API credentials (optional)
   ANTHROPIC_API_KEY=your_anthropic_api_key_here

   # Google AI API credentials (optional)
   GOOGLE_API_KEY=your_google_api_key_here

   # DreamEngine configuration
   DREAMENGINE_DEFAULT_PROVIDER=auto
   DREAMENGINE_MAX_TOKENS=8192
   DREAMENGINE_TEMPERATURE=0.7
   DREAMENGINE_RATE_LIMIT=100
   DREAMENGINE_RATE_LIMIT_PERIOD=3600
   DREAMENGINE_LOG_LEVEL=INFO
   DREAMENGINE_SECURITY_SCAN_ENABLED=true
   ```

4. **Add Router to main.py**

   Add the following line to your `main.py` file:

   ```python
   from app.utils.dream_engine import router as dream_router
   app.include_router(dream_router)
   ```

5. **Include UI Component**

   Add the following line to your main template file (e.g., `index.html`):

   ```html
   {% include 'dream_component.html' %}
   ```

   And include the client JS in your HTML head or before the closing body tag:

   ```html
   <script src="{{ url_for('static', path='js/dream_client.js') }}"></script>
   ```

6. **Start Your Server**

   ```bash
   uvicorn main:app --reload
   ```

7. **Verify Installation**

   Test the integration with:

   ```bash
   curl -X POST http://localhost:8000/api/v1/dreamengine/health
   ```

   You should receive a response like:

   ```json
   {
     "status": "healthy",
     "service": "DreamEngine - AI Debugger Factory Extension",
     "providers": {
       "openai": true
     }
   }
   ```

## API Endpoints

DreamEngine provides the following endpoints:

### 1. Health Check

```
POST /api/v1/dreamengine/health
```

Returns the health status of the DreamEngine service and available LLM providers.

### 2. Process Dream

```
POST /api/v1/dreamengine/process
```

Generates code from a founder's natural language description.

**Request Body:**

```json
{
  "id": "string",
  "user_id": "string",
  "input_text": "Build a FastAPI CRUD app for task management",
  "options": {
    "model_provider": "openai",
    "project_type": "web_api",
    "programming_language": "python",
    "database_type": "postgresql",
    "security_level": "standard",
    "include_tests": true,
    "include_documentation": true,
    "include_docker": false,
    "include_ci_cd": false,
    "max_tokens": 8192,
    "temperature": 0.7
  }
}
```

### 3. Validate Idea

```
POST /api/v1/dreamengine/validate
```

Analyzes and validates a founder's idea before code generation.

**Request Body:** Same as `/process`

### 4. Stream Generation

```
POST /api/v1/dreamengine/stream
```

Streams code generation with real-time updates using Server-Sent Events (SSE).

**Request Body:** Same as `/process`

### 5. Cancel Generation

```
POST /api/v1/dreamengine/cancel
```

Cancels an ongoing streaming generation.

**Request Body:**

```json
{
  "request_id": "string",
  "user_id": "string"
}
```

## Frontend Integration

The DreamEngine frontend consists of:

1. **dream_client.js** - Client library for interacting with the DreamEngine API
2. **dream_component.html** - UI component for the DreamEngine interface

The UI component provides:

- Input field for founder's description
- Options configuration
- Generation controls
- Real-time progress updates
- Results display with syntax highlighting
- Deployment instructions

## Troubleshooting

### API Key Issues

If you see errors related to LLM providers:

1. Verify your API keys are correctly set in the environment variables
2. Check that the keys have sufficient permissions and quota
3. Ensure network connectivity to the LLM provider APIs

### Integration Issues

If the router is not working:

1. Verify the import path in main.py is correct
2. Check that all files are in the correct locations
3. Ensure FastAPI is correctly configured to include the router

### Frontend Issues

If the UI is not displaying or functioning correctly:

1. Check browser console for JavaScript errors
2. Verify that dream_client.js is being loaded
3. Ensure the template inclusion path is correct

## Security Considerations

DreamEngine includes:

- Input sanitization to prevent injection attacks
- Rate limiting to prevent abuse
- Code security scanning for generated output
- Proper error handling and logging

## Performance Optimization

For optimal performance:

1. Configure appropriate rate limits based on your usage patterns
2. Consider enabling caching for repeated requests
3. Monitor and adjust max_tokens based on your needs
4. Use streaming for large generations to improve user experience

## Support

For issues or questions, please contact the AI Debugger Factory support team.
