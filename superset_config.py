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
WTF_CSRF_ENABLED = False
HTTP_HEADERS = {"X-Frame-Options": "ALLOWALL"}

# Custom logout handling - Add JavaScript to handle multi-tab logout coordination
EXTRA_CATEGORICAL_COLOR_SCHEMES = []

# Add global JavaScript for logout coordination
GLOBAL_ASYNC_QUERIES_ENABLED = True

# Custom cache settings to prevent authentication caching issues
SEND_FILE_MAX_AGE_DEFAULT = 60  # Cache static files for 1 minute only
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour session lifetime

# Add no-cache headers for authenticated pages
def add_no_cache_headers(response):
    """Add no-cache headers to prevent authentication caching issues"""
    if hasattr(response, 'headers'):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache' 
        response.headers['Expires'] = '0'
    return response

# Custom Jinja2 global functions
def setup_jinja_globals(app):
    """Setup custom Jinja2 global functions"""
    @app.template_global()
    def logout_script():
        """Generate logout coordination script"""
        return """
<script>
(function() {
    // Handle logout coordination between tabs
    if (typeof BroadcastChannel !== 'undefined') {
        const channel = new BroadcastChannel('superset-logout');
        channel.addEventListener('message', function(event) {
            if (event.data.type === 'LOGOUT') {
                window.location.href = '/login/';
            }
        });
    }
    
    // Fallback: localStorage listener
    window.addEventListener('storage', function(e) {
        if (e.key === 'superset-logout-event') {
            window.location.href = '/login/';
        }
    });
    
    // Handle session expiry
    setInterval(function() {
        fetch('/api/v1/security/current_user/', {
            credentials: 'include',
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        }).then(function(response) {
            if (response.status === 401 || response.status === 403) {
                // Session expired or forbidden
                window.location.href = '/login/';
            }
        }).catch(function() {
            // Network error or other issues - check if we're still authenticated
            // Don't redirect immediately, but check again later
        });
    }, 30000); // Check every 30 seconds
})();
</script>
        """.strip()

FEATURE_FLAGS = {
    "EMBEDDED_SUPERSET": True,
    "ENABLE_TEMPLATE_PROCESSING": True,
    "DASHBOARD_RBAC": True,
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