# Apache Superset with SAML Authentication 🚀

<!-- Version Management: Update version file and docker-compose.yml image tag when releasing -->
**Current Version: 1.0.1** - Enhanced Apache Superset setup with dual authentication support (SAML + Database) and complete enterprise integration.

> 📝 **Version Management**: The current version is dynamically managed through the [`version`](version) file. Update this file and corresponding Docker image tags when releasing new versions.

![Docker Pulls](https://img.shields.io/docker/pulls/jawadrafique/superset?style=flat-square)
![Docker Image Version](https://img.shields.io/docker/v/jawadrafique/superset/latest?style=flat-square)
![Docker Image Size](https://img.shields.io/docker/image-size/jawadrafique/superset/latest?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)

## ✨ Features (Latest Version)

### 🔐 Dual Authentication System
- **SAML SSO Integration** with Azure AD/ADFS
- **Database Authentication** fallback  
- **Seamless user experience** with unified login page
- **Enterprise-ready security** with X.509 certificates
- **Smart Logout Management** with cache clearing and multi-tab coordination

### 🎯 Core Capabilities  
- **Auto-initialization** with admin user creation
- **MySQL database integration** with optimized connection pooling  
- **Environment-based configuration** for easy deployment
- **Custom Docker image** with pre-installed SAML libraries
- **Helm chart support** for Kubernetes deployment
- **Advanced session management** with comprehensive cache clearing

## 🆕 What's New in v1.0.1

### 🚪 Enhanced Logout & Session Management (v1.0.1)
- **Smart logout options** with local vs full SAML logout
- **Multi-tab coordination** prevents 403 Forbidden errors
- **Comprehensive cache clearing** eliminates manual site data clearing
- **Real-time session monitoring** across browser tabs
- **SAML authentication fix** for Azure AD method conflicts (AADSTS75011)

### 🎥 SAML Authentication Demo (v1.0.0)
**[Watch the SAML Demo Video](https://youtu.be/eUC1EElVgTo)** - See complete SAML authentication flow with Azure AD integration!

### Production-Ready SAML Support  
- **Azure App Gateway SSL termination** compatibility
- **Updated Azure AD certificates** for signature validation
- **Enhanced error handling** and debugging for SAML authentication
- **Complete certificate management** (both SP and IdP certificates)
- **Verified working configuration** with Azure AD integration

### SAML Authentication Support
- **Azure AD/ADFS integration** with complete SAML 2.0 support
- **Dual login page** - users can choose SAML or database authentication  
- **Automatic user provisioning** from SAML attributes
- **Role mapping** from Azure AD groups to Superset roles
- **Full signature validation** with proper certificate management

### Enhanced Security  
- **Certificate-based SAML signing** for production environments
- **Configurable SAML validation** (strict/relaxed modes)
- **Debug mode** for troubleshooting SAML issues
- **Secure environment variable** configuration
- **Advanced logout management** with comprehensive cache clearing
- **Multi-tab session coordination** to prevent authentication errors

### 🚪 Advanced Logout & Session Management
- **Smart logout options** - Local logout (preserves Azure AD) or Full SAML logout
- **Comprehensive cache clearing** - localStorage, sessionStorage, IndexedDB, cookies
- **Multi-tab coordination** - Automatic logout across all browser tabs
- **Session monitoring** - Prevents 403 Forbidden errors in multiple tabs
- **Client-side cleanup** - Removes all cached authentication data

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- MySQL database (local or cloud-based like Azure MySQL)  
- Port 8088 available for Superset
- *Optional*: Azure AD application for SAML SSO

### 1. Clone and Setup

```bash
git clone https://github.com/JawadRafique/superset-with-docker-setup
cd my-superset
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` file with your configuration:

```bash
# =============================================================================
# Database Configuration (Required)
# =============================================================================  
DATABASE_URL=mysql://your-username:your-password@your-host:3306/your-database

# =============================================================================
# Security Configuration (Required)
# =============================================================================
# Generate with: openssl rand -base64 42
SECRET_KEY=your-secret-key

# =============================================================================
# Superset Admin User (Required)
# =============================================================================
SUPERSET_ADMIN_USERNAME=admin
SUPERSET_ADMIN_PASSWORD=admin123  
SUPERSET_ADMIN_FIRST_NAME=Super
SUPERSET_ADMIN_LAST_NAME=Admin
SUPERSET_ADMIN_EMAIL=admin@yourcompany.com

# =============================================================================
# SAML Authentication (Optional - v1.0.0+)
# =============================================================================
ENABLE_SAML_AUTH=true                    # Set to 'false' to disable SAML
SAML_DEFAULT_ROLE=Gamma                  # Default role for new SAML users

# Your Superset URLs (update for production)
SAML_SP_ENTITY_ID=https://your-superset-domain.com
SAML_SP_ACS_URL=https://your-superset-domain.com/acs  
SAML_SP_SLS_URL=https://your-superset-domain.com/login/?sls=true
SAML_SP_NAMEID_FORMAT=urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress

# SP Certificate and Private Key (Required for your working setup)
SAML_SP_X509_CERT=-----BEGIN CERTIFICATE-----\nYOUR_SP_CERTIFICATE\n-----END CERTIFICATE-----
SAML_SP_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nYOUR_SP_PRIVATE_KEY\n-----END PRIVATE KEY-----

# Azure AD Configuration (get from your Azure AD admin)
SAML_IDP_ENTITY_ID=https://sts.windows.net/your-tenant-id/
SAML_IDP_SSO_URL=https://login.microsoftonline.com/your-tenant-id/saml2
SAML_IDP_SLS_URL=https://login.microsoftonline.com/your-tenant-id/saml2

# Azure AD Signing Certificate (REQUIRED - get latest from Azure AD)
SAML_IDP_X509_CERT=-----BEGIN CERTIFICATE-----\nYOUR_LATEST_AZURE_CERTIFICATE\n-----END CERTIFICATE-----
```

### 3. Generate SAML Certificates (Required for SAML)

**SP Certificates**: Generate certificates for your Superset Service Provider:

```bash
# Generate private key and certificate for SAML SP
openssl req -x509 -new -newkey rsa:2048 -nodes \
  -keyout saml_sp.key -out saml_sp.crt -days 3650 \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=your-superset-domain.com"
```

Add the generated certificates to your `.env` file:

```bash
# Add these to your .env file
SAML_SP_X509_CERT="$(cat saml_sp.crt | tr -d '\n')"
SAML_SP_PRIVATE_KEY="$(cat saml_sp.key | tr -d '\n')"
```

**Azure AD Certificate**: Download the signing certificate from Azure AD:
1. Go to Azure AD > Enterprise Applications > Your App > Single sign-on
2. Download the **Certificate (Base64)** 
3. Add it to your `.env` file as `SAML_IDP_X509_CERT`

### 4. Build Custom Image

```bash
docker build . -t superset:1.0.1
```

### 5. Start Superset

```bash
docker-compose up -d
```

### 6. Access Superset

- **Superset Dashboard**: http://localhost:8088
- **Database + SAML Login**: Choose your preferred authentication method
- **Default Admin**: Use credentials from your `.env` file

## 🔐 SAML Authentication Setup

### Azure AD Configuration

1. **Register Application** in Azure AD
2. **Configure SAML**: Use Entity ID and ACS URL from your `.env` file  
3. **Generate Certificate**: Download the signing certificate
4. **Update .env**: Add Azure AD configuration details

### SAML User Flow

1. User visits http://localhost:8088
2. **Dual Login Page** displays with options:
   - **"Sign in with Azure"** button for SAML SSO
   - **Database login form** for local authentication
3. **SAML Users**: Redirected to Azure AD → auto-provisioned in Superset
4. **Database Users**: Direct login with username/password

### Troubleshooting SAML

Enable debug mode in your `.env` file:

```bash
SAML_DEBUG=true
```

Check logs for SAML authentication issues:

```bash
docker-compose logs superset | grep -i saml
```

## � Logout & Session Management

### Smart Logout Options

The enhanced logout system provides two modes to handle different security requirements:

#### **Local Logout (Default - Recommended)**
```bash
SAML_FORCE_LOCAL_LOGOUT=true  # Default setting
```
- **Logs out from Superset only** - preserves Azure AD session
- **Ideal for shared workstations** - users remain logged in to Office 365, Teams, etc.
- **Convenient re-login** - quick SAML authentication without re-entering credentials
- **Enhanced security** - comprehensive client-side cache clearing

#### **Full SAML Logout (Optional)**
```bash
SAML_FORCE_LOCAL_LOGOUT=false  # For high-security environments
```
- **Global logout** - logs out from both Superset AND Azure AD
- **Complete session termination** - ends all SAML-connected applications
- **Maximum security** - ensures no residual sessions

### Multi-Tab Session Coordination

**Problem Solved**: No more "403 Forbidden" errors when logging out with multiple Superset tabs open.

**Features**:
- **Automatic coordination** across all browser tabs
- **Real-time notifications** using BroadcastChannel API
- **Comprehensive cache clearing** - localStorage, sessionStorage, IndexedDB, cookies
- **Session monitoring** - detects expired sessions and auto-redirects
- **Fallback mechanisms** - localStorage events for older browsers

**User Experience**:
1. User logs out from any Superset tab
2. **All other tabs automatically redirect** to login page
3. **No manual cache clearing** required
4. **Seamless experience** across all browser tabs

### Cache & Storage Clearing

The logout process comprehensively clears:
- **Server-side**: Flask sessions, authentication cookies, SAML session data
- **Client-side**: localStorage, sessionStorage, IndexedDB, browser cache
- **Cross-tab**: Notifications to all open tabs via BroadcastChannel
- **Security headers**: No-cache directives to prevent authentication caching

## �📁 Project Structure

```
├── docker-compose.yml              # Service orchestration (current version)
├── Dockerfile                      # Custom image with SAML + MySQL support  
├── entrypoint.sh                  # Auto-initialization script
├── superset_config.py             # Configuration with SAML integration
├── auth_saml.py                   # Custom SAML security manager (v1.0.0+)
├── templates/                     # Custom templates for dual authentication
│   └── appbuilder/general/security/
│       ├── login_db.html         # Dual authentication login page
│       └── logout.html           # Enhanced logout with cache clearing (v1.0.1+)
├── helm/                          # Kubernetes deployment (v1.0.0+)
├── microservice-superset.yaml # Helm template with SAML support
│   └── values.yaml               # Configuration values
├── .env.example                   # Environment variables template  
├── .env                           # Your local configuration (git-ignored)
├── version                        # Current Version: 1.0.1
├── volumes/                       # Persistent data storage
│   └── superset/                  # Superset application data
└── README.md                      # This documentation
```

## 🏷️ Version Management

This project uses semantic versioning managed through the [`version`](version) file:

- **Current Version**: `1.0.1`
- **Docker Image Tag**: `superset:1.0.1` (in docker-compose.yml)
- **Release Notes**: See [What's New](#-whats-new-in-v101) sections for version history

**To release a new version:**
1. Update the [`version`](version) file
2. Update image tag in [`docker-compose.yml`](docker-compose.yml)
3. Update any version references in documentation
4. Build and tag Docker image: `docker build -t superset:$(cat version) .`

## 🔧 Configuration Files

### Key Files (v1.0.0)

#### [superset_config.py](superset_config.py)
- **Purpose**: Main configuration with conditional SAML support
- **Features**: Environment-based SAML toggle, template paths, security settings
- **SAML Integration**: Automatic SAML security manager loading when enabled

#### [auth_saml.py](auth_saml.py) ⚡ NEW
- **Purpose**: Custom SAML security manager for dual authentication  
- **Features**: Azure AD/ADFS integration, user auto-provisioning, role mapping
- **Template Support**: Custom login views with SAML + database options

#### [templates/appbuilder/general/security/login_db.html](templates/appbuilder/general/security/login_db.html) ⚡ NEW
- **Purpose**: Unified login page with dual authentication  
- **Features**: Azure AD button, database login form, responsive design
- **User Experience**: Seamless choice between SAML and database authentication

### Environment Variables

#### Core Configuration (Required)
- `DATABASE_URL`: MySQL connection string
- `SECRET_KEY`: Superset secret key for sessions  
- `SUPERSET_ADMIN_*`: Admin user configuration

#### SAML Configuration (Optional v1.0.0+)  
- `ENABLE_SAML_AUTH`: Toggle SAML authentication (true/false)
- `SAML_SP_*`: Service Provider configuration (Entity ID, ACS URL, certificates)
- `SAML_IDP_*`: Identity Provider configuration (Azure AD details)
- `SAML_DEFAULT_ROLE`: Default role for new SAML users (Gamma/Alpha/Admin)

### Auto-Initialization Enhanced (v1.0.0)

The enhanced entrypoint script automatically:
1. **Database Readiness**: Waits for MySQL database connectivity
2. **Schema Management**: Creates/upgrades database schema
3. **SAML Setup**: Configures SAML authentication when enabled  
4. **Admin User**: Creates admin user on first run
5. **Template Loading**: Registers custom SAML templates
6. **Service Startup**: Starts Superset with dual authentication support

## 🛠️ Development & Deployment

### Local Development

```bash
# Rebuild with SAML support 
docker build --no-cache . -t superset:1.0.1
docker-compose up -d

# View logs with SAML debug info
docker-compose logs -f superset | grep -E "(SAML|Auth)"

# Access container for debugging
docker exec -it superset bash
```

### Production Deployment

#### Docker Compose
Update `docker-compose.yml` with production settings:

```yaml
version: '3.8'
services:
  superset:
    image: superset:1.0.1
    environment:
      - ENABLE_SAML_AUTH=true
      - SAML_SP_ENTITY_ID=https://superset.yourcompany.com  
      - SUPERSET_ENV=production
```

#### Kubernetes with Helm
Use the included Helm templates in the `k8s/` directory:

```bash
helm install superset ./k8s/superset-helm \
  --set image.tag=1.0.1 \
  --set saml.enabled=true \
  --set saml.idpEntityId=https://sts.windows.net/your-tenant/
```

## 🔗 Database Integration

Enhanced MySQL integration with SAML authentication support:

- **Dual Drivers**: Both `mysqlclient` and `PyMySQL` for maximum compatibility
- **Connection Validation**: Automatic MySQL connection health checks
- **Performance Optimization**: Optimized engine options for MySQL  
- **Cloud Support**: Azure MySQL, AWS RDS, Google Cloud SQL compatibility
- **SAML User Storage**: Seamless user provisioning in MySQL backend

### Connection String Format

```bash
# Standard MySQL
DATABASE_URL=mysql://username:password@host:port/database

# Azure MySQL (with SSL) 
DATABASE_URL=mysql://username:password@host:port/database?ssl_mode=REQUIRED

# Production with connection pooling
DATABASE_URL=mysql://username:password@host:port/database?charset=utf8&pool_size=10&max_overflow=20
```

## 🚨 Troubleshooting

### SAML Authentication Issues (v1.0.0)

**SAML Login Not Working:**
1. Verify `ENABLE_SAML_AUTH=true` in `.env`
2. Check Azure AD application configuration
3. Validate certificate format (no line breaks in .env)
4. Enable SAML debug: `SAML_DEBUG=true`

**Azure AD Configuration:**
```bash
# Check SAML logs
docker-compose logs superset | grep -i saml

# Verify SAML configuration
docker exec superset cat /app/superset_config.py | grep -A 20 "SAML"
```

### Logout & Session Issues

**403 Forbidden Errors in Multiple Tabs (SOLVED):**
- ✅ **Fixed in v1.0.1** - Enhanced logout automatically coordinates all tabs
- ✅ **No manual cache clearing** required anymore
- ✅ **All tabs redirect automatically** when user logs out

**Logout Not Working Properly:**
1. Check logout configuration: `SAML_FORCE_LOCAL_LOGOUT=true` (recommended)
2. Verify browser supports BroadcastChannel (modern browsers do)
3. Check browser console for logout coordination logs
4. Test with different logout modes:
   ```bash
   # Local logout (preserves Azure AD session)
   SAML_FORCE_LOCAL_LOGOUT=true
   
   # Full SAML logout (logs out from Azure AD too)
   SAML_FORCE_LOCAL_LOGOUT=false
   ```

**Cache/Session Issues:**
```bash
# Check if comprehensive cache clearing is working
# 1. Login to Superset
# 2. Open browser DevTools > Application > Storage
# 3. Note localStorage, sessionStorage, cookies
# 4. Logout from Superset
# 5. Check that all auth-related storage is cleared
```

**User Provisioning Issues:**
- Check `SAML_DEFAULT_ROLE` setting  
- Verify user email format from Azure AD
- Ensure database connectivity for user creation

### General Issues  

**Database Connection Failed:**
- Verify MySQL credentials in `.env`
- Test connection: `mysql -h host -u user -p database`
- Check firewall settings for cloud databases
- Validate SSL requirements for Azure MySQL

**Image Build Issues:**
- Use `--no-cache` flag: `docker build --no-cache . -t superset:1.0.0`
- Ensure Docker has sufficient memory (4GB+ recommended)
- Check for template file changes requiring rebuild

**Environment Variables Not Loading:**
- Verify `.env` file format (no spaces around = signs)  
- Rebuild image after configuration changes
- Check for hidden characters in certificate strings

### Advanced Debugging

```bash
# Check SAML configuration inside container
docker exec superset python -c "
import os; 
print('SAML Enabled:', os.getenv('ENABLE_SAML_AUTH'));
print('IDP Entity:', os.getenv('SAML_IDP_ENTITY_ID')[:50]+'...')
"

# Validate MySQL connection
docker exec superset python -c "
from sqlalchemy import create_engine;
engine = create_engine(os.getenv('DATABASE_URL'));
print('DB Connection:', engine.execute('SELECT 1').scalar())
"

# Reset environment completely  
docker-compose down -v
rm -rf volumes/
docker rmi superset:1.0.0
docker build . -t superset:1.0.0
docker-compose up -d
```

## 🌟 Benefits of v1.0.0

### For Organizations
- **Enterprise SSO**: Seamless integration with existing Azure AD infrastructure
- **Security Compliance**: X.509 certificate-based authentication  
- **User Management**: Automatic user provisioning and role assignment
- **Flexibility**: Optional SAML - can disable for simpler setups

### For Developers  
- **Dual Authentication**: Database fallback for service accounts and testing
- **Easy Configuration**: Environment variable-based setup
- **Debug Support**: Comprehensive logging and troubleshooting tools
- **Template Customization**: Override login pages and authentication flows

### For DevOps
- **Container Ready**: Production-ready Docker image with SAML support
- **Kubernetes Support**: Helm charts with SAML environment variables  
- **Monitoring**: Enhanced logging for authentication events
- **Scalability**: Stateless SAML authentication for multi-instance deployments

## 📚 Documentation & Resources

### Project Resources
- **[GitHub Repository](https://github.com/JawadRafique/superset-with-docker-setup)** - Source code and issues
- **[Docker Hub](https://hub.docker.com/r/jawadrafique/superset:1.0.0)** - Ready-to-use container image
- **[SAML Demo Video](https://youtu.be/eUC1EElVgTo)** - Complete SAML authentication walkthrough
- **[Release Notes v1.0.0](./CHANGELOG.md)** - Detailed changes and migration guide

### Apache Superset Documentation  
- **[Official Documentation](https://superset.apache.org/docs/intro)** - Complete Superset guide
- **[Security Configuration](https://superset.apache.org/docs/security/)** - Security best practices
- **[Database Connections](https://superset.apache.org/docs/databases/mysql)** - MySQL setup guide

### SAML Integration References
- **[OneLogin SAML Python](https://github.com/onelogin/python3-saml)** - SAML library documentation  
- **[Azure AD SAML](https://docs.microsoft.com/en-us/azure/active-directory/saml-claims-customization)** - Azure AD SAML setup
- **[Flask-AppBuilder Security](https://flask-appbuilder.readthedocs.io/en/latest/security.html)** - Authentication framework

## 📄 License

This project is **free to use** and licensed under the **MIT License**.

✅ **Free for personal and commercial use**  
✅ **No restrictions on modification and distribution**  
✅ **Open source and community-driven**

## 👨‍💻 Author

**Muhammad Jawad**  
🌐 **Portfolio**: [https://ijawadrafique.com/](https://ijawadrafique.com/)  
☕ **Support**: [Buy me a coffee](http://buymeacoffee.com/m.jawad)

## 🤝 Contributing  

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### 💖 Support the Project

If this project helped you, consider supporting its development:

[![Buy Me A Coffee](https://img.shields.io/badge/☕-Buy%20me%20a%20coffee-yellow.svg)](http://buymeacoffee.com/m.jawad)

Your support helps maintain and improve this project!

---

**⚡ Version 1.0.0** - Production-ready Apache Superset with enhanced SAML authentication and Azure App Gateway support  
**🛡️ Production Ready** - Secure, scalable, and enterprise-friendly setup  
**📧 Support** - [Open an issue](https://github.com/JawadRafique/superset-with-docker-setup/issues) for support