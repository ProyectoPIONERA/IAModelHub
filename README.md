# AIModelHub

AI model management platform with an EDC-style runtime in Node.js and an Angular frontend to explore, register, and operate IA assets with S3 storage and rich metadata.

## Project status

First functional delivery of the AI model lifecycle for data spaces: it already supports registering and discovering models, creating EDC-style policies and contracts, and enabling negotiations between providers and consumers for service-based usage or direct download from S3 storage. The next phase will add model execution and evaluation within the data space to complete comparison and scoring.

## Contents

- Overview and features
- Repository structure
- Requirements and dependencies
- Installation and build
- Usage with examples
- Contribution
- Acknowledgments and funding
- Authors and license

## Main features

- EDC-compatible backend in Node.js with modular extensions (asset management, ML metadata, S3, authentication).
- Angular 17 frontend for browsing, creating, and detailing assets.
- PostgreSQL + MinIO S3 for metadata and artifacts.
- Ready-to-use scripts for local deployment and sample data restore.

## Repository structure

```
AIModelHub/
├── deploy.sh                       # Automated deployment
├── AIModelHub_Extensiones/         # Logic and services (symlinks keep previous paths)
│   ├── runtime-edc-backend/        # EDC backend + API (symlink: backend)
│   ├── database-scripts/           # SQL init/backup (symlink: database)
│   ├── model-serving/              # Model HTTP server (symlink: model-server)
│   └── infra-docker/               # Docker Compose (symlink: docker-compose.yml)
├── AIModelHub_EDCUI/               # Interfaces
│   └── ui-model-browser/           # Angular UI (symlink: ml-browser-app)
├── DEPLOYMENT.md
└── README.md
```

## Requirements and dependencies

- Docker and Docker Compose (PostgreSQL + MinIO).
- Node.js 18+ and npm 10+.
- Python 3 (optional, for `model-serving`).

## Installation and build

```bash
# 1) Enter the project
cd AIModelHub

# 2) Automated deployment (requires Docker permissions)
./deploy.sh

# 3) Manual (equivalent result to ./deploy.sh)
# Infrastructure (PostgreSQL + MinIO)
cd AIModelHub_Extensiones
docker compose up -d

# Backend
cd runtime-edc-backend
npm install
nohup node src/server-edc.js > ../../backend.log 2>&1 &

# Frontend
cd ../../AIModelHub_EDCUI/ui-model-browser
npm install
nohup npm run start > ../../frontend.log 2>&1 &

# Verification
curl http://localhost:3000/health
```

## Usage with examples

- Backend health: `curl http://localhost:3000/health`
- List assets: `curl -X POST http://localhost:3000/v3/assets/request -H "Authorization: Bearer <token>"`
- Frontend: open `http://localhost:4200`
  - User 1: `user-conn-user1-demo / user1123`
  - User 2: `user-conn-user2-demo / user2123`
- MinIO Console: `http://localhost:9001` (`minioadmin/minioadmin123`).

## Contribution

1. Open an issue with a clear description.
2. Fork and create a branch (`feature/...` or `fix/...`).
3. Submit a pull request with summary, test steps, and impact checklist.

## Acknowledgments and funding

- Inspired by Eclipse Dataspace Components (EDC): extensions of this architecture to apply it to any data space.
- Base technologies: Angular for UI, Express/Node.js for services, PostgreSQL for metadata, MinIO for S3 artifacts.

## Funding

This work has received funding from the PIONERA project (Enhancing interoperability in data spaces through artificial intelligence), a project funded in the context of the call for Technological Products and Services for Data Spaces of the Ministry for Digital Transformation and Public Administration within the framework of the PRTR funded by the European Union (NextGenerationEU)

<div align="center">
  <img src="funding_label.png" alt="Logos financiación" width="900" />
</div>

## Authors and contact

- Maintainers: Edmundo Mori, Jiayun Liu.
- Contact: edmundo.mori.orrillo@upm.es, jiayun.liu@alumnos.upm.es.

## License

Mapping Editor is available under the **[Apache License 2.0](https://github.com/ProyectoPIONERA/AIModelHub/blob/main/LICENSE)**.
