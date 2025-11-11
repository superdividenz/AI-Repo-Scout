# 🐳 Docker Setup for AI Repo Scout

## Quick Start

```bash
# Start Docker Desktop (if not running)
open -a Docker

# Build and run with docker-compose (recommended)
docker-compose up --build

# Or build manually
docker build -t ai-repo-scout:free .
docker run -p 8503:8503 ai-repo-scout:free
```

## Access Points

- **Dashboard**: http://localhost:8503
- **Health Check**: http://localhost:8503/\_stcore/health

## Environment Variables

Create a `.env` file for API tokens:

```bash
# .env file
GITHUB_TOKEN=your_github_token_here
DEEPSEEK_API_KEY=your_deepseek_key_here
```

## Docker Commands

### Using Docker Compose (Recommended)

```bash
# Build and start dashboard
docker-compose up --build

# Run in background
docker-compose up -d --build

# Run analysis only (no dashboard)
docker-compose --profile analysis up analyzer

# Stop all services
docker-compose down
```

### Using Docker Directly

```bash
# Build image
docker build -t ai-repo-scout:free .

# Run dashboard (interactive)
docker run -it -p 8503:8503 \
  -e GITHUB_TOKEN="$GITHUB_TOKEN" \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/reports:/app/reports \
  ai-repo-scout:free

# Run analysis (CLI)
docker run --rm \
  -e GITHUB_TOKEN="$GITHUB_TOKEN" \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/reports:/app/reports \
  ai-repo-scout:free \
  python3 src/main.py --timeframe daily --languages python --ai-provider huggingface

# Run free version demo
docker run --rm ai-repo-scout:free python3 demo_free.py
```

## Volume Mounts

- `/app/data` - Analysis cache and exports
- `/app/reports` - Generated reports (Markdown, HTML, JSON)
- `/app/config.yaml` - Configuration file

## Container Features

- **Multi-stage optimized** - Minimal image size
- **Health checks** - Automatic container monitoring
- **Persistent data** - Reports and cache survive restarts
- **Environment isolation** - No conflicts with host Python
- **Easy deployment** - Works on any Docker-enabled system

## Production Deployment

### Docker Swarm

```bash
docker stack deploy -c docker-compose.yml ai-repo-scout
```

### Kubernetes

```bash
# Generate Kubernetes manifests
docker-compose config | kompose convert -f -

# Apply to cluster
kubectl apply -f ai-repo-scout-*.yaml
```

### Cloud Platforms

- **AWS ECS**: Use docker-compose.yml with ECS CLI
- **Google Cloud Run**: Deploy with `gcloud run deploy`
- **Azure Container Instances**: Use `az container create`

## Troubleshooting

### Docker Desktop Not Running

```bash
# Start Docker Desktop
open -a Docker
# Wait for startup, then retry build
```

### Port Already in Use

```bash
# Use different port
docker run -p 8504:8503 ai-repo-scout:free

# Or find and stop conflicting process
lsof -ti:8503 | xargs kill -9
```

### Memory Issues

```bash
# Increase Docker memory limit in Docker Desktop settings
# Or use resource limits
docker run --memory=2g ai-repo-scout:free
```

## Container Logs

```bash
# View logs
docker-compose logs -f

# Debug specific service
docker-compose logs ai-repo-scout

# Container shell access
docker exec -it ai-repo-scout bash
```
