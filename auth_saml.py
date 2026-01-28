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
        },
        # Security settings - balance compatibility with security
        "security": {
            # Authentication Context Settings
            "requestedAuthnContext": False,  # Accept ANY authentication method from Azure AD
            
            # Signature and Encryption Settings (Enhanced Security)
            "signatureAlgorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
            "digestAlgorithm": "http://www.w3.org/2001/04/xmlenc#sha256",
            
            # Assertion Security (Configurable via environment)
            "wantAssertionsSigned": os.environ.get('SAML_WANT_ASSERTIONS_SIGNED', 'true').lower() == 'true',
            "wantNameId": True,  # Always require NameID for user identification
            "wantNameIdEncrypted": os.environ.get('SAML_WANT_NAMEID_ENCRYPTED', 'false').lower() == 'true',
            "wantAssertionsEncrypted": os.environ.get('SAML_WANT_ASSERTIONS_ENCRYPTED', 'false').lower() == 'true',
            
            # XML Validation and Metadata
            "wantXMLValidation": True,  # Always validate XML structure
            "signMetadata": os.environ.get('SAML_SIGN_METADATA', 'false').lower() == 'true',
            
            # Response Security
            "rejectUnsolicitedResponsesWithInResponseTo": True,  # Prevent replay attacks
            "allowRepeatAttributeName": False,  # Prevent attribute injection
            
            # Session Security  
            "authnRequestsSigned": os.environ.get('SAML_SIGN_REQUESTS', 'false').lower() == 'true',
            "logoutRequestSigned": os.environ.get('SAML_SIGN_LOGOUT', 'false').lower() == 'true',
            "logoutResponseSigned": os.environ.get('SAML_SIGN_LOGOUT', 'false').lower() == 'true',
            
            # Timing Security
            "clockSkew": 30,  # 30 second tolerance for clock differences
        }
    }
    
    auth = OneLogin_Saml2_Auth(req, settings)
    return auth


def prepare_flask_request(request):
    """Prepare Flask request for SAML - force HTTPS for Azure App Gateway SSL termination"""
    url_data = request.url.split('/')
    # Force HTTPS since Azure App Gateway terminates SSL and forwards HTTP internally
    return {
        'https': 'on',  # Always force HTTPS for SAML
        'http_host': request.host,
        'server_port': '443',  # Always use HTTPS port for SAML
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
        
        # Handle SAML ACS callback FIRST (before CSRF check)
        if request.method == 'POST' and 'SAMLResponse' in request.form:
            logger.info("📥 SAML Response received")
            # Temporarily disable CSRF validation for this SAML response only
            logger.info("🔓 Bypassing CSRF validation for SAML response from external provider")
            original_csrf_enabled = getattr(self.appbuilder.app.config, 'WTF_CSRF_ENABLED', True)
            self.appbuilder.app.config['WTF_CSRF_ENABLED'] = False
            try:
                result = self._handle_saml_response()
                return result
            finally:
                # Always re-enable CSRF protection
                self.appbuilder.app.config['WTF_CSRF_ENABLED'] = original_csrf_enabled
        
        # Handle SAML login request
        if 'saml' in request.args and request.args.get('saml') == 'true':
            logger.info("🚀 SAML login requested")
            return self._handle_saml_login()
        
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
    
    @expose('/acs', methods=['POST'])
    @no_cache
    def acs(self):
        """SAML Assertion Consumer Service - CSRF exempt endpoint"""
        logger.info("📥 SAML ACS endpoint called (CSRF exempt)")
        logger.info(f"🔍 Request method: {request.method}")
        logger.info(f"🔍 Request form keys: {list(request.form.keys())}")
        
        if 'SAMLResponse' in request.form:
            return self._handle_saml_response()
        else:
            logger.error("❌ No SAMLResponse in form data")
            flash('Invalid SAML response', 'danger')
            return redirect('/login/')
    
    @expose('/logout/', methods=['GET', 'POST'])
    @no_cache
    def logout(self):
        """Custom logout that handles both SAML and database users"""
        logger.info("🚪 CustomSamlAuthView.logout() called")
        
        # Check if we should perform SAML logout or just local logout
        force_local_logout = os.environ.get('SAML_FORCE_LOCAL_LOGOUT', 'true').lower() == 'true'
        
        # Check if user came from SAML authentication
        user_is_saml = session.get('samlNameId') is not None
        
        if user_is_saml and not force_local_logout:
            logger.info("🔄 SAML user - performing SAML logout (will logout from Azure AD)")
            return self._handle_saml_logout()
        else:
            logger.info("🏠 Performing local logout only (preserving Azure AD session)")
            return self._handle_local_logout()
    
    def _handle_saml_logout(self):
        """Handle SAML Single Logout - logs out from both Superset and Azure AD"""
        try:
            req = prepare_flask_request(request)
            auth = init_saml_auth(req)
            
            # Get the logout URL from Azure AD
            logout_url = auth.logout(
                name_id=session.get('samlNameId'),
                session_index=session.get('samlSessionIndex'),
                nid_format=session.get('samlNameIdFormat')
            )
            
            # Clear local session
            self._clear_user_session()
            
            # Call Flask-Login logout
            from flask_login import logout_user
            logout_user()
            
            logger.info("🔄 Redirecting to Azure AD for global logout")
            
            # Create response with cache clearing
            response = redirect(logout_url)
            self._clear_auth_cookies(response)
            self._add_cache_control_headers(response)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ SAML logout error: {e}")
            # Fallback to local logout if SAML logout fails
            flash('SAML logout failed, performing local logout', 'warning')
            return self._handle_local_logout()
    
    def _handle_local_logout(self):
        """Handle local logout only - logs out from Superset but preserves Azure AD session"""
        try:
            # Clear user session and logout from Superset
            self._clear_user_session()
            
            # Call parent logout (Flask-AppBuilder logout)
            from flask_login import logout_user
            logout_user()
            
            logger.info("✅ Local logout successful - Azure AD session preserved")
            
            # Check if this is an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # For AJAX requests, return JSON response
                from flask import jsonify
                response = jsonify({
                    'success': True,
                    'message': 'Logged out successfully',
                    'redirect': '/login/'
                })
                self._add_cache_control_headers(response)
                return response
            
            # For regular requests, show logout page with client-side cleanup
            response = self.render_template(
                'appbuilder/general/security/logout.html',
                message='You have been logged out of Superset. Your organization account session remains active.'
            )
            
            # Clear authentication cookies
            self._clear_auth_cookies(response)
            
            # Add cache control headers to prevent caching
            self._add_cache_control_headers(response)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Local logout error: {e}")
            # Force redirect to login even if logout fails
            response = redirect('/login/')
            self._clear_auth_cookies(response)
            self._add_cache_control_headers(response)
            return response
    
    def _clear_user_session(self):
        """Clear SAML-related session data"""
        logger.info("🧹 Clearing user session data")
        
        # Clear SAML session data
        saml_keys = ['samlUserdata', 'samlNameId', 'samlNameIdFormat', 'samlSessionIndex']
        for key in saml_keys:
            session.pop(key, None)
        
        # Clear Flask-Login session data
        flask_login_keys = ['_user_id', '_fresh', '_id']
        for key in flask_login_keys:
            session.pop(key, None)
            
        # Clear any Superset-specific session data
        superset_keys = ['_flashes', 'csrf_token']
        for key in superset_keys:
            session.pop(key, None)
    
    def _clear_auth_cookies(self, response):
        """Clear all authentication-related cookies"""
        logger.info("🍪 Clearing authentication cookies")
        
        # List of common authentication cookies to clear
        cookie_names = [
            'session',           # Flask session cookie
            'remember_token',    # Flask-Login remember me
            'csrf_token',        # CSRF token
            'superset_session',  # Superset session
            '_csrf',            # Alternative CSRF
            'auth_token',       # Generic auth token
        ]
        
        for cookie_name in cookie_names:
            response.set_cookie(
                cookie_name, 
                '',  # Empty value
                expires=0,  # Immediate expiry
                max_age=0,  # No max age
                path='/',   # Clear for all paths
                domain=None,  # Use default domain
                secure=False,  # Works for both HTTP and HTTPS
                httponly=True,  # Prevent JavaScript access
                samesite='Lax'  # CSRF protection
            )
    
    def _add_cache_control_headers(self, response):
        """Add headers to prevent caching of authenticated content"""
        logger.info("🚫 Adding cache control headers")
        
        # Prevent caching of the logout response
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        # Additional security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
    
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