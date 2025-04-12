# Litigation Simulator - Deployment Instructions

This document provides comprehensive instructions for deploying the Litigation Simulator application in both development and production environments.

## Prerequisites

Before deploying the application, ensure you have the following prerequisites installed and configured:

### Development Environment

- Python 3.10+
- Docker and Docker Compose
- Git
- Node.js 16+ and npm
- PostgreSQL 13+
- Redis 6+

### Production Environment

- AWS or Azure account with appropriate permissions
- Domain name (if deploying with HTTPS)
- Docker and Docker Compose (for container deployment)
- SSL certificate (for HTTPS)

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/litigation-simulator.git
cd litigation-simulator
```

### 2. Environment Configuration

Create the necessary environment files:

```bash
cp .env.example .env.dev
```

Edit `.env.dev` with appropriate values:

```
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=litigation_simulator
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

# Court Listener API
COURT_LISTENER_API_TOKEN=your_court_listener_api_token

# Application Settings
SECRET_KEY=your_secure_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Machine Learning Settings
MODEL_DIR=./models
```

### 3. Start Docker Services

Start all required services with Docker Compose:

```bash
docker compose -f docker-compose.dev.yml up -d
```

This will start the following services:
- PostgreSQL database
- Redis cache and queue
- FastAPI backend
- React frontend development server

### 4. Run Database Migrations

Apply database migrations:

```bash
docker compose -f docker-compose.dev.yml exec backend python -m alembic upgrade head
```

### 5. Create Admin User

Create an admin user for the application:

```bash
docker compose -f docker-compose.dev.yml exec backend python -m scripts.create_admin
```

### 6. Access the Application

The application should now be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Production Deployment

### Option 1: Kubernetes Deployment

#### 1. Kubernetes Configuration

Ensure you have a Kubernetes cluster set up and kubectl configured to connect to it.

#### 2. Create Kubernetes Secrets

```bash
kubectl create secret generic litigation-simulator-secrets \
  --from-literal=postgres-password=your_secure_password \
  --from-literal=redis-password=your_secure_redis_password \
  --from-literal=secret-key=your_secure_secret_key \
  --from-literal=court-listener-api-token=your_court_listener_api_token
```

#### 3. Apply Kubernetes Manifests

Apply the Kubernetes manifests:

```bash
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/configmap.yml
kubectl apply -f k8s/postgres.yml
kubectl apply -f k8s/redis.yml
kubectl apply -f k8s/backend.yml
kubectl apply -f k8s/frontend.yml
kubectl apply -f k8s/ingress.yml
```

#### 4. Verify Deployment

Verify all pods are running:

```bash
kubectl get pods -n litigation-simulator
```

The application should be accessible at the configured ingress URL.

### Option 2: Docker Compose Deployment

#### 1. Environment Configuration

Create the production environment file:

```bash
cp .env.example .env.prod
```

Edit `.env.prod` with production-specific values:

```
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_production_password
POSTGRES_DB=litigation_simulator
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_secure_redis_password

# Court Listener API
COURT_LISTENER_API_TOKEN=your_court_listener_api_token

# Application Settings
SECRET_KEY=your_secure_production_secret_key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
CORS_ALLOWED_ORIGINS=https://your-domain.com

# Machine Learning Settings
MODEL_DIR=/app/models
```

#### 2. Start Docker Services

Start all services in production mode:

```bash
docker compose -f docker-compose.prod.yml up -d
```

#### 3. Run Database Migrations

Apply database migrations:

```bash
docker compose -f docker-compose.prod.yml exec backend python -m alembic upgrade head
```

#### 4. Create Admin User

Create an admin user for the application:

```bash
docker compose -f docker-compose.prod.yml exec backend python -m scripts.create_admin
```

#### 5. Configure Nginx

If you're using Nginx as a reverse proxy, configure it to forward requests to the Docker services:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Option 3: AWS Deployment

#### 1. Create ECR Repositories

Create ECR repositories for backend and frontend images:

```bash
aws ecr create-repository --repository-name litigation-simulator-backend
aws ecr create-repository --repository-name litigation-simulator-frontend
```

#### 2. Build and Push Docker Images

Build and push Docker images to ECR:

```bash
# Login to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin your-aws-account-id.dkr.ecr.region.amazonaws.com

# Build and push backend image
docker build -t your-aws-account-id.dkr.ecr.region.amazonaws.com/litigation-simulator-backend:latest -f Dockerfile.backend .
docker push your-aws-account-id.dkr.ecr.region.amazonaws.com/litigation-simulator-backend:latest

# Build and push frontend image
docker build -t your-aws-account-id.dkr.ecr.region.amazonaws.com/litigation-simulator-frontend:latest -f Dockerfile.frontend .
docker push your-aws-account-id.dkr.ecr.region.amazonaws.com/litigation-simulator-frontend:latest
```

#### 3. Create RDS Database

Create a PostgreSQL RDS instance:

```bash
aws rds create-db-instance \
  --db-instance-identifier litigation-simulator-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --allocated-storage 20 \
  --master-username dbadmin \
  --master-user-password your_secure_password \
  --vpc-security-group-ids sg-xxxxxxxx \
  --no-publicly-accessible
```

#### 4. Create ElastiCache Redis Cluster

Create a Redis ElastiCache cluster:

```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id litigation-simulator-redis \
  --engine redis \
  --cache-node-type cache.t3.micro \
  --num-cache-nodes 1 \
  --security-group-ids sg-xxxxxxxx
```

#### 5. Create ECS Cluster and Task Definitions

Create an ECS cluster:

```bash
aws ecs create-cluster --cluster-name litigation-simulator-cluster
```

Create task definitions for backend and frontend services:

```bash
aws ecs register-task-definition --cli-input-json file://ecs/backend-task-definition.json
aws ecs register-task-definition --cli-input-json file://ecs/frontend-task-definition.json
```

#### 6. Create ECS Services

Create ECS services for backend and frontend:

```bash
aws ecs create-service --cli-input-json file://ecs/backend-service.json
aws ecs create-service --cli-input-json file://ecs/frontend-service.json
```

#### 7. Create Application Load Balancer

Create an Application Load Balancer to route traffic to the ECS services:

```bash
# Create load balancer
aws elbv2 create-load-balancer --name litigation-simulator-alb --subnets subnet-xxxxxxxx subnet-yyyyyyyy --security-groups sg-xxxxxxxx

# Create target groups
aws elbv2 create-target-group --name backend-target-group --protocol HTTP --port 8000 --vpc-id vpc-xxxxxxxx --target-type ip
aws elbv2 create-target-group --name frontend-target-group --protocol HTTP --port 3000 --vpc-id vpc-xxxxxxxx --target-type ip

# Create listeners
aws elbv2 create-listener --load-balancer-arn arn:aws:elasticloadbalancing:region:account-id:loadbalancer/app/litigation-simulator-alb/xxxxxxxx --protocol HTTP --port 80 --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:region:account-id:targetgroup/frontend-target-group/xxxxxxxx
aws elbv2 create-listener-rule --listener-arn arn:aws:elasticloadbalancing:region:account-id:listener/app/litigation-simulator-alb/xxxxxxxx/xxxxxxxx --priority 10 --conditions Field=path-pattern,Values=/api/* --actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:region:account-id:targetgroup/backend-target-group/xxxxxxxx
```

## Database Initialization

After deploying the application, you'll need to initialize the database with initial data.

### 1. Run Initial Data Import

```bash
# For development
docker compose -f docker-compose.dev.yml exec backend python -m scripts.import_initial_data

# For production
docker compose -f docker-compose.prod.yml exec backend python -m scripts.import_initial_data
```

This script will:
- Import basic judge data from Court Listener
- Create initial user roles
- Set up default case types and jurisdictions

### 2. Run Court Listener Data Import

Import more detailed data from Court Listener:

```bash
# For development
docker compose -f docker-compose.dev.yml exec backend python -m scripts.import_court_listener_data

# For production
docker compose -f docker-compose.prod.yml exec backend python -m scripts.import_court_listener_data
```

This script will:
- Import detailed judge profiles
- Import recent opinions for analysis
- Import oral arguments for analysis

## Initial ML Model Training

Train the initial machine learning models:

```bash
# For development
docker compose -f docker-compose.dev.yml exec backend python -m scripts.train_initial_models

# For production
docker compose -f docker-compose.prod.yml exec backend python -m scripts.train_initial_models
```

This script will:
- Train the judge analysis models
- Train the case outcome prediction models
- Train the simulation engine models

## Monitoring and Maintenance

### Logging

Logs are stored in the following locations:

- Backend logs: `/var/log/litigation-simulator/backend.log`
- Frontend logs: `/var/log/litigation-simulator/frontend.log`
- Database logs: `/var/log/postgresql/postgresql.log`
- Redis logs: `/var/log/redis/redis.log`

### Backup and Restore

#### Database Backup

Create a database backup:

```bash
# For development
docker compose -f docker-compose.dev.yml exec db pg_dump -U postgres litigation_simulator > backup_$(date +%Y%m%d).sql

# For production
docker compose -f docker-compose.prod.yml exec db pg_dump -U postgres litigation_simulator > backup_$(date +%Y%m%d).sql
```

#### Database Restore

Restore from a database backup:

```bash
# For development
cat backup_20250410.sql | docker compose