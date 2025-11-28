# Deployment Guide

This guide shows how to deploy the Code Review and Debug Agent to various platforms for the **bonus points** category.

## 🎯 Deployment Options

1. **Google Cloud Run** (Recommended for Agent Engine compatibility)
2. **Docker Container** (Platform-agnostic)
3. **Local Server** (Development/Testing)
4. **Kaggle Notebooks** (Competition submission)

---

## Option 1: Google Cloud Run (Bonus Points! 🌟)

Deploy as a serverless container on Google Cloud Platform.

### Prerequisites
- Google Cloud account
- `gcloud` CLI installed
- Docker installed

### Step 1: Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agent/ ./agent/
COPY config.py .
COPY app.py .

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]
```

### Step 2: Create Flask API

```python
# app.py
from flask import Flask, request, jsonify
from agent import MultiAgentOrchestrator
import os

app = Flask(__name__)

# Initialize orchestrator
orchestrator = MultiAgentOrchestrator(
    enable_tracing=True,
    enable_metrics=True
)

@app.route('/review', methods=['POST'])
def review_code():
    data = request.json
    code = data.get('code')
    language = data.get('language')
    
    result = orchestrator.execute_sequential_workflow(
        code=code,
        language=language
    )
    
    return jsonify(result)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
```

### Step 3: Deploy to Cloud Run

```bash
# Set your project ID
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"

# Build container
gcloud builds submit --tag gcr.io/$PROJECT_ID/code-review-agent

# Deploy to Cloud Run
gcloud run deploy code-review-agent \
  --image gcr.io/$PROJECT_ID/code-review-agent \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY \
  --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY \
  --memory 2Gi \
  --timeout 300

# Get the URL
gcloud run services describe code-review-agent \
  --platform managed \
  --region $REGION \
  --format 'value(status.url)'
```

### Step 4: Test Deployment

```bash
curl -X POST https://your-service-url.run.app/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def test():\n    x = 1\n    return x",
    "language": "python"
  }'
```

### Cost Optimization
- Cloud Run pricing: Pay only when handling requests
- Free tier: 2 million requests/month
- Estimated cost: $5-20/month for moderate use

---

## Option 2: Docker Container

Deploy as a Docker container on any platform (AWS ECS, Azure, etc.)

### Build Image

```bash
# Build
docker build -t code-review-agent:latest .

# Run locally
docker run -p 8080:8080 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e GEMINI_API_KEY=$GEMINI_API_KEY \
  code-review-agent:latest

# Test
curl http://localhost:8080/health
```

### Push to Registry

```bash
# Docker Hub
docker tag code-review-agent:latest username/code-review-agent:latest
docker push username/code-review-agent:latest

# Google Container Registry
docker tag code-review-agent:latest gcr.io/$PROJECT_ID/code-review-agent:latest
docker push gcr.io/$PROJECT_ID/code-review-agent:latest
```

---

## Option 3: Local Development Server

Run locally for development and testing.

### Flask Server

```bash
# Install dependencies
pip install flask gunicorn

# Run development server
python app.py

# Or with Gunicorn (production)
gunicorn -w 4 -b 0.0.0.0:8080 app:app
```

### FastAPI Alternative

```python
# app_fastapi.py
from fastapi import FastAPI
from pydantic import BaseModel
from agent import MultiAgentOrchestrator

app = FastAPI()
orchestrator = MultiAgentOrchestrator()

class CodeReviewRequest(BaseModel):
    code: str
    language: str = None

@app.post("/review")
async def review_code(request: CodeReviewRequest):
    result = orchestrator.execute_sequential_workflow(
        code=request.code,
        language=request.language
    )
    return result

# Run with: uvicorn app_fastapi:app --host 0.0.0.0 --port 8080
```

---

## Option 4: Agent Engine Deployment

Deploy using Google's Agent Engine (recommended for competition).

### Step 1: Configure Agent

```yaml
# agent.yaml
name: code-review-agent
description: AI-powered code review and debug agent
version: 1.0.0

runtime:
  language: python
  version: "3.10"
  
endpoints:
  - name: review
    method: POST
    handler: agent.handle_review
    
  - name: debug
    method: POST
    handler: agent.handle_debug

environment:
  OPENAI_API_KEY: ${OPENAI_API_KEY}
  GEMINI_API_KEY: ${GEMINI_API_KEY}

resources:
  memory: 2Gi
  cpu: 2
  timeout: 300s

scaling:
  min_instances: 0
  max_instances: 10
```

### Step 2: Deploy

```bash
# Using Agent Engine CLI
agent-engine deploy \
  --config agent.yaml \
  --project $PROJECT_ID \
  --region $REGION
```

---

## Security Best Practices

### 1. API Key Management

```python
# Use Secret Manager
from google.cloud import secretmanager

def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# In your app
OPENAI_API_KEY = get_secret("openai-api-key")
GEMINI_API_KEY = get_secret("gemini-api-key")
```

### 2. Authentication

```python
# Add API key authentication
from functools import wraps
from flask import request

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != os.environ.get('API_KEY'):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/review', methods=['POST'])
@require_api_key
def review_code():
    # ... your code
```

### 3. Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/review', methods=['POST'])
@limiter.limit("10 per minute")
def review_code():
    # ... your code
```

---

## Monitoring & Observability

### Built-in Metrics

```python
from agent import MultiAgentOrchestrator

orchestrator = MultiAgentOrchestrator(
    enable_tracing=True,
    enable_metrics=True
)

# Get metrics endpoint
@app.route('/metrics', methods=['GET'])
def get_metrics():
    return jsonify(orchestrator.get_metrics_summary())

# Get traces endpoint
@app.route('/traces', methods=['GET'])
def get_traces():
    return jsonify(orchestrator.get_trace_log())
```

### Cloud Monitoring Integration

```python
from google.cloud import monitoring_v3

def record_metric(metric_name, value):
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{PROJECT_ID}"
    
    series = monitoring_v3.TimeSeries()
    series.metric.type = f"custom.googleapis.com/{metric_name}"
    
    point = monitoring_v3.Point()
    point.value.double_value = value
    
    series.points = [point]
    client.create_time_series(name=project_name, time_series=[series])
```

---

## Load Testing

Test your deployment's performance:

```bash
# Using Apache Bench
ab -n 100 -c 10 -p request.json -T application/json \
  https://your-service-url.run.app/review

# Using Locust
# locustfile.py
from locust import HttpUser, task

class CodeReviewUser(HttpUser):
    @task
    def review_code(self):
        self.client.post("/review", json={
            "code": "def test(): pass",
            "language": "python"
        })

# Run: locust -f locustfile.py
```

---

## Deployment Checklist

- [ ] Dockerfile created
- [ ] API endpoints implemented
- [ ] Environment variables configured
- [ ] API keys secured (Secret Manager)
- [ ] Container built and tested locally
- [ ] Deployed to Cloud Run / Agent Engine
- [ ] Health check endpoint working
- [ ] Authentication implemented
- [ ] Rate limiting configured
- [ ] Monitoring enabled
- [ ] Load tested
- [ ] Documentation updated
- [ ] URL shared in submission

---

## Cost Estimates

### Google Cloud Run
- **Free Tier**: 2M requests/month
- **Light Use**: $5-10/month
- **Moderate Use**: $20-50/month
- **Heavy Use**: $100-200/month

### Optimization Tips
1. Use caching for repeated code reviews
2. Implement request batching
3. Use cheaper models when possible (Gemini vs GPT-4)
4. Set appropriate timeout limits
5. Scale to zero when idle

---

## Troubleshooting

### Common Issues

**1. Out of Memory**
```bash
# Increase memory allocation
gcloud run services update code-review-agent \
  --memory 4Gi
```

**2. Timeout Errors**
```bash
# Increase timeout
gcloud run services update code-review-agent \
  --timeout 600
```

**3. Cold Start Latency**
```bash
# Set minimum instances
gcloud run services update code-review-agent \
  --min-instances 1
```

---

## Evidence for Bonus Points

Include in your submission:
1. ✅ Deployment URL
2. ✅ Screenshots of Cloud Run dashboard
3. ✅ API request/response examples
4. ✅ Monitoring metrics screenshots
5. ✅ This deployment documentation

---

## Next Steps

1. Deploy to Cloud Run for bonus points
2. Test all endpoints
3. Take screenshots for submission
4. Include deployment URL in README
5. Document any issues encountered

---

*Deployment guide for Kaggle Agents Intensive Capstone Project*


