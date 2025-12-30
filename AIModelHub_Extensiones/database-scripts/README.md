# Database Initialization

Scripts to initialize the PostgreSQL database for AIModelHub (reorganized CatalogModelIA_DS).

## 📋 Files
- **`init-database.sql`**: Full initialization script (recommended).
- **`schema.sql`**: Schema export for reference.
- **`generate-password-hash.js`**: Utility to generate bcrypt password hashes.

## 🚀 Quick use

### Option 1: Automatic with Docker Compose
If you use Docker Compose, the database initializes automatically when containers start.

### Option 2: Manual initialization
```bash
# 1. Create database
createdb -U postgres ml_assets_db
# 2. Create user
psql -U postgres -c "CREATE USER ml_assets_user WITH PASSWORD 'ml_assets_password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE ml_assets_db TO ml_assets_user;"
# 3. Run init script
psql -U ml_assets_user -d ml_assets_db -f init-database.sql
```

### Option 3: From Docker container
```bash
docker cp init-database.sql ml-assets-postgres:/tmp/
docker exec -it ml-assets-postgres psql -U ml_assets_user -d ml_assets_db -f /tmp/init-database.sql
```

## 🗄️ Tables (high level)
1. **users** - Authentication + multi-tenant connector
2. **assets** - Asset metadata and ownership (owner = connector_id)
3. **data_addresses** - Storage configuration
4. **ml_metadata** - ML-specific metadata
5. **contract_definitions** - Contract definition linking assets to policies
6. **policy_definitions** - EDC policies (ODRL)

Views / helpers:
- **`assets_with_owner`**: Assets with owner info
- **`update_updated_at_column()`**: Trigger to auto-update timestamps

## 🔑 Demo users
```
user-conn-user1-demo    / user1123
user-conn-user2-demo / user2123
```
⚠️ Change these in production.

### Change passwords
```bash
node generate-password-hash.js           # interactive
node generate-password-hash.js "MyNewPass123!"
# Update DB with the generated hash
```

## 🧪 Verification
After running the script:
```bash
psql -U ml_assets_user -d ml_assets_db -c "\dt"        # tables
psql -U ml_assets_user -d ml_assets_db -c "SELECT * FROM users;"
```

## 🐛 Troubleshooting
- Check PostgreSQL is running: `docker exec ml-assets-postgres pg_isready -U ml_assets_user`
- View logs: `docker logs ml-assets-postgres`

## 📚 More information
- See `../docker-compose.yml` for PostgreSQL configuration.
