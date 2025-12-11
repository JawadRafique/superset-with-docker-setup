# Use the official Apache Superset image as base
FROM apache/superset:5.0.0

USER root

# Install system dependencies for MySQL client (REQUIRED for mysqlclient)
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install ClickHouse drivers and MySQL driver using uv into the virtual environment
RUN . /app/.venv/bin/activate && \
    uv pip install \
    clickhouse-connect>=0.5.14 \
    mysqlclient==2.2.4

# Create custom entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Switch back to superset user
USER superset

# Set the working directory
WORKDIR /app

# Use custom entrypoint
CMD ["/app/entrypoint.sh"]