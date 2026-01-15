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
    # Always check if Superset tables exist in the database first
    echo -e "${BLUE}🔍 Checking if Superset tables exist in database...${NC}"
    
    # Check for key Superset tables in the database
    if python -c "
import MySQLdb
import os
import sys
try:
    # Get database connection info
    if os.environ.get('DATABASE_URL'):
        import re
        url = os.environ.get('DATABASE_URL', '')
        match = re.match(r'mysql\+?.*://([^:]+):([^@]+)@([^:/]+):?(\d*)/(\w+)', url)
        if match:
            user, password, host, port, database = match.groups()
            port = int(port) if port else 3306
        else:
            sys.exit(1)
    elif all(os.environ.get(key) for key in ['DB_HOST', 'DB_USERNAME', 'DB_PASSWORD', 'DB_DATABASE']):
        host = os.environ.get('DB_HOST')
        port = int(os.environ.get('DB_PORT', 3306))
        user = os.environ.get('DB_USERNAME')
        password = os.environ.get('DB_PASSWORD')
        database = os.environ.get('DB_DATABASE')
    else:
        print('No database configuration found')
        sys.exit(1)
    
    # Connect and check for Superset tables
    conn = MySQLdb.connect(host=host, port=port, user=user, passwd=password, db=database)
    cursor = conn.cursor()
    
    # Check for key Superset tables
    cursor.execute(\"SHOW TABLES LIKE 'ab_user'\")
    ab_user_exists = cursor.fetchone() is not None
    
    cursor.execute(\"SHOW TABLES LIKE 'dashboards'\")
    dashboards_exists = cursor.fetchone() is not None
    
    cursor.execute(\"SHOW TABLES LIKE 'slices'\")
    slices_exists = cursor.fetchone() is not None
    
    # Check if ab_user table has actual admin users (check both configured and existing)
    admin_user_exists = False
    if ab_user_exists:
        # First check for the configured admin username
        admin_username = os.environ.get('SUPERSET_ADMIN_USERNAME', 'admin')
        cursor.execute(\"SELECT COUNT(*) FROM ab_user WHERE username = %s\", (admin_username,))
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            # If configured admin doesn't exist, check for any admin users with Admin role
            cursor.execute(\"SELECT COUNT(*) FROM ab_user u JOIN ab_user_role ur ON u.id = ur.user_id JOIN ab_role r ON ur.role_id = r.id WHERE r.name = 'Admin'\")
            existing_admin_count = cursor.fetchone()[0]
            admin_user_exists = existing_admin_count > 0
            if admin_user_exists:
                print(f'Found existing admin user(s) with Admin role, but not with configured username: {admin_username}')
        else:
            admin_user_exists = True
    
    cursor.close()
    conn.close()
    
    if ab_user_exists and dashboards_exists and slices_exists and admin_user_exists:
        print('Superset tables and admin user found in database')
        sys.exit(0)
    else:
        print(f'Incomplete Superset installation detected:')
        print(f'  ab_user table: {ab_user_exists}')
        print(f'  dashboards table: {dashboards_exists}')
        print(f'  slices table: {slices_exists}')
        print(f'  admin user: {admin_user_exists}')
        print('Database requires initialization')
        sys.exit(1)
        
except Exception as e:
    print(f'Database check failed: {e}')
    sys.exit(1)
"; then
        echo -e "${GREEN}✅ Superset tables and admin user found in database${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Database requires initialization or is incomplete${NC}"
        # Remove stale marker file if it exists
        rm -f /app/superset_home/.superset_initialized
        return 1
    fi
}

# Function to initialize superset
initialize_superset() {
    echo -e "${BLUE}🔧 Initializing Superset...${NC}"
    
    # FORCE MySQL credential verification before proceeding
    echo -e "${YELLOW}🔒 Verifying MySQL credentials before initialization...${NC}"
    
    # Determine which database configuration to use
    if [[ -n "$DB_HOST" && -n "$DB_USERNAME" && -n "$DB_PASSWORD" && -n "$DB_DATABASE" ]]; then
        echo -e "${BLUE}📊 Using individual MySQL configuration${NC}"
        MYSQL_HOST="$DB_HOST"
        MYSQL_PORT="${DB_PORT:-3306}"
        MYSQL_USER="$DB_USERNAME"
        MYSQL_PASS="$DB_PASSWORD"
        MYSQL_DB="$DB_DATABASE"
        
        # Force set DATABASE_URL for Superset
        export DATABASE_URL="mysql://${MYSQL_USER}:${MYSQL_PASS}@${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DB}"
        export SQLALCHEMY_DATABASE_URI="$DATABASE_URL"
        
    elif [[ -n "$DATABASE_URL" && "$DATABASE_URL" == mysql* ]]; then
        echo -e "${BLUE}📊 Using DATABASE_URL MySQL configuration${NC}"
        # Parse DATABASE_URL to extract components
        if python -c "
import os
import re
url = os.environ.get('DATABASE_URL', '')
match = re.match(r'mysql\+?.*://([^:]+):([^@]+)@([^:/]+):?(\d*)/(\w+)', url)
if match:
    user, password, host, port, database = match.groups()
    port = int(port) if port else 3306
    print(f'MYSQL_HOST={host}')
    print(f'MYSQL_PORT={port}')
    print(f'MYSQL_USER={user}')
    print(f'MYSQL_PASS={password}')
    print(f'MYSQL_DB={database}')
else:
    exit(1)
" > /tmp/mysql_vars; then
            source /tmp/mysql_vars
            rm /tmp/mysql_vars
            
            # Force set SQLALCHEMY_DATABASE_URI
            export SQLALCHEMY_DATABASE_URI="$DATABASE_URL"
        else
            echo -e "${RED}❌ Failed to parse DATABASE_URL for MySQL connection${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ No MySQL configuration found!${NC}"
        echo -e "${RED}❌ Superset REQUIRES MySQL database. SQLite is not allowed.${NC}"
        echo -e "${RED}❌ Please set either:${NC}"
        echo -e "${RED}   - DATABASE_URL=mysql+mysqlclient://user:pass@host:port/db${NC}"
        echo -e "${RED}   - Or: DB_HOST, DB_USERNAME, DB_PASSWORD, DB_DATABASE${NC}"
        exit 1
    fi
    
    # Test MySQL connection before proceeding
    echo -e "${YELLOW}🔌 Testing MySQL connection: ${MYSQL_USER}@${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DB}${NC}"
    if ! python -c "
import MySQLdb
import os
try:
    conn = MySQLdb.connect(host='${MYSQL_HOST}', port=${MYSQL_PORT}, user='${MYSQL_USER}', passwd='${MYSQL_PASS}', db='${MYSQL_DB}')
    cursor = conn.cursor()
    cursor.execute('SELECT VERSION()')
    version = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    print(f'✅ MySQL connection successful! Version: {version}')
except Exception as e:
    print(f'❌ MySQL connection failed: {e}')
    exit(1)
"; then
        echo -e "${RED}❌ MySQL connection test failed! Cannot proceed with initialization.${NC}"
        exit 1
    fi
    
    # Print final database configuration
    echo -e "${GREEN}✅ MySQL credentials verified successfully!${NC}"
    echo -e "${BLUE}🔗 Database: mysql+mysqlclient://${MYSQL_USER}:***@${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DB}${NC}"
    
    # Mask password in SQLALCHEMY_DATABASE_URI for logging
    MASKED_URI=$(echo "${SQLALCHEMY_DATABASE_URI}" | sed -E 's/(:\/\/[^:]+:)[^@]+(@)/\1***\2/')
    echo -e "${BLUE}🔗 SQLALCHEMY_DATABASE_URI: ${MASKED_URI}${NC}"
    
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
    
    # Validate initialization by checking created tables
    echo -e "${BLUE}🔍 Validating initialization...${NC}"
    if python -c "
import MySQLdb
import os
try:
    # Get database connection info (same logic as before)
    if os.environ.get('DATABASE_URL'):
        import re
        url = os.environ.get('DATABASE_URL', '')
        match = re.match(r'mysql\+?.*://([^:]+):([^@]+)@([^:/]+):?(\d*)/(\w+)', url)
        if match:
            user, password, host, port, database = match.groups()
            port = int(port) if port else 3306
        else:
            raise Exception('Could not parse DATABASE_URL')
    else:
        host = os.environ.get('DB_HOST')
        port = int(os.environ.get('DB_PORT', 3306))
        user = os.environ.get('DB_USERNAME')
        password = os.environ.get('DB_PASSWORD')
        database = os.environ.get('DB_DATABASE')
    
    # Connect and check tables
    conn = MySQLdb.connect(host=host, port=port, user=user, passwd=password, db=database)
    cursor = conn.cursor()
    
    # Get table count
    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()
    table_count = len(tables)
    
    # Check for admin user
    cursor.execute('SELECT COUNT(*) FROM ab_user WHERE username = %s', (os.environ.get('SUPERSET_ADMIN_USERNAME', 'admin'),))
    admin_count = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    print(f'Successfully created {table_count} tables in database: {database}')
    print(f'Admin user created: {admin_count > 0}')
    
except Exception as e:
    print(f'Validation failed: {e}')
"; then
        echo -e "${GREEN}✅ Database initialization validated successfully!${NC}"
    else
        echo -e "${YELLOW}⚠️  Could not validate database initialization${NC}"
    fi
    
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