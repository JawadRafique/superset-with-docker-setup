import os

# Check if SAML is enabled before importing SAML components
ENABLE_SAML_AUTH = os.environ.get('ENABLE_SAML_AUTH', 'true').lower() == 'true'

# Conditionally import and configure SAML
if ENABLE_SAML_AUTH:
    from auth_saml import SamlSecurityManager
    # Enable SAML authentication with database fallback
    CUSTOM_SECURITY_MANAGER = SamlSecurityManager
    
    # Add custom template directory
    import jinja2
    FAB_TEMPLATE_LOADER = jinja2.ChoiceLoader([
        jinja2.FileSystemLoader('/app/pythonpath/templates'),
        jinja2.FileSystemLoader('/app/superset/templates')
    ])

AUTH_TYPE = 1  # AUTH_DB (allows both database and SAML auth)
AUTH_USER_REGISTRATION = True

# Configure default role for SAML users from environment
SAML_DEFAULT_ROLE = os.environ.get('SAML_DEFAULT_ROLE', 'Gamma')
AUTH_USER_REGISTRATION_ROLE = SAML_DEFAULT_ROLE

# Allow both SAML and database authentication
AUTH_ROLES_SYNC_AT_LOGIN = True  # Sync roles at login
AUTH_ROLES_MAPPING = {
    "Gamma": ["Gamma"],
    "Alpha": ["Alpha"], 
    "Admin": ["Admin"]
}

# Security settings
TALISMAN_ENABLED = False
# Keep CSRF enabled for security, we'll handle SAML exemption differently
WTF_CSRF_ENABLED = True  
# Exempt specific SAML endpoints from CSRF protection
WTF_CSRF_EXEMPT_LIST = [
    'CustomSamlAuthView.acs',  # Only SAML ACS endpoint
]
HTTP_HEADERS = {"X-Frame-Options": "ALLOWALL"}

FEATURE_FLAGS = {
    "EMBEDDED_SUPERSET": True,
    "ENABLE_TEMPLATE_PROCESSING": True,
}

# Allow CSS styling in templates
HTML_SANITIZATION_SCHEMA_EXTENSIONS = {
    "attributes": {
        "*": ["style", "className", "id"],
    },
    "tagNames": ["style"],
}

# Database configuration - read from environment
# MySQL is REQUIRED - fail fast if not configured properly
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or os.environ.get('SQLALCHEMY_DATABASE_URI')

if not SQLALCHEMY_DATABASE_URI:
    raise ValueError("❌ DATABASE_URL or SQLALCHEMY_DATABASE_URI environment variable is required!")

if 'mysql' not in SQLALCHEMY_DATABASE_URI:
    raise ValueError(f"❌ MySQL database required! Got: {SQLALCHEMY_DATABASE_URI}")

# Secret key configuration
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("❌ SECRET_KEY environment variable is required!")

# MySQL-specific engine options
if 'mysql' in SQLALCHEMY_DATABASE_URI:
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'echo': False
    }