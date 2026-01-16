# Use the official Apache Superset image as base
FROM apache/superset:5.0.0

USER root

# Install system dependencies for MySQL client and SAML support
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    libxml2-dev \
    libxmlsec1-dev \
    libxmlsec1-openssl \
    && rm -rf /var/lib/apt/lists/*

# Install ClickHouse drivers, MySQL driver, and SAML libraries using uv into the virtual environment
RUN . /app/.venv/bin/activate && \
    uv pip install \
    clickhouse-connect>=0.5.14 \
    mysqlclient==2.2.4 \
    python3-saml==1.16.0 \
    xmlsec==1.3.14 \
    lxml==5.2.1

# Create custom entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy SAML configuration files
COPY auth_saml.py /app/pythonpath/auth_saml.py

# Copy custom templates with correct directory structure
COPY templates/ /app/pythonpath/templates/

# Switch back to superset user
USER superset

# Set the working directory
WORKDIR /app

# Use custom entrypoint
CMD ["/app/entrypoint.sh"]