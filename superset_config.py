import os

TALISMAN_ENABLED = False
HTTP_HEADERS={"X-Frame-Options":"ALLOWALL"}

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