# Nessie + Dremio + Spark Cluster

Complete data lakehouse platform combining Apache Spark, Project Nessie (versioned metadata), Apache Iceberg (ACID tables), Dremio (SQL query engine) and MinIO (S3-compatible storage). This architecture provides a modern lakehouse with version control for data.

## Architecture

| Service | Description | Port(s) |
|---------|-------------|---------|
| **spark-master** | Spark Master node for distributed computing | `8080` (UI), `7077` (RPC) |
| **spark-worker-1/2/3** | 3 Spark Worker nodes for parallel execution | `8081-8083` (UI) |
| **nessie** | Project Nessie - versioned metadata catalog | `19120` |
| **dremio** | Dremio OSS - SQL query engine for Iceberg | `9047` (UI), `31010`, `45678` |
| **minio** | S3-compatible object storage (warehouse) | `9000` (API), `9001` (Console) |
| **postgres** | PostgreSQL - persistence for Nessie metadata | `5432` |

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) ≥ 24.0
- [Docker Compose](https://docs.docker.com/compose/install/) ≥ 2.20
- At least **8 GB RAM** allocated to Docker

## Quick Start

### 1. Clone and Configure

```bash
# Navigate to project directory
cd nessie-dremio-spark

# Create environment file if not exists
cp .env.example .env

# (Optional) Edit .env for custom configuration
```

### 2. Start the Cluster

```bash
# Start all services in the background
make up

# Follow logs to ensure healthy startup
make logs
```

> **Note:** On first run, services may take 2-3 minutes to initialize. Watch logs until all services are healthy.

### 3. Verify Cluster Health

```bash
# Check service status
make status

# Expected output:
# CONTAINER ID   IMAGE                          COMMAND                  STATUS
# xxxxx          postgres:17.5-alpine           "postgres"               Up X min (healthy)
# xxxxx          quay.io/minio/minio:...        "server /data ..."       Up X min (healthy)
# xxxxx          projectnessie/nessie:latest    "..."                    Up X min (healthy)
# xxxxx          apache/spark:3.5.0             "/opt/spark/bin/..."     Up X min (healthy)
# xxxxx          apache/spark:3.5.0             "/opt/spark/bin/..."     Up X min (healthy)
# xxxxx          apache/spark:3.5.0             "/opt/spark/bin/..."     Up X min (healthy)
# xxxxx          apache/spark:3.5.0             "/opt/spark/bin/..."     Up X min (healthy)
# xxxxx          dremio/dremio-oss:latest       "..."                    Up X min (healthy)
```

## Common Operations

```bash
make up              # Start cluster in background
make down            # Stop all services
make restart         # Restart cluster
make logs            # Follow all service logs (Ctrl+C to exit)
make reset           # Stop, remove volumes and restart fresh
make status          # Show running container status
make shell           # Open bash shell in Spark Master
make clean           # Clean Python cache and logs
```

## Service URLs & Access

| Service | URL | Credentials |
|---------|-----|-------------|
| **Spark Master UI** | http://localhost:8080 | — |
| **Spark Worker 1** | http://localhost:8081 | — |
| **Spark Worker 2** | http://localhost:8082 | — |
| **Spark Worker 3** | http://localhost:8083 | — |
| **Dremio Console** | http://localhost:9047 | `dremio` / `dremio123` |
| **Nessie API** | http://localhost:19120/api/v2 | — |
| **MinIO Console** | http://localhost:9001 | `minioadmin` / `minioadmin` |
| **PostgreSQL** | `localhost:5432` | `postgres` / `postgres123` |

## Project Structure

```
.
├── .env                            # Environment variables (create from .env.example)
├── .env.example                    # Environment template
├── docker-compose.yaml             # Docker Compose service definitions
├── Makefile                        # Common make targets
│
├── spark/
│   ├── config/
│   │   ├── spark-defaults.conf     # Spark cluster config (Nessie/Iceberg/MinIO)
│   │   ├── spark-env.sh            # Spark environment variables
│   │   └── log4j2.properties       # Logging configuration
│   │
│   └── jobs/
│       ├── hello_nessie.py         # Test job - verify Nessie connectivity
│       └── sample_etl.py           # Example ETL creating Iceberg tables
│
├── dremio/
│   └── dremio.conf                 # Dremio configuration
│
├── .gitignore
└── README.md
```

## Configuration

### Spark Configuration

Edit `spark/config/spark-defaults.conf` to adjust:
- **Nessie Catalog URI**: `spark.sql.catalog.nessie.uri` (default: `http://nessie:19120/api/v2`)
- **MinIO/S3 Endpoint**: `spark.hadoop.fs.s3a.endpoint` (default: `http://minio:9000`)
- **Worker Memory**: Edit `docker-compose.yaml` `SPARK_WORKER_MEMORY` (default: 2G per worker)
- **Worker Cores**: Edit `docker-compose.yaml` `SPARK_WORKER_CORES` (default: 2 per worker)

### Environment Variables

Edit `.env` to customize:
- PostgreSQL credentials (`POSTGRES_USER`, `POSTGRES_PASSWORD`)
- MinIO credentials (`MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`)
- Service ports (`SPARK_MASTER_PORT`, `DREMIO_PORT`)
- Timezone (`TZ`)

### Nessie Configuration

Nessie is configured to:
- Use PostgreSQL for persistence (JDBC backend)
- Store data in MinIO S3 bucket `warehouse`
- Provide versioned catalog at `http://nessie:19120/api/v2`

### Dremio Setup

After starting the stack, access Dremio at http://localhost:9047:

1. **Initialize Dremio** (first login):
   - Username: `dremio`
   - Password: `dremio123`

2. **Add Nessie Data Source**:
   - Click "+" next to "Sources" in the left sidebar
   - Select "Nessie"
   - Configure:
     - **Name**: `nessie`
     - **Nessie URL**: `http://nessie:19120/api/v2`
     - **Warehouse Location**: `s3://warehouse`
     - **Access Key ID**: `minioadmin`
     - **Access Secret**: `minioadmin`
   - Test and Save

3. **Query Iceberg Tables**:
   - Once Nessie source is added, tables created by Spark appear automatically
   - Click on table to see schema, data and query history

## Running Spark Jobs

### Submit a Job Directly

```bash
# Execute a job from the jobs/ directory
docker exec spark-master spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  --conf spark.sql.catalog.nessie=org.apache.iceberg.spark.SparkCatalog \
  --conf spark.sql.catalog.nessie.catalog-impl=org.apache.iceberg.nessie.NessieCatalog \
  --conf spark.sql.catalog.nessie.uri=http://nessie:19120/api/v2 \
  --conf spark.sql.catalog.nessie.ref=main \
  --conf spark.sql.catalog.nessie.warehouse=s3://warehouse \
  --conf spark.sql.catalog.nessie.s3.endpoint=http://minio:9000 \
  --conf spark.sql.catalog.nessie.s3.access-key-id=minioadmin \
  --conf spark.sql.catalog.nessie.s3.secret-access-key=minioadmin \
  /opt/spark-apps/hello_nessie.py
```

Or using the pre-configured defaults (from `spark-defaults.conf`):

```bash
docker exec spark-master spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  /opt/spark-apps/hello_nessie.py
```

### Interactive Spark Shell

```bash
# Open PySpark REPL connected to cluster
docker exec -it spark-master pyspark \
  --master spark://spark-master:7077 \
  --conf spark.sql.catalog.nessie=org.apache.iceberg.spark.SparkCatalog \
  --conf spark.sql.catalog.nessie.catalog-impl=org.apache.iceberg.nessie.NessieCatalog \
  --conf spark.sql.catalog.nessie.uri=http://nessie:19120/api/v2 \
  --conf spark.sql.catalog.nessie.warehouse=s3://warehouse
```

Then in PySpark:
```python
# List Nessie branches
df = spark.sql("SELECT * FROM nessie.metadata.branches")
df.show()

# Create an Iceberg table
spark.sql("""
  CREATE TABLE nessie.main.my_table (
    id INT,
    name STRING,
    value DOUBLE
  ) USING iceberg
""")

# Query the table
spark.sql("SELECT * FROM nessie.main.my_table").show()
```

## Example: Creating Iceberg Tables

### Using Python/PySpark

Create `spark/jobs/my_etl.py`:

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
  .appName("MyETL") \
  .getOrCreate()

# Create sample data
data = [
  (1, "Alice", 100.0),
  (2, "Bob", 200.0),
  (3, "Charlie", 150.0),
]

df = spark.createDataFrame(data, ["id", "name", "value"])

# Write as Iceberg table in Nessie
df.writeTo("nessie.main.customers") \
  .using("iceberg") \
  .tableProperty("write.format.default", "parquet") \
  .mode("overwrite") \
  .create()

print("Table created: nessie.main.customers")

spark.stop()
```

Submit the job:
```bash
docker exec spark-master spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  /opt/spark-apps/my_etl.py
```

## Troubleshooting

### Services Not Starting

```bash
# Check logs for errors
make logs

# Restart specific service
docker-compose restart spark-master

# Full reset (removes volumes)
make reset
```

### Spark Workers Not Connecting

```bash
# Verify worker logs
docker logs spark-worker-1

# Check Spark Master UI - should show 3 workers
# http://localhost:8080
```

### Nessie Not Accessible

```bash
# Test Nessie API
curl http://localhost:19120/api/v2/config

# Check if PostgreSQL is running
docker exec postgres pg_isready -U postgres
```

### MinIO Data Not Visible in Dremio

1. Ensure MinIO is healthy: `curl http://localhost:9000`
2. Verify Nessie source credentials in Dremio
3. Check MinIO Console (http://localhost:9001) for `warehouse` bucket
4. Restart Dremio: `docker-compose restart dremio`

### Out of Memory

Increase Docker memory allocation and adjust worker resources:

```yaml
# In docker-compose.yaml
environment:
  SPARK_WORKER_MEMORY: 4G  # Increase from 2G
  SPARK_WORKER_CORES: 4    # Increase from 2
```

Then restart:
```bash
make reset
```

## Performance Tips

1. **Allocate sufficient memory**: Minimum 8GB, recommended 16GB for Docker
2. **Adjust worker count**: For heavier workloads, add more spark-worker services in docker-compose.yaml
3. **Optimize data format**: Use Parquet for better compression and query performance
4. **Partition large tables**: For tables > 1GB, use `write.target-file-size-bytes` property
5. **Use Nessie branching**: For testing, create isolated branches instead of modifying main

## Architecture Decisions

### Why This Stack?

- **Spark**: Native Iceberg support with optimistic locking (unlike dbt)
- **Nessie**: Git-like versioning for data with ACID guarantees
- **Iceberg**: Mature table format with schema evolution and time-travel
- **Dremio**: SQL layer without transaction conflicts
- **MinIO**: Self-hosted S3 alternative with no external dependencies

### Why Not dbt?

dbt is incompatible with Nessie due to transaction model mismatch. dbt sends sequential metadata operations that conflict with Nessie's optimistic locking. Spark handles Iceberg transactions natively without this issue.