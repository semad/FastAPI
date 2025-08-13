#!/bin/bash

# FastAPI Project Cleanup Script
# This script stops all containers and removes all volumes

set -e  # Exit on any error

echo "🧹 Starting FastAPI project cleanup..."

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Function to stop and remove containers
cleanup_containers() {
    echo "📦 Stopping and removing containers..."
    
    # Stop all running containers
    if docker ps -q | grep -q .; then
        echo "   Stopping running containers..."
        docker stop $(docker ps -q) 2>/dev/null || true
    fi
    
    # Remove all containers
    if docker ps -aq | grep -q .; then
        echo "   Removing containers..."
        docker rm $(docker ps -aq) 2>/dev/null || true
    fi
    
    echo "   ✅ Containers cleaned up"
}

# Function to remove volumes
cleanup_volumes() {
    echo "🗂️  Removing volumes..."
    
    # Get list of volumes
    VOLUMES=$(docker volume ls -q 2>/dev/null || true)
    
    if [ -n "$VOLUMES" ]; then
        echo "   Removing volumes: $VOLUMES"
        echo "$VOLUMES" | xargs -r docker volume rm
        echo "   ✅ Volumes removed"
    else
        echo "   ℹ️  No volumes to remove"
    fi
}

# Function to remove networks
cleanup_networks() {
    echo "🌐 Cleaning up networks..."
    
    # Remove custom networks (skip default ones)
    CUSTOM_NETWORKS=$(docker network ls --filter "type=custom" -q 2>/dev/null || true)
    
    if [ -n "$CUSTOM_NETWORKS" ]; then
        echo "   Removing custom networks..."
        echo "$CUSTOM_NETWORKS" | xargs -r docker network rm
        echo "   ✅ Custom networks removed"
    else
        echo "   ℹ️  No custom networks to remove"
    fi
}

# Function to remove images (optional)
cleanup_images() {
    echo "🖼️  Removing unused images..."
    
    # Remove dangling images
    DANGLING_IMAGES=$(docker images -f "dangling=true" -q 2>/dev/null || true)
    
    if [ -n "$DANGLING_IMAGES" ]; then
        echo "   Removing dangling images..."
        echo "$DANGLING_IMAGES" | xargs -r docker rmi
        echo "   ✅ Dangling images removed"
    else
        echo "   ℹ️  No dangling images to remove"
    fi
}

# Function to cleanup project-specific resources
cleanup_project() {
    echo "🏗️  Cleaning up project-specific resources..."
    
    # Stop and remove project containers if docker-compose is available
    if command -v docker-compose >/dev/null 2>&1; then
        if [ -f "docker-compose.yml" ]; then
            echo "   Stopping docker-compose services..."
            docker-compose down -v --remove-orphans 2>/dev/null || true
            echo "   ✅ Docker-compose services stopped and volumes removed"
        fi
    fi
    
    # Alternative: use docker compose (newer versions)
    if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
        if [ -f "docker-compose.yml" ]; then
            echo "   Stopping docker compose services..."
            docker compose down -v --remove-orphans 2>/dev/null || true
            echo "   ✅ Docker compose services stopped and volumes removed"
        fi
    fi
}

# Function to show cleanup summary
show_summary() {
    echo ""
    echo "🎉 Cleanup completed successfully!"
    echo ""
    echo "📊 Current status:"
    echo "   Containers: $(docker ps -aq 2>/dev/null | wc -l | tr -d ' ') running"
    echo "   Volumes: $(docker volume ls -q 2>/dev/null | wc -l | tr -d ' ') remaining"
    echo "   Networks: $(docker network ls -q 2>/dev/null | wc -l | tr -d ' ') remaining"
    echo "   Images: $(docker images -q 2>/dev/null | wc -l | tr -d ' ') remaining"
    echo ""
}

# Main execution
main() {
    echo "🚀 FastAPI Project Cleanup Script"
    echo "=================================="
    echo ""
    
    # Check if Docker is running
    check_docker
    
    # Cleanup project-specific resources first
    cleanup_project
    
    # Cleanup containers
    cleanup_containers
    
    # Cleanup volumes
    cleanup_volumes
    
    # Cleanup networks
    cleanup_networks
    
    # Optional: cleanup images
    if [ "$1" = "--remove-images" ]; then
        cleanup_images
    fi
    
    # Show summary
    show_summary
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --remove-images    Also remove unused Docker images"
        echo "  --help, -h         Show this help message"
        echo ""
        echo "This script will:"
        echo "  - Stop all running containers"
        echo "  - Remove all containers"
        echo "  - Remove all volumes"
        echo "  - Remove custom networks"
        echo "  - Clean up project-specific resources"
        echo ""
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac


