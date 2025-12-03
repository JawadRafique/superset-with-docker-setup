# My Superset Project

A comprehensive data analytics and visualization platform built with Apache Superset, integrated with multiple data sources and streaming capabilities.

## 🏗️ Architecture

This project provides a complete data stack including:

- **Apache Superset** - Modern data exploration and visualization platform
- **PostgreSQL** - Primary database for Superset metadata
- **ClickHouse** - High-performance columnar database for analytics
- **Apache Kafka** - Distributed streaming platform for real-time data
- **Kafka UI** - Web interface for Kafka cluster management

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 4GB of available RAM
- Ports 8088, 8123, 9000, 9092, 9094, and 8081 available

### 1. Clone and Setup

```bash
git clone https://github.com/JawadRafique/superset-with-docker-setup.git
cd superset-with-docker-setup
```

### 2. Start Services

```bash
docker-compose up -d
```

### 3. Access Applications

- **Superset Dashboard**: http://localhost:8088/dash
- **ClickHouse HTTP Interface**: http://localhost:8123
- **Kafka UI**: http://localhost:8081

### 4. Default Credentials

**Superset Admin:**
- Username: `admin`
- Password: `admin`
- Email: `admin@example.com`

**ClickHouse:**
- Database: `jawad`
- Username: `admin`
- Password: `password123`

**PostgreSQL:**
- Database: `superset`
- Username: `superset`
- Password: `superset`

## 📁 Project Structure

```
.
├── docker-compose.yml          # Main service orchestration
├── Dockerfile                  # Custom Superset image
├── superset_config.py          # Superset configuration
├── .gitignore                 # Git ignore rules
├── volumes/                   # Persistent data storage
│   ├── superset/             # Superset application data
│   ├── postgres/             # PostgreSQL data
│   ├── clickhouse-data/      # ClickHouse database files
│   └── clickhouse-logs/      # ClickHouse log files
└── README.md                 # This file
```

## 🔧 Configuration

### Superset Configuration

The Superset service is configured with:
- Development environment with examples loaded
- Custom configuration via `superset_config.py`
- Persistent storage in `./volumes/superset`
- Web server prefix: `/dash`

### ClickHouse Setup

ClickHouse is configured for high-performance analytics:
- HTTP interface on port 8123
- Native client interface on port 9000
- Custom database `jawad` with admin access
- Persistent data storage

### Kafka Configuration

Kafka runs in KRaft mode (no Zookeeper required):
- Internal communication on port 9092
- External client access on port 9094
- 3 default partitions for new topics
- Kafka UI for cluster management

## 🛠️ Development

### Building Custom Superset Image

If you need to customize the Superset image:

```bash
docker-compose build superset
```

### Accessing Services

**Enter Superset container:**
```bash
docker exec -it jawad-superset bash
```

**Enter ClickHouse container:**
```bash
docker exec -it jawad-clickhouse clickhouse-client
```

**View Kafka logs:**
```bash
docker logs jawad-Kafka
```

### Data Persistence

All service data is persisted in the `volumes/` directory:
- Superset application data and metadata
- PostgreSQL database files
- ClickHouse data and logs
- Volume mappings ensure data survives container restarts

## 🔗 Connecting Data Sources

### Adding ClickHouse to Superset

1. Access Superset at http://localhost:8088/dash
2. Go to Settings > Database Connections
3. Add new database with:
   - **Database**: ClickHouse
   - **SQLAlchemy URI**: `clickhouse+http://admin:password123@clickhouse:8123/jawad`

### Kafka Integration

Use Kafka for streaming data into ClickHouse or other data stores:
- Producer endpoint: `localhost:9094`
- Internal broker: `kafka:9092`
- Manage topics via Kafka UI at http://localhost:8081

## 📊 Sample Workflows

### 1. Stream Data with Kafka

```bash
# Create a topic
docker exec jawad-Kafka kafka-topics.sh --create \
  --topic user-events \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1

# Produce messages
docker exec -it jawad-Kafka kafka-console-producer.sh \
  --topic user-events \
  --bootstrap-server localhost:9092
```

### 2. Query ClickHouse

```sql
-- Connect to ClickHouse
-- Create a table for analytics
CREATE TABLE user_events (
    timestamp DateTime,
    user_id String,
    event_type String,
    properties String
) ENGINE = MergeTree()
ORDER BY (timestamp, user_id);
```

### 3. Create Superset Dashboards

1. Connect ClickHouse as a data source
2. Create datasets from your tables
3. Build charts and dashboards
4. Share with your team

## 🔍 Monitoring

### Health Checks

Check service status:
```bash
docker-compose ps
```

### Logs

View service logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f superset
docker-compose logs -f clickhouse
docker-compose logs -f kafka
```

### Resource Usage

Monitor resource consumption:
```bash
docker stats
```

## 🚨 Troubleshooting

### Common Issues

**Port Conflicts:**
- Ensure ports 8088, 8123, 9000, 9092, 9094, 8081 are available
- Modify port mappings in docker-compose.yml if needed

**Memory Issues:**
- ClickHouse requires sufficient memory for large datasets
- Increase Docker memory allocation if needed

**Kafka Connectivity:**
- Verify network connectivity between services
- Check `KAFKA_ADVERTISED_LISTENERS` configuration

### Reset Environment

To start fresh:
```bash
docker-compose down -v
rm -rf volumes/
docker-compose up -d
```

## 📚 Documentation

- [Apache Superset Documentation](https://superset.apache.org/docs/intro)
- [ClickHouse Documentation](https://clickhouse.com/docs)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Docker Compose Reference](https://docs.docker.com/compose/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

For questions and support:
- Create an issue in the repository
- Check the documentation links above
- Review Docker Compose logs for debugging

---

**Note**: This is a development setup. For production use, ensure proper security configurations, environment variables, and resource allocations.