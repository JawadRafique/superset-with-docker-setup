#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Superset Auto-Initialize Entrypoint${NC}"

# Default values if not provided
SUPERSET_ADMIN_USERNAME=${SUPERSET_ADMIN_USERNAME:-admin}
SUPERSET_ADMIN_PASSWORD=${SUPERSET_ADMIN_PASSWORD:-admin}
SUPERSET_ADMIN_FIRST_NAME=${SUPERSET_ADMIN_FIRST_NAME:-Super}
SUPERSET_ADMIN_LAST_NAME=${SUPERSET_ADMIN_LAST_NAME:-Admin}
SUPERSET_ADMIN_EMAIL=${SUPERSET_ADMIN_EMAIL:-admin@company.com}
DATABASE_URL=${DATABASE_URL:-}

# Function to wait for database
wait_for_database() {
    echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
    
    # Check if using individual database config or DATABASE_URL
    if [[ -n "$DB_HOST" && -n "$DB_USERNAME" && -n "$DB_PASSWORD" && -n "$DB_DATABASE" ]]; then
        echo -e "${BLUE}📊 Using individual database configuration${NC}"
        DB_TYPE=${DB_TYPE:-mysql}
        DB_PORT=${DB_PORT:-3306}
        
        # Wait up to 60 seconds for database
        for i in {1..12}; do
            if python -c "
import MySQLdb
import os
try:
    db_type = os.environ.get('DB_TYPE', 'mysql')
    if 'mysql' in db_type.lower():
        host = os.environ.get('DB_HOST')
        port = int(os.environ.get('DB_PORT', 3306))
        user = os.environ.get('DB_USERNAME')
        password = os.environ.get('DB_PASSWORD')
        database = os.environ.get('DB_DATABASE')
        
        conn = MySQLdb.connect(host=host, port=port, user=user, passwd=password, db=database)
        conn.close()
        print('Database connection successful!')
    else:
        raise Exception(f'Unsupported database type: {db_type}')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
"; then
                echo -e "${GREEN}✅ Database is ready!${NC}"
                
                # Construct DATABASE_URL for Superset
                export DATABASE_URL="mysql+mysqlclient://${DB_USERNAME}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_DATABASE}"
                echo -e "${BLUE}🔗 Constructed DATABASE_URL for Superset${NC}"
                return 0
            fi
            echo -e "${YELLOW}⏳ Database not ready yet, waiting... (attempt $i/12)${NC}"
            sleep 5
        done
        echo -e "${RED}❌ Database failed to become ready after 60 seconds${NC}"
        exit 1
        
    elif [[ -n "$DATABASE_URL" ]]; then
        echo -e "${BLUE}📊 Using DATABASE_URL configuration${NC}"
        # Extract database type from DATABASE_URL
        if [[ $DATABASE_URL == mysql* ]]; then
            echo -e "${BLUE}📊 Detected MySQL database${NC}"
            # Wait up to 60 seconds for MySQL
            for i in {1..12}; do
                if python -c "
import MySQLdb
import os
try:
    url = os.environ.get('DATABASE_URL', '')
    # Parse mysql+pymysql://user:password@host:port/database
    if 'mysql' in url:
        import re
        match = re.match(r'mysql\+?.*://([^:]+):([^@]+)@([^:/]+):?(\d*)/(\w+)', url)
        if match:
            user, password, host, port, database = match.groups()
            port = int(port) if port else 3306
            conn = MySQLdb.connect(host=host, port=port, user=user, passwd=password, db=database)
            conn.close()
            print('Database connection successful!')
        else:
            raise Exception('Could not parse DATABASE_URL')
    else:
        raise Exception('Not a MySQL URL')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
"; then
                    echo -e "${GREEN}✅ Database is ready!${NC}"
                    return 0
                fi
                echo -e "${YELLOW}⏳ Database not ready yet, waiting... (attempt $i/12)${NC}"
                sleep 5
            done
            echo -e "${RED}❌ Database failed to become ready after 60 seconds${NC}"
            exit 1
        else
            echo -e "${BLUE}📊 Using default database setup${NC}"
            sleep 10  # Generic wait for other databases
        fi
    else
        echo -e "${RED}❌ No database configuration found. Please set either DATABASE_URL or individual DB_* variables${NC}"
        exit 1
    fi
}

# Function to check if superset is already initialized
is_initialized() {
    if [ -f "/app/superset_home/.superset_initialized" ]; then
        return 0
    else
        return 1
    fi
}

# Function to initialize superset
initialize_superset() {
    echo -e "${BLUE}🔧 Initializing Superset...${NC}"
    
    # Ensure superset home directory exists
    mkdir -p /app/superset_home
    
    # Database upgrade
    echo -e "${YELLOW}📈 Upgrading database schema...${NC}"
    superset db upgrade
    
    # Create admin user (only if not exists)
    echo -e "${YELLOW}👤 Creating admin user...${NC}"
    superset fab create-admin \
        --username "$SUPERSET_ADMIN_USERNAME" \
        --password "$SUPERSET_ADMIN_PASSWORD" \
        --firstname "$SUPERSET_ADMIN_FIRST_NAME" \
        --lastname "$SUPERSET_ADMIN_LAST_NAME" \
        --email "$SUPERSET_ADMIN_EMAIL" || echo "Admin user might already exist"
    
    # Initialize superset (roles, permissions, etc.)
    echo -e "${YELLOW}🎯 Setting up roles and permissions...${NC}"
    superset init
    
    # Load examples if requested
    if [ "$SUPERSET_LOAD_EXAMPLES" = "yes" ]; then
        echo -e "${YELLOW}📊 Loading example data...${NC}"
        superset load-examples || echo "Examples might already be loaded"
    fi
    
    # Mark as initialized
    touch /app/superset_home/.superset_initialized
    
    echo -e "${GREEN}✅ Superset initialization complete!${NC}"
}

# Main execution
echo -e "${BLUE}🔍 Checking initialization status...${NC}"

# Wait for database to be ready
wait_for_database

# Check if already initialized
if is_initialized; then
    echo -e "${GREEN}✅ Superset already initialized, starting server...${NC}"
else
    echo -e "${YELLOW}🔄 First run detected, initializing Superset...${NC}"
    initialize_superset
fi

# Start Superset server
echo -e "${BLUE}🌐 Starting Superset web server...${NC}"
exec /app/docker/entrypoints/run-server.sh