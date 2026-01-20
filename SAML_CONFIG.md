# SAML Configuration Guide for Apache Superset (v1.2.6)

🎥 **[Watch the SAML Demo Video](https://youtu.be/eUC1EElVgTo)** - Complete walkthrough of SAML authentication setup and testing!

This guide explains how to configure SAML authentication with Azure AD for your Apache Superset instance.

## 🆕 Version 1.2.6 Updates

### ✅ Production-Ready SAML Configuration
- **Complete certificate management** - Both SP and IdP certificates for full SAML compliance
- **Azure App Gateway compatibility** - Works with SSL termination and offloading
- **Enhanced signature validation** with proper error handling
- **Verified working setup** - Tested configuration with Azure AD integration

### 🔧 Enhanced SAML Features  
- **Azure App Gateway compatibility** - Works with SSL offloading
- **Updated Azure AD certificates** - Supports latest Azure AD signing certificates
- **Better error logging** - Enhanced debugging for SAML authentication issues
- **Complete SAML workflow** - Full SP and IdP certificate support

## Overview

The SAML integration includes:
- **auth_saml.py**: Custom security manager that handles SAML authentication
- **saml_settings.json**: SAML configuration for Service Provider (SP) and Identity Provider (IdP)
- Updated Dockerfile with required SAML libraries
- Modified superset_config.py to enable SAML authentication

## Azure ADFS Configuration

### 1. Create Enterprise Application in Azure

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **Enterprise Applications**
3. Click **+ New application**
4. Choose **Create your own application**
5. Name it "Apache Superset SAML"
6. Select "Integrate any other application you don't find in the gallery"

### 2. Configure Single Sign-On

1. In the application menu, go to **Single sign-on**
2. Choose **SAML**
3. Click **Edit** on **Basic SAML Configuration**

**Fill in these fields:**

```
Identifier (Entity ID): https://your-superset-domain.com
Reply URL (ACS URL): https://your-superset-domain.com/saml/login?acs
Sign on URL: https://your-superset-domain.com/login/
```

### 3. Get IdP Information

After saving the configuration, Azure will provide:

1. **Login URL** (Single Sign-On Service URL)
2. **Azure AD Identifier** (Entity ID)  
3. **Logout URL** (Single Logout Service URL)
4. **Certificate** (Base64 format)

## Superset Configuration

### 1. Configure Environment Variables

All SAML settings are now configured through environment variables in your [.env](.env) file:

#### Service Provider (SP) Configuration
Configure these variables for your Superset instance:

```bash
# Service Provider (SP) Configuration - Your Superset instance
SAML_SP_ENTITY_ID=https://your-superset-domain.com
SAML_SP_ACS_URL=https://your-superset-domain.com/saml/login?acs
SAML_SP_SLS_URL=https://your-superset-domain.com/saml/login?sls
SAML_SP_NAMEID_FORMAT=urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified
SAML_SP_X509_CERT=
SAML_SP_PRIVATE_KEY=
```

#### Identity Provider (IdP) Configuration
Configure these variables with your Azure ADFS information:

```bash
# Identity Provider (IdP) Configuration - Your Azure ADFS
SAML_IDP_ENTITY_ID=YOUR_AZURE_ADFS_ENTITY_ID
SAML_IDP_SSO_URL=YOUR_AZURE_ADFS_SSO_URL
SAML_IDP_SLS_URL=YOUR_AZURE_ADFS_SLS_URL
SAML_IDP_X509_CERT=YOUR_AZURE_ADFS_CERTIFICATE
```

#### General SAML Settings

```bash
# SAML Settings
SAML_STRICT=true
SAML_DEBUG=false
ENABLE_SAML_AUTH=true
SAML_DEFAULT_ROLE=Gamma
```

**Important Notes:**
- Replace `your-superset-domain.com` with your actual domain
- The certificate should be pasted **without** the `-----BEGIN CERTIFICATE-----` and `-----END CERTIFICATE-----` lines
- Remove any line breaks from the certificate

### 2. Environment Variable Reference

| Environment Variable | Description | Example |
|---------------------|-------------|---------|
| `SAML_SP_ENTITY_ID` | Your Superset URL (unique identifier) | `https://superset.company.com` |
| `SAML_SP_ACS_URL` | Where Superset receives SAML responses | `https://superset.company.com/saml/login?acs` |
| `SAML_SP_SLS_URL` | Logout endpoint | `https://superset.company.com/saml/login?sls` |
| `SAML_IDP_ENTITY_ID` | Azure AD Identifier from Azure portal | `https://sts.windows.net/abc123-...` |
| `SAML_IDP_SSO_URL` | Login URL from Azure portal | `https://login.microsoftonline.com/...` |
| `SAML_IDP_SLS_URL` | Logout URL from Azure portal | `https://login.microsoftonline.com/...` |
| `SAML_IDP_X509_CERT` | Certificate from Azure portal (base64, no headers) | Long string of characters |
| `SAML_STRICT` | Enable strict SAML validation | `true` or `false` |
| `SAML_DEBUG` | Enable SAML debug logging | `true` or `false` |

## User Attribute Mapping

The SAML integration maps these Azure AD attributes to Superset user fields:

| Azure AD Attribute | Superset Field |
|-------------------|----------------|
| `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name` | Username |
| `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress` | Email |
| `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname` | First Name |
| `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname` | Last Name |

## Build and Deploy

1. **Build the new Docker image:**
   ```bash
   docker build --no-cache -t jawad-superset:1.2.0 .
   ```

2. **Update docker-compose.yml:**
   ```yaml
   services:
     superset:
       image: jawad-superset:1.2.0
   ```

3. **Deploy:**
   ```bash
   docker-compose up -d
   ```

## Authentication Flow

1. User visits Superset URL
2. User is redirected to Azure ADFS login page
3. After successful authentication in Azure, user is redirected back to Superset
4. Superset processes the SAML response and creates/updates the user account
5. User is logged into Superset with their Azure identity

## Default User Role

New SAML users are assigned the "Gamma" role by default. You can change this in [superset_config.py](superset_config.py):

```python
AUTH_USER_REGISTRATION_ROLE = "Gamma"  # Change to "Alpha" or "Admin" if needed
```

## Troubleshooting

### Common Issues

1. **Certificate Issues**: Ensure the certificate is copied correctly without headers and line breaks
2. **URL Mismatches**: Verify all URLs in Azure and saml_settings.json match exactly
3. **Attribute Mapping**: Check Azure AD user attributes if user creation fails

### Debug Mode

To enable SAML debug logging, set `SAML_DEBUG=true` in your .env file and check Superset logs.

### Testing

1. Ensure all required environment variables are set in your .env file
2. Access your Superset URL
3. You should be automatically redirected to Azure ADFS
4. After authentication, you should be redirected back to Superset
5. Check Superset logs for any SAML-related errors

## Security Considerations

1. **HTTPS Required**: SAML should only be used over HTTPS in production
2. **Certificate Validation**: Keep Azure AD certificates up to date
3. **Session Security**: Configure appropriate session timeouts
4. **Attribute Verification**: Validate that user attributes are correctly mapped

## Dual Authentication Support

This configuration supports **both SAML and database authentication** simultaneously:

### Authentication Options

1. **SAML Authentication (Azure AD)**
   - Users click "Sign in with Azure AD" button
   - Redirected to Azure ADFS login page
   - Automatic user creation/updates from Azure AD attributes

2. **Database Authentication (Local)**
   - Users enter username/password directly
   - Existing admin users and local accounts
   - Useful for system administrators and service accounts

### Login Flow

1. User visits Superset login page
2. Two options are presented:
   - **"Sign in with Azure AD"** button (SAML)
   - Username/password form (Database)
3. Users can choose their preferred authentication method
4. Both methods lead to the same Superset dashboard

### Admin Access

- **SAML Users**: Automatically created with "Gamma" role by default
- **Database Users**: Existing admin users maintain their roles
- **Emergency Access**: Database authentication always available for admin users

The configuration allows both SAML and database authentication, ensuring flexibility and admin access.

---

For more information, refer to the [onelogin/python3-saml documentation](https://github.com/onelogin/python3-saml).