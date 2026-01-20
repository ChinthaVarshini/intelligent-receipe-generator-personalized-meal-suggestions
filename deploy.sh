#!/bin/bash

# Intelligent Recipe Generator Deployment Script
# This script handles deployment to various platforms

set -e

echo "🚀 Intelligent Recipe Generator Deployment"
echo "=========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your actual API keys and configuration."
fi

# Build and start services
echo "🏗️  Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
echo "🔍 Checking service health..."

# Check backend
if curl -f http://localhost:3000/database-status -H "X-API-Key: intelligent-recipe-generator-api-key-2023" &> /dev/null; then
    echo "✅ Backend service is healthy"
else
    echo "❌ Backend service failed to start"
    exit 1
fi

# Check frontend
if curl -f http://localhost:3001 &> /dev/null; then
    echo "✅ Frontend service is healthy"
else
    echo "❌ Frontend service failed to start"
    exit 1
fi

echo ""
echo "🎉 Deployment successful!"
echo "📱 Frontend: http://localhost:3001"
echo "🔧 Backend API: http://localhost:3000"
echo "📊 Database: localhost:5432"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop services: docker-compose down"
echo "To rebuild: docker-compose up --build"
