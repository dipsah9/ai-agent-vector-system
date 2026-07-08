#!/bin/bash

echo "🚀 Setting up AI Agent Vector System..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create .env file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file from example"
fi

# Pull and start Ollama models
echo "📦 Pulling LLM models (this may take a few minutes)..."
docker compose up -d ollama

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to start..."
sleep 10

# Pull embedding model
echo "📦 Pulling embedding model..."
docker exec ollama_server ollama pull nomic-embed-text

# Pull chat model
echo "📦 Pulling chat model..."
docker exec ollama_server ollama pull llama3.2

# Start all services
echo "🔄 Starting all services..."
docker compose up -d

echo "✅ System is ready!"
echo "📊 API: http://localhost:8000"
echo "📈 Grafana: http://localhost:3000 (admin/admin)"
echo "🔍 Prometheus: http://localhost:9090"