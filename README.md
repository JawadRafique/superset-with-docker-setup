# My Superset Project

A simple Apache Superset setup with MySQL database integration, built on top of the official `apache/superset:5.0.0` image.

## 🎯 Purpose

This project provides a streamlined way to:
- Set up Apache Superset with MySQL database support
- Auto-initialize Superset with admin user creation
- Use environment-based configuration for easy deployment
- Build a custom Docker image with MySQL drivers included

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- MySQL database (local or cloud-based like Azure MySQL)
- Port 8088 available for Superset

### 1. Clone and Setup

```bash
git clone https://github.com/JawadRafique/superset-with-docker-setup
cd my-superset
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` file and update your MySQL database credentials:

```bash
# Update these with your MySQL credentials
DATABASE_URL=mysql://your-username:your-password@your-host:3306/your-database
# Generate this secret key with openssl rand -base64 42 
SECRET_KEY=your-secret-key

# Superset Admin User Configuration
SUPERSET_ADMIN_USERNAME=admin
SUPERSET_ADMIN_PASSWORD=admin123
SUPERSET_ADMIN_FIRST_NAME=Super
SUPERSET_ADMIN_LAST_NAME=Admin
SUPERSET_ADMIN_EMAIL=admin@yourcompany.com

# Superset Application Configuration
SUPERSET_ENV=development
SUPERSET_LOAD_EXAMPLES=no
SUPERSET_WEBSERVER_PREFIX=/dash
```

### 3. Build Custom Image

```bash
docker build . -t mysuperset:latest
```

### 4. Start Superset

```bash
docker-compose up -d
```

### 5. Access Superset

- **Superset Dashboard**: http://localhost:8088
- Login with the credentials you set in the `.env` file

## 📁 Project Structure

```
.
├── docker-compose.yml          # Service orchestration
├── Dockerfile                  # Custom Superset image with MySQL drivers
├── entrypoint.sh              # Auto-initialization script
├── superset_config.py         # Superset configuration
├── .env.example              # Environment variables template
├── .gitignore               # Git ignore rules
├── volumes/                # Persistent data storage
│   └── superset/          # Superset application data
└── README.md             # This file
```

## 🔧 Configuration

### Environment Variables

The project uses environment variables for configuration:

- `DATABASE_URL`: MySQL connection string
- `SECRET_KEY`: Superset secret key for sessions
- `SUPERSET_ADMIN_*`: Admin user configuration
- `SUPERSET_ENV`: Environment mode (development/production)

### Auto-Initialization

The custom entrypoint script automatically:
1. Waits for MySQL database to be ready
2. Creates database schema if needed
3. Creates admin user on first run
4. Upgrades database on subsequent runs
5. Starts Superset web server

## 🛠️ Development

### Rebuilding the Image

After making changes to configuration:

```bash
docker build --no-cache . -t mysuperset:latest
docker-compose up -d
```

### Accessing the Container

```bash
docker exec -it jawad-superset bash
```

### Viewing Logs

```bash
docker-compose logs -f superset
```

## 🔗 MySQL Integration

This setup is specifically designed for MySQL databases:

- Includes both `mysqlclient` and `PyMySQL` drivers
- Automatic MySQL connection validation
- Optimized engine options for MySQL performance
- Support for cloud databases like Azure MySQL

### Connection String Format

```bash
# Standard MySQL
DATABASE_URL=mysql://username:password@host:port/database

# Azure MySQL (with SSL)
DATABASE_URL=mysql://username:password@host:port/database?ssl_mode=REQUIRED
```

## 🚨 Troubleshooting

### Common Issues

**Database Connection Failed:**
- Verify MySQL credentials in `.env`
- Ensure MySQL server is accessible
- Check firewall settings for cloud databases

**Image Build Issues:**
- Use `--no-cache` flag when rebuilding
- Ensure Docker has sufficient memory

**Environment Variables Not Loading:**
- Verify `.env` file exists and is properly formatted
- Rebuild image after configuration changes

### Reset Environment

To start fresh:
```bash
docker-compose down -v
rm -rf volumes/
docker build --no-cache . -t mysuperset:latest
docker-compose up -d
```

## 📚 Documentation

- [Github Repo](https://github.com/JawadRafique/superset-with-docker-setup)
- [Public Docker Image](https://hub.docker.com/r/jawadrafique/jawad-superset)
- [Apache Superset Documentation](https://superset.apache.org/docs/intro)
- [MySQL Connection Guide](https://superset.apache.org/docs/databases/mysql)

## 📄 License

This project is licensed under the MIT License.

---

**Note**: This is a development-focused setup. For production deployments, ensure proper security configurations, SSL certificates, and resource allocations.