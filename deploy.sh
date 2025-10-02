#!/bin/bash

# VnExpress News Scraper API Deployment Script

set -e

echo "🚀 VnExpress News Scraper API Deployment"
echo "========================================"

# Function to install dependencies
install_dependencies() {
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed successfully"
}

# Function to run with Gunicorn
deploy_gunicorn() {
    echo "🌟 Starting with Gunicorn..."
    gunicorn -c gunicorn.conf.py main:app
}

# Function to build and run Docker
deploy_docker() {
    echo "🐳 Building Docker image..."
    docker build -t vnexpress-api .
    echo "🚀 Running Docker container..."
    docker run -d -p 8000:8000 --name vnexpress-api-container vnexpress-api
    echo "✅ Docker deployment complete"
    echo "🌐 API available at: http://localhost:8000"
}

# Function to deploy with Docker Compose
deploy_docker_compose() {
    echo "🐳 Deploying with Docker Compose..."
    docker-compose up -d
    echo "✅ Docker Compose deployment complete"
    echo "🌐 API available at: http://localhost:8000"
}

# Function to setup systemd service
setup_systemd() {
    echo "⚙️  Setting up systemd service..."
    sudo cp vnexpress-api.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable vnexpress-api.service
    sudo systemctl start vnexpress-api.service
    echo "✅ Systemd service setup complete"
    echo "📊 Check status with: sudo systemctl status vnexpress-api"
}

# Function to display help
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  install     Install dependencies only"
    echo "  gunicorn    Deploy with Gunicorn (production)"
    echo "  docker      Deploy with Docker"
    echo "  compose     Deploy with Docker Compose"
    echo "  systemd     Setup systemd service (requires sudo)"
    echo "  dev         Run development server"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 install                 # Install dependencies"
    echo "  $0 gunicorn               # Production deployment with Gunicorn"
    echo "  $0 docker                 # Docker deployment"
    echo "  $0 compose                # Docker Compose deployment"
}

# Parse command line arguments
case "${1:-help}" in
    install)
        install_dependencies
        ;;
    gunicorn)
        install_dependencies
        deploy_gunicorn
        ;;
    docker)
        deploy_docker
        ;;
    compose)
        deploy_docker_compose
        ;;
    systemd)
        install_dependencies
        setup_systemd
        ;;
    dev)
        install_dependencies
        echo "🔧 Starting development server..."
        python main.py
        ;;
    help|*)
        show_help
        ;;
esac