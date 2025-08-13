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
    
    # Get all networks except the default ones that Docker needs
    # Default networks: bridge, host, none
    ALL_NETWORKS=$(docker network ls -q 2>/dev/null || true)
    DEFAULT_NETWORKS="bridge host none"
    
    if [ -n "$ALL_NETWORKS" ]; then
        if [ "$1" = "--remove-all-networks" ]; then
            echo "   Removing ALL networks (including default Docker networks)..."
            
            # Remove each network individually to handle errors gracefully
            for network_id in $ALL_NETWORKS; do
                network_name=$(docker network inspect --format='{{.Name}}' "$network_id" 2>/dev/null || echo "")
                echo "     Removing network: $network_name ($network_id)"
                docker network rm "$network_id" 2>/dev/null || echo "       ⚠️  Failed to remove network: $network_name"
            done
        else
            echo "   Removing all networks (except default Docker networks)..."
            
            # Remove each network individually to handle errors gracefully
            for network_id in $ALL_NETWORKS; do
                network_name=$(docker network inspect --format='{{.Name}}' "$network_id" 2>/dev/null || echo "")
                
                # Skip default networks
                if [[ " $DEFAULT_NETWORKS " =~ " $network_name " ]]; then
                    echo "     Skipping default network: $network_name"
                    continue
                fi
                
                echo "     Removing network: $network_name ($network_id)"
                docker network rm "$network_id" 2>/dev/null || echo "       ⚠️  Failed to remove network: $network_name"
            done
        fi
        
        echo "   ✅ Networks cleanup completed"
    else
        echo "   ℹ️  No networks to remove"
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
    cleanup_networks "$1"
    
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
        echo "  --remove-images        Also remove unused Docker images"
        echo "  --remove-all-networks  Remove ALL networks (including default Docker networks)"
        echo "  --help, -h             Show this help message"
        echo ""
        echo "This script will:"
        echo "  - Stop all running containers"
        echo "  - Remove all containers"
        echo "  - Remove all volumes"
        echo "  - Remove all networks (except default Docker networks)"
        echo "  - Clean up project-specific resources"
        echo ""
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac



