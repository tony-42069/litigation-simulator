# Litigation Simulator

A cutting-edge legal technology platform for data-driven trial preparation, judge analytics, outcome prediction, and interactive litigation simulation. Built for attorneys and legal teams, with a focus on Commercial Real Estate (CRE) litigation.

---

## Features

- **Judge Analysis:** Profiles, writing style, ruling patterns, questioning analysis
- **Case Outcome Prediction:** ML-powered predictions, factor analysis, "what-if" scenarios
- **Interactive Simulation:** AI-generated judicial questioning, opposing counsel, feedback
- **Strategy Recommendations:** Citation and argument suggestions
- **Admin Tools:** Data import, model retraining, background tasks

---

## Technical Architecture

- **Backend:** FastAPI (Python), async, modular microservices
- **Frontend:** React.js (TypeScript), Tailwind CSS, Recharts
- **Database:** PostgreSQL (relational), Redis (cache/queue), JSONB for analytics
- **ML/AI:** Transformers, scikit-learn, topic modeling, clustering, simulation engine
- **Deployment:** Docker Compose, Kubernetes, AWS-ready

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/tony-42069/litigation-simulator.git
cd litigation-simulator
```

### 2. Environment Setup

- Python 3.10+
- Node.js 16+ and npm
- Docker & Docker Compose
- PostgreSQL 13+
- Redis 6+ (can use WSL or Docker)

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=litigation_simulator
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
REDIS_HOST=localhost
REDIS_PORT=6379
COURT_LISTENER_API_TOKEN=your_court_listener_api_token
SECRET_KEY=your_secret_key
DEBUG=True
MODEL_DIR=./models
```

### 4. Database Setup

- Create the database:
  ```bash
  psql -U postgres -c "CREATE DATABASE litigation_simulator;"
  ```
- Initialize schema:
  ```bash
  psql -U postgres -d litigation_simulator -f schema.sql
  ```

### 5. Data Import

- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- Import initial data from Court Listener:
  ```bash
  python import_courtlistener_data.py
  ```

### 6. Running the App

- **Backend:**  
  ```bash
  uvicorn api-endpoints:app --reload
  ```
- **Frontend:**  
  ```bash
  cd frontend
  npm install
  npm start
  ```

---

## Deployment

- **Docker Compose:**  
  ```bash
  docker compose -f docker-compose.dev.yml up -d
  ```
- **Kubernetes & AWS:**  
  See `deployment-instructions.md` for full production deployment steps.

---

## Contributing

1. Fork the repo and create your branch
2. Commit your changes with clear messages
3. Push to your fork and submit a pull request

---

## Documentation

- [Project Overview](project-overview.md)
- [Technical Architecture](technical-architecture.md)
- [Database Schema](database-schema.md)
- [Business Plan](litigation-simulator-business-plan.md)
- [Deployment Instructions](deployment-instructions.md)
- [TODO List](TODO.md)

---

## License

MIT License

---

## Contact

For questions, support, or partnership inquiries, please open an issue or contact the maintainer.

# Database Connection Tester

A simple FastAPI application to test database connectivity.

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install fastapi sqlalchemy uvicorn python-dotenv
   ```
3. Create a `.env` file based on the `.env.example` template:
   ```
   cp .env.example .env
   ```
4. Edit the `.env` file with your actual database connection string

## Usage

Run the application:
```
python test_db_connection.py
```

Or with uvicorn directly:
```
uvicorn test_db_connection:app --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /`: Returns a simple message confirming the service is running
- `GET /test-connection`: Tests the database connection and returns the result

## Environment Variables

- `DATABASE_URL`: Connection string for your database (required)
- `PORT`: Server port (default: 8000)
- `HOST`: Server host address (default: 0.0.0.0)
