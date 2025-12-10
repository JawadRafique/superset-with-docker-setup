# Use the official Apache Superset image as base
FROM apache/superset:5.0.0

USER root

# Install system dependencies for MySQL client (REQUIRED for mysqlclient)
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install MySQL driver using uv into the virtual environment
RUN . /app/.venv/bin/activate && \
    uv pip install \
    mysqlclient>=2.2.4

# Switch back to superset user
USER superset

# Set the working directory
WORKDIR /app

CMD ["/app/docker/entrypoints/run-server.sh"]