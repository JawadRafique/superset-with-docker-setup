# Use the official Apache Superset image as base
FROM apache/superset:5.0.0

USER root

# Install system dependencies for MySQL client (if needed)
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install ClickHouse drivers and MySQL driver using uv into the virtual environment
RUN . /app/.venv/bin/activate && \
    uv pip install \
    clickhouse-connect>=0.5.14 \
    pymysql>=1.0.2

# Switch back to superset user
USER superset

# Set the working directory
WORKDIR /app

CMD ["/app/docker/entrypoints/run-server.sh"]