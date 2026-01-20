"""
Custom SAML Security Manager for Apache Superset
Provides SAML authentication with database fallback capability
Based on successful GitHub examples for dual authentication
"""
import os
import logging
from flask import redirect, url_for, flash, request, g, session
from flask_login import login_user
from flask_appbuilder.security.views import AuthDBView
from flask_appbuilder.views import expose
from flask_appbuilder.security.decorators import no_cache
from flask_appbuilder.security.forms import LoginForm_db
from flask_appbuilder._compat import as_unicode
from flask_appbuilder.utils.base import get_safe_redirect
from superset.security import SupersetSecurityManager
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from werkzeug.wrappers import Response as WerkzeugResponse
from typing import Optional

logger = logging.getLogger(__name__)


def init_saml_auth(req):
    """Initialize SAML Auth from environment variables"""
    
    # Build SAML settings from environment variables
    settings = {
        "strict": os.environ.get('SAML_STRICT', 'true').lower() == 'true',
        "debug": os.environ.get('SAML_DEBUG', 'false').lower() == 'true',
        "sp": {
            "entityId": os.environ.get('SAML_SP_ENTITY_ID', 'https://your-superset-domain.com'),
            "assertionConsumerService": {
                "url": os.environ.get('SAML_SP_ACS_URL', 'https://your-superset-domain.com/login/saml'),
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            },
            "singleLogoutService": {
                "url": os.environ.get('SAML_SP_SLS_URL', 'https://your-superset-domain.com/logout'),
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            "NameIDFormat": os.environ.get('SAML_SP_NAMEID_FORMAT', 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress'),
            "x509cert": os.environ.get('SAML_SP_X509_CERT', ''),
            "privateKey": os.environ.get('SAML_SP_PRIVATE_KEY', '')
        },
        "idp": {
            "entityId": os.environ.get('SAML_IDP_ENTITY_ID', ''),
            "singleSignOnService": {
                "url": os.environ.get('SAML_IDP_SSO_URL', ''),
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            "singleLogoutService": {
                "url": os.environ.get('SAML_IDP_SLO_URL', ''),
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            "x509cert": os.environ.get('SAML_IDP_X509_CERT', '')
        }
    }
    
    auth = OneLogin_Saml2_Auth(req, settings)
    return auth


def prepare_flask_request(request):
    """Prepare Flask request for SAML"""
    url_data = request.url.split('/')
    return {
        'https': 'on' if request.scheme == 'https' else 'off',
        'http_host': request.host,
        'server_port': url_data[2].split(':')[1] if ':' in url_data[2] else ('443' if request.scheme == 'https' else '80'),
        'script_name': request.path,
        'get_data': request.args.copy(),
        'post_data': request.form.copy()
    }


class CustomSamlAuthView(AuthDBView):
    """Custom Auth View for SAML with Database Auth fallback"""
    login_template = "appbuilder/general/security/login_db.html"
    
    @expose('/login/', methods=['GET', 'POST'])
    @no_cache
    def login(self):
        """Handle both SAML and database authentication"""
        logger.info(f"🔍 CustomSamlAuthView.login() called!")
        logger.info(f"🔍 Request method: {request.method}")
        logger.info(f"🔍 Request args: {dict(request.args)}")
        
        # If user is already authenticated, redirect to index
        if g.user is not None and g.user.is_authenticated:
            return redirect(self.appbuilder.get_url_for_index)
        
        # Handle SAML login request
        if 'saml' in request.args and request.args.get('saml') == 'true':
            logger.info("🚀 SAML login requested")
            return self._handle_saml_login()
        
        # Handle SAML ACS callback
        if request.method == 'POST' and 'SAMLResponse' in request.form:
            logger.info("📥 SAML Response received")
            # Bypass CSRF for SAML responses from external providers
            if hasattr(g, 'csrf_token'):
                g.csrf_token = None
            return self._handle_saml_response()
        
        # For GET requests or database login, show our custom template
        if request.method == 'GET':
            logger.info("📄 Showing custom SAML + database login form")
            form = LoginForm_db()
            return self.render_template(
                self.login_template,
                form=form,
                title='Superset Login',
                appbuilder=self.appbuilder,
                saml_enabled=os.environ.get('ENABLE_SAML_AUTH', 'true').lower() == 'true'
            )
        
        # For POST requests (database login), call parent method
        logger.info("🔐 Processing database login")
        return super().login()
    
    def _handle_saml_login(self):
        """Handle SAML authentication request"""
        try:
            # Check if SAML is enabled
            saml_enabled = os.environ.get('ENABLE_SAML_AUTH', 'true').lower() == 'true'
            if not saml_enabled:
                flash("SAML authentication is disabled", "warning")
                return redirect('/login/')
            
            req = prepare_flask_request(request)
            auth = init_saml_auth(req)
            return redirect(auth.login())
            
        except Exception as e:
            logger.error(f"❌ SAML request error: {e}")
            flash(f"SAML authentication error: {e}", "danger")
            return redirect('/login/')
    
    def _handle_saml_response(self):
        """Handle SAML authentication response"""
        try:
            req = prepare_flask_request(request)
            auth = init_saml_auth(req)
            auth.process_response()
            
            errors = auth.get_errors()
            if len(errors) == 0:
                session['samlUserdata'] = auth.get_attributes()
                session['samlNameId'] = auth.get_nameid()
                session['samlNameIdFormat'] = auth.get_nameid_format()
                session['samlSessionIndex'] = auth.get_session_index()
                
                # Create or update user
                user = self._auth_user_saml(auth)
                if user:
                    logger.info(f"✅ SAML user authenticated: {user.username}")
                    return redirect(self.appbuilder.get_url_for_index)
                else:
                    flash('Could not create user from SAML response', 'danger')
            else:
                logger.error(f"❌ SAML errors: {auth.get_last_error_reason()}")
                flash(f'SAML authentication failed: {auth.get_last_error_reason()}', 'danger')
                
        except Exception as e:
            logger.error(f"❌ SAML response processing error: {e}")
            flash(f'SAML processing error: {e}', 'danger')
            
        return redirect('/login/')
    
    def _auth_user_saml(self, saml_auth):
        """Create or update user from SAML attributes"""
        try:
            userdata = saml_auth.get_attributes()
            nameid = saml_auth.get_nameid()
            
            # Extract user information from SAML response
            email = nameid  # Usually email from Azure AD
            first_name = userdata.get('http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname', [email.split('@')[0]])[0]
            last_name = userdata.get('http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname', ['User'])[0]
            username = email.split('@')[0]  # Use email prefix as username
            
            # Find or create user
            user = self.appbuilder.sm.find_user(email=email)
            if not user:
                user = self.appbuilder.sm.add_user(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    role=self.appbuilder.sm.find_role(os.environ.get('SAML_DEFAULT_ROLE', 'Gamma'))
                )
                logger.info(f"✅ Created new SAML user: {username}")
            else:
                logger.info(f"✅ Found existing SAML user: {username}")
                
            # Login the user
            login_user(user, remember=False)
            return user
            
        except Exception as e:
            logger.error(f"❌ Error authenticating SAML user: {e}")
            return None


class SamlSecurityManager(SupersetSecurityManager):
    """Custom Security Manager with SAML support"""
    
    # Use authdbview for database-style authentication (includes our custom login)
    authdbview = CustomSamlAuthView
    
    def __init__(self, appbuilder):
        super(SamlSecurityManager, self).__init__(appbuilder)
        logger.info("🔧 SAML Security Manager initialized with CustomSamlAuthView")
        
        # Add custom template directory to Jinja2 loader
        try:
            appbuilder.app.jinja_loader.searchpath.append('/app/pythonpath/templates')
            logger.info("✅ Added custom template directory to Jinja2 loader")
        except Exception as e:
            logger.warning(f"⚠️ Could not add template directory: {e}")


# Export for use in superset_config.py
__all__ = ['SamlSecurityManager']