# Use the official Apache Superset image as base
FROM apache/superset:5.0.0

USER root

# Install ClickHouse drivers using uv into the virtual environment
RUN . /app/.venv/bin/activate && \
    uv pip install \
    clickhouse-connect>=0.5.14

# Switch back to superset user
USER superset

# Set the working directory
WORKDIR /app

CMD ["/app/docker/entrypoints/run-server.sh"]