# 🚀 Deployment Guide - AIModelHub

Reorganization of `CatalogModelIA_DS` with separated logic and UI. This guide explains how to deploy the IA Assets Catalog with the new structure.

---

## 📋 Prerequisites

| Component | Minimum Version | Check |
|-----------|-----------------|-------|
| **Docker** | 20.10+ | `docker --version` |
| **Node.js** | 18+ | `node --version` |
| **npm** | 9+ | `npm --version` |
| **Git** | 2.0+ | `git --version` |

Recommended resources:
- CPU: 2 cores
- RAM: 4 GB
- Disk: 10 GB free

---

## ⚡ Automated Deployment (Recommended)

### Option 1: Single Script

```bash
# 1. Go to the project
cd AIModelHub

# 2. Run the deployment script
./deploy.sh   # Ensure you can use Docker (user in docker group or sudo)
```

The script automatically:
- ✅ Checks dependencies
- ✅ Stops existing services
- ✅ Starts PostgreSQL + MinIO in Docker
- ✅ Restores the full database (schema + data)
- ✅ Configures the MinIO bucket
- ✅ Installs npm dependencies
- ✅ Starts backend (EDC + API)
- ✅ Starts frontend (Angular)

Estimated time: 3-5 minutes

---

## 🔧 Manual Deployment

### Step 1: Enter the project

```bash
cd AIModelHub
```

### Step 2: Start Docker infrastructure

```bash
# PostgreSQL
docker run -d \
  --name ml-assets-postgres \
  -e POSTGRES_USER=ml_assets_user \
  -e POSTGRES_PASSWORD=ml_assets_password \
  -e POSTGRES_DB=ml_assets_db \
  -p 5432:5432 \
  -v ml-assets-postgres-data:/var/lib/postgresql/data \
  postgres:16-alpine

# MinIO S3
docker run -d \
  --name ml-assets-minio \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin123 \
  -p 9000:9000 -p 9001:9001 \
  -v ml-assets-minio-data:/data \
  minio/minio:latest server /data --console-address ":9001"
```

### Step 3: Initialize the database

**Option A: With sample data (recommended)**
```bash
docker exec -i ml-assets-postgres psql -U ml_assets_user -d ml_assets_db \
  < AIModelHub_Extensiones/database/full-backup.sql
```

Includes:
- 2 users (user1123, user2123)
- 13 IA assets
- 10 ML metadata records

**Option B: Schema only**
```bash
docker exec -i ml-assets-postgres psql -U ml_assets_user -d ml_assets_db \
  < AIModelHub_Extensiones/database/init-database.sql
```

### Step 4: Configure MinIO

```bash
# Create bucket
docker exec ml-assets-minio mkdir -p /data/ml-assets
```

### Step 5: Install dependencies

```bash
# Backend
cd AIModelHub_Extensiones/backend
npm install

# Frontend
cd ../../AIModelHub_EDCUI/ml-browser-app
npm install
```

### Step 6: Start services

**Terminal 1 - Backend:**
```bash
cd AIModelHub_Extensiones/backend
node src/server-edc.js
```

**Terminal 2 - Frontend:**
```bash
cd AIModelHub_EDCUI/ml-browser-app
npm run start
```

> ℹ️ Note: Health checks against `localhost` (for example `curl http://localhost:3000/health`) may require elevated permissions if your environment restricts local calls.

---

## 🌐 URLs and Credentials

### Services

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:4200 | Angular application |
| **Backend API** | http://localhost:3000 | EDC + Management API |
| **MinIO Console** | http://localhost:9001 | MinIO web console |
| **PostgreSQL** | localhost:5432 | Database |

### Default credentials

**Web application:**
```
User: user-conn-user1-demo
Password: user1123

User: user-conn-user2-demo  
Password: user2123
```

**MinIO:**
```
User: minioadmin
Password: minioadmin123
```

**PostgreSQL:**
```
User: ml_assets_user
Password: ml_assets_password
Database: ml_assets_db
```

---

## ✅ Verification

### 1. Check Docker containers

```bash
docker ps | grep ml-assets
```

Should show two containers: `ml-assets-postgres` and `ml-assets-minio`.

### 2. Check database

```bash
docker exec ml-assets-postgres psql -U ml_assets_user -d ml_assets_db -c "\dt"
```

Should show 9 tables.

### 3. Check backend

```bash
curl http://localhost:3000/v3/assets
```

Should return JSON with assets.

### 4. Check frontend

Open http://localhost:4200 in the browser. The application should load.

### 5. Login test

1. Go to http://localhost:4200  
2. Login with `user-conn-user1-demo` / `user1123`  
3. You should reach the assets catalog

---

## 📦 Key File Structure

```
AIModelHub/
├── deploy.sh                           # Automated deployment script
├── AIModelHub_Extensiones/
│   ├── backend/                        # EDC backend + API
│   ├── database/                       # SQL scripts (init, backup)
│   ├── docker-compose.yml              # Postgres + MinIO
│   └── model-server/                   # Model HTTP server (Python)
├── AIModelHub_EDCUI/
│   └── ml-browser-app/                 # Angular frontend
│       ├── src/                        # Angular source
│       └── package.json                # Frontend dependencies
├── CREDENTIALS.md                      # All credentials
└── DEPLOYMENT.md
```

---

## 🔄 Backup and Restore

### Create full backup

```bash
# Database backup with data
docker exec ml-assets-postgres pg_dump -U ml_assets_user -d ml_assets_db \
  --clean --if-exists --inserts > backup-$(date +%Y%m%d).sql

# MinIO files backup
docker exec ml-assets-minio tar czf /tmp/minio-backup.tar.gz /data/ml-assets
docker cp ml-assets-minio:/tmp/minio-backup.tar.gz ./
```

### Restore backup

```bash
# Restore database
docker exec -i ml-assets-postgres psql -U ml_assets_user -d ml_assets_db \
  < backup-20251212.sql

# Restore MinIO files
docker cp minio-backup.tar.gz ml-assets-minio:/tmp/
docker exec ml-assets-minio tar xzf /tmp/minio-backup.tar.gz -C /
```

---

## 🛑 Stop services

```bash
# Stop applications (if you used deploy.sh)
kill $(pgrep -f "server-edc.js")
kill $(pgrep -f "ng serve")

# Stop Docker
docker stop ml-assets-postgres ml-assets-minio

# Remove containers (keep data)
docker rm ml-assets-postgres ml-assets-minio

# Remove everything including data (CAUTION)
docker rm -f ml-assets-postgres ml-assets-minio
docker volume rm ml-assets-postgres-data ml-assets-minio-data
```

---

## 🐛 Troubleshooting

### Error: "Port 5432 in use"

```bash
# See which process uses the port
sudo lsof -i :5432

# Change port in deploy.sh or docker command
-p 5433:5432  # use 5433 on host
```

### Error: "Cannot connect to database"

```bash
# Check PostgreSQL readiness
docker exec ml-assets-postgres pg_isready -U ml_assets_user

# View logs
docker logs ml-assets-postgres
```

### Error: "Frontend does not compile"

```bash
# Clean npm cache
cd AIModelHub_EDCUI/ml-browser-app
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version  # should be 18+
```

### Error: "Backend does not start"

```bash
# View logs
cat AIModelHub_Extensiones/backend/server.log

# Check PostgreSQL is running
docker ps | grep postgres

# Test manual connection
docker exec -it ml-assets-postgres psql -U ml_assets_user -d ml_assets_db
```

---

## 🔐 Production security

Default credentials are for development. In production:

1. Change database passwords.
2. Change MinIO passwords.
3. Rotate web users and API keys.
4. Use environment variables or a secrets manager.
