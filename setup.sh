#!/bin/bash

# Prima Scholar Setup Script
# This script sets up the complete Prima Scholar development environment

echo "🎓 Prima Scholar - Setup Script"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Docker and Docker Compose are installed${NC}"
}

# Create necessary directories
create_directories() {
    echo -e "${YELLOW}📁 Creating project directories...${NC}"
    
    mkdir -p backend/{models,services,routes,database}
    mkdir -p frontend/src/{components/{ui},utils}
    mkdir -p docs
    mkdir -p examples/{sample_documents}
    mkdir -p logs
    mkdir -p uploads
    
    echo -e "${GREEN}✅ Directories created${NC}"
}

# Setup environment variables
setup_env() {
    echo -e "${YELLOW}🔧 Setting up environment variables...${NC}"
    
    if [ ! -f .env ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ Created .env file from .env.example${NC}"
        echo -e "${YELLOW}⚠️  Please edit .env with your actual credentials:${NC}"
        echo "   - TiDB connection string"
        echo "   - OpenAI API key"
        echo "   - External API keys (optional)"
    else
        echo -e "${GREEN}✅ .env file already exists${NC}"
    fi
}

# Check environment variables
check_env() {
    echo -e "${YELLOW}🔍 Checking environment variables...${NC}"
    
    source .env
    
    if [ -z "$TIDB_CONNECTION_STRING" ] || [ "$TIDB_CONNECTION_STRING" = "mysql://username:password@host:4000/database?sslmode=require" ]; then
        echo -e "${RED}❌ Please configure TIDB_CONNECTION_STRING in .env${NC}"
        return 1
    fi
    
    if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "sk-your-openai-api-key-here" ]; then
        echo -e "${RED}❌ Please configure OPENAI_API_KEY in .env${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Environment variables configured${NC}"
    return 0
}

# Initialize database schema
init_database() {
    echo -e "${YELLOW}🗄️ Initializing database schema...${NC}"
    
    # This will be called after the backend container is running
    echo "Database initialization will be handled by the backend service on startup"
    echo -e "${GREEN}✅ Database initialization prepared${NC}"
}

# Build and start services
start_services() {
    echo -e "${YELLOW}🚀 Building and starting services...${NC}"
    
    # Build images
    echo "Building Docker images..."
    docker compose build --parallel
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Docker images built successfully${NC}"
    else
        echo -e "${RED}❌ Failed to build Docker images${NC}"
        return 1
    fi
    
    # Start services
    echo "Starting services..."
    docker compose up -d
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Services started successfully${NC}"
    else
        echo -e "${RED}❌ Failed to start services${NC}"
        return 1
    fi
    
    return 0
}

# Wait for services to be healthy
wait_for_services() {
    echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
    
    # Wait for backend
    echo "Checking backend health..."
    for i in {1..30}; do
        if curl -sf http://localhost:5000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend is ready${NC}"
            break
        fi
        sleep 2
        echo -n "."
    done
    
    # Wait for frontend
    echo "Checking frontend health..."
    for i in {1..30}; do
        if curl -sf http://localhost:3000 > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Frontend is ready${NC}"
            break
        fi
        sleep 2
        echo -n "."
    done
    
    # Wait for Redis
    echo "Checking Redis health..."
    if docker compose exec redis redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Redis is ready${NC}"
    else
        echo -e "${YELLOW}⚠️  Redis health check failed, but may still be working${NC}"
    fi
}

# Display final information
display_info() {
    echo ""
    echo "🎉 Prima Scholar Setup Complete!"
    echo "================================="
    echo ""
    echo "📍 Access your application:"
    echo "   Frontend:  http://localhost:3000"
    echo "   Backend:   http://localhost:5000"
    echo "   API Docs:  http://localhost:5000/docs"
    echo ""
    echo "🛠️ Useful commands:"
    echo "   View logs:     docker compose logs -f"
    echo "   Stop services: docker compose down"
    echo "   Restart:       docker compose restart"
    echo "   Clean up:      docker compose down -v"
    echo ""
    echo "📚 Next steps:"
    echo "   1. Upload academic documents at http://localhost:3000"
    echo "   2. Ask scholar-level questions to test the mentorship system"
    echo "   3. Check your excellence predictions and roadmap"
    echo "   4. Review API documentation for integration"
    echo ""
    echo "🎯 Demo ready! Your Prima Scholar system is now running."
    echo ""
}

# Main setup function
main() {
    echo "Starting Prima Scholar setup process..."
    echo ""
    
    check_docker
    create_directories
    setup_env
    
    # Ask user to configure environment variables
    echo -e "${YELLOW}📝 Please configure your .env file with actual credentials.${NC}"
    echo "Press Enter after configuring .env, or 'q' to quit:"
    read -r response
    
    if [ "$response" = "q" ]; then
        echo "Setup cancelled. Please configure .env and run setup again."
        exit 0
    fi
    
    if ! check_env; then
        echo -e "${RED}❌ Environment configuration incomplete. Please update .env and try again.${NC}"
        exit 1
    fi
    
    init_database
    
    if start_services; then
        wait_for_services
        display_info
        
        # Open browser (optional)
        if command -v xdg-open &> /dev/null; then
            echo "Opening browser..."
            xdg-open http://localhost:3000
        elif command -v open &> /dev/null; then
            echo "Opening browser..."
            open http://localhost:3000
        fi
        
    else
        echo -e "${RED}❌ Setup failed. Check the logs with: docker compose logs${NC}"
        exit 1
    fi
}

# Run main setup
main "$@"