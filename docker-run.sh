#!/bin/bash
# Docker deployment and management script for AI Repo Scout

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is installed and running
check_docker() {
    log_info "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker Desktop."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    
    log_success "Docker is installed and running"
}

# Build the Docker image
build_image() {
    log_info "Building AI Repo Scout Docker image..."
    docker build -t ai-repo-scout:latest .
    log_success "Docker image built successfully"
}

# Start the services
start_services() {
    log_info "Starting AI Repo Scout services..."
    docker-compose up -d
    log_success "Services started successfully"
    log_info "Dashboard available at: http://localhost:8501"
}

# Stop the services
stop_services() {
    log_info "Stopping AI Repo Scout services..."
    docker-compose down
    log_success "Services stopped successfully"
}

# Show service status
status() {
    log_info "AI Repo Scout service status:"
    docker-compose ps
}

# Show logs
logs() {
    log_info "AI Repo Scout logs:"
    docker-compose logs -f ai-repo-scout
}

# Run batch analysis
run_batch() {
    local languages=${1:-"python javascript"}
    local timeframe=${2:-"daily"}
    
    log_info "Running batch analysis for: $languages ($timeframe)"
    docker-compose run --rm ai-repo-scout-batch python3 src/main.py \
        --timeframe "$timeframe" \
        --languages $languages \
        --ai-provider huggingface
    log_success "Batch analysis completed"
}

# Clean up Docker resources
cleanup() {
    log_info "Cleaning up Docker resources..."
    docker-compose down -v
    docker image rm ai-repo-scout:latest 2>/dev/null || true
    docker system prune -f
    log_success "Cleanup completed"
}

# Setup environment file
setup_env() {
    log_info "Setting up environment configuration..."
    
    if [ ! -f .env ]; then
        cat > .env << EOF
# GitHub API Token (optional but recommended)
# Get from: https://github.com/settings/tokens
GITHUB_TOKEN=

# DeepSeek API Key (optional - for enhanced AI analysis)
# Get from: https://platform.deepseek.com/
DEEPSEEK_API_KEY=
EOF
        log_success "Created .env file. Please edit it to add your API tokens."
        log_warning "Without GITHUB_TOKEN, you're limited to 60 API calls/hour"
    else
        log_info ".env file already exists"
    fi
}

# Main menu
show_help() {
    echo "🚀 AI Repo Scout - Docker Management"
    echo "=================================="
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  setup     - Check requirements and setup environment"
    echo "  build     - Build Docker image"
    echo "  start     - Start dashboard service"
    echo "  stop      - Stop all services" 
    echo "  restart   - Restart services"
    echo "  status    - Show service status"
    echo "  logs      - Show service logs"
    echo "  batch     - Run batch analysis (usage: batch 'python go' weekly)"
    echo "  cleanup   - Remove all Docker resources"
    echo "  shell     - Open shell in container"
    echo ""
    echo "Examples:"
    echo "  $0 setup && $0 start              # First time setup"
    echo "  $0 batch 'python javascript'      # Analyze Python and JavaScript"
    echo "  $0 batch 'go rust' weekly         # Weekly analysis of Go and Rust"
    echo ""
}

# Open shell in container
shell() {
    log_info "Opening shell in AI Repo Scout container..."
    docker-compose exec ai-repo-scout /bin/bash || \
    docker-compose run --rm ai-repo-scout /bin/bash
}

# Main script logic
case "${1:-help}" in
    setup)
        check_docker
        setup_env
        build_image
        log_success "Setup completed! Run '$0 start' to launch the dashboard."
        ;;
    build)
        check_docker
        build_image
        ;;
    start)
        check_docker
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        start_services
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    batch)
        check_docker
        run_batch "$2" "$3"
        ;;
    cleanup)
        cleanup
        ;;
    shell)
        shell
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac