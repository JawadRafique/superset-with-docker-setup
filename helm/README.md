# Apache Superset Helm Chart

This Helm chart deploys Apache Superset to a Kubernetes cluster with auto-scaling capabilities.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- MySQL database (Azure MySQL or equivalent)
- Docker registry access for the Superset image

## Installation

### 1. Clone or download this chart

```bash
git clone <your-repo>
cd my-superset/helm
```

### 2. Configure values

Edit `values.yaml` or create a custom values file:

```yaml
# Example custom values
name: my-superset-app
superset:
  database:
    host: your-mysql-host
    database: your-database-name
    username: your-username
    password: your-password
```

### 3. Install the chart

```bash
# Install with default values
helm install my-superset .

# Install with custom values file
helm install my-superset . -f custom-values.yaml

# Install with inline overrides
helm install my-superset . \
  --set superset.database.host=your-host \
  --set superset.database.password=your-password
```

## Configuration

### Required Configuration

| Parameter | Description | Required |
|-----------|-------------|----------|
| `superset.database.host` | MySQL database hostname | Yes |
| `superset.database.database` | Database name | Yes |
| `superset.database.username` | Database username | Yes |
| `superset.database.password` | Database password | Yes |

### Optional Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `name` | Application name | `Application Name` |
| `namespace.name` | Kubernetes namespace | `superset` |
| `deployment.minreplicas` | Minimum number of replicas | `1` |
| `deployment.maxreplicas` | Maximum number of replicas | `3` |
| `deployment.cpuutilization` | CPU threshold for scaling | `70` |
| `deployment.memoryutilization` | Memory threshold for scaling | `80` |
| `superset.image.package` | Docker image name | `superset` |
| `superset.image.tag` | Docker image tag | `1.1.0` |
| `superset.port` | Application port | `8088` |

## Features

- **Auto-scaling**: Horizontal Pod Autoscaler based on CPU and memory usage
- **Custom Superset Image**: Uses `superset` with MySQL drivers and enhanced entrypoint
- **Database Integration**: MySQL database connection with configurable credentials
- **Admin User**: Automatic creation of admin user during initialization
- **NodePort Service**: Exposes Superset on a NodePort for external access

## Database Setup

Ensure your MySQL database has the required permissions:

```sql
-- Create database
CREATE DATABASE superset CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user and grant permissions
CREATE USER 'supersetuser'@'%' IDENTIFIED BY 'your-password';
GRANT ALL PRIVILEGES ON superset.* TO 'supersetuser'@'%';
FLUSH PRIVILEGES;
```

## Access

After installation, you can access Superset:

1. **Find the NodePort**:
   ```bash
   kubectl get service -n superset
   ```

2. **Get cluster node IP**:
   ```bash
   kubectl get nodes -o wide
   ```

3. **Access Superset**: `http://<node-ip>:<node-port>/dash`

4. **Default credentials**:
   - Username: `admin`
   - Password: `admin123`

## Upgrading

```bash
helm upgrade my-superset . -f your-values.yaml
```

## Uninstalling

```bash
helm uninstall my-superset
```

## Troubleshooting

### Pod Restart Loops

Check pod logs for database connection issues:

```bash
kubectl logs -n superset -l app=<name>-superset --follow
```

### Common Issues

1. **Database Connection**: Verify MySQL credentials and network connectivity
2. **Image Pull**: Ensure the Docker image is accessible from your cluster
3. **Resources**: Check if cluster has sufficient resources for scaling

### Database Permissions

The Superset image requires these MySQL privileges:
- `SELECT`, `INSERT`, `UPDATE`, `DELETE`
- `CREATE`, `DROP`, `ALTER`
- `INDEX`

Note: `REFERENCES` privilege is optional and handled gracefully if not available.

## Architecture

This chart deploys:
- **Deployment**: Superset application with configurable replicas
- **HPA**: Auto-scaling based on resource utilization
- **Service**: NodePort service for external access

The deployment uses a custom entrypoint that:
- Validates database connectivity
- Initializes Superset schema if needed
- Creates admin user automatically
- Handles graceful startup and error recovery