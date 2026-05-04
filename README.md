# Full-Stack FastAPI Calculator with JWT Auth & Interactive UI

A production-ready FastAPI application featuring a fully functional interactive calculator front-end, secured by JWT-based user authentication and backed by PostgreSQL. The project includes automated CI/CD pipelines, comprehensive End-to-End (E2E) testing, and Docker containerization.

## Features

* **Interactive Frontend UI:** Client-side HTML/JS application (`index.html`, `login.html`, `register.html`) providing a seamless interface for users to register, log in, compute standard and advanced math operations, and manage their data.
* **Advanced Mathematical Operations:** Fully supports addition, subtraction, multiplication, division, as well as advanced operations like **Exponentiation** and **Modulus**.
* **Complete BREAD Lifecycle:** Fully integrated front-end and back-end operations allowing users to **B**rowse their history, **R**ead specific calculation details via an expandable panel, **E**dit past calculations by populating the main form, **A**dd new calculations, and **D**elete records.
* **JWT-Based Security:** Secure user registration and login endpoints utilizing JSON Web Tokens (JWT) for session management, alongside `passlib` and `bcrypt` for secure password hashing. Users are strictly isolated to accessing and modifying only their own data.
* **Modular Architecture:** Organized codebase utilizing FastAPI `APIRouter` to cleanly separate user authentication routes from calculation logic.
* **Robust Data Validation:** Strict input validation utilizing Pydantic schemas and Enums to catch errors (like division/modulus by zero or invalid operation types) before they reach the database.
* **Scalable Logic:** Implements the Factory Design Pattern to cleanly decouple the mathematical calculation logic from the API routing and database layers, making it incredibly easy to scale and add new calculation features.
* **PostgreSQL Integration:** Fully integrated relational database setup using SQLAlchemy ORM.
* **Accelerated E2E Testing:** Unit, integration, and E2E testing using `pytest` and Playwright, featuring API-level authentication fixtures to rapidly inject JWT tokens and speed up UI testing while dynamically handling database sorting states.
* **Automated CI/CD:** GitHub Actions pipeline configured for testing (with a live background server), security scanning (Bandit), and automated deployment to Docker Hub.

---

## Prerequisites

Before you begin, ensure you have the following installed on your machine:
* **Python 3.11+**
* **Docker Desktop** (for running the local PostgreSQL database)
* **Git**

---

## Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Aniket-NJIT/final_project.git
cd final_project
```
### 2. Set Up a Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium  # Required for E2E UI testing
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory to store your JWT secret key.
```bash
echo 'SECRET_KEY="your-secure-random-secret-key-here"' > .env
```
(Note: You can generate a truly random secure key by running `python -c "import secrets; print(secrets.token_hex(32))"` in your terminal).


### 5. Start the Database (Docker Compose)
```bash
docker compose up -d
```
Access pgAdmin at http://localhost:5050 (Login: `admin@admin.com` / Password: admin).

Once connected to pgAdmin, create two databases:
1. calculator_db (For the main application)
2. test_calculator_db (For local testing)


### 6. Run the Application
```bash
python -m uvicorn main:app --reload
```
- Frontend UI: Open your browser to http://127.0.0.1:8000/ to access the interactive web app.
- Interactive API Docs (Swagger): http://127.0.0.1:8000/docs

### 7. Run Tests
Because this project includes Playwright End-to-End tests that simulate a real browser interacting with the frontend, testing is split into two phases.

**Phase 1: Unit & Integration Tests**
Run the standard API and logic tests without starting the server:
```bash
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/test_calculator_db" pytest tests/ --ignore=tests/test_e2e.py
```

**Phase 2: End-to-End (E2E) UI Tests**
To run the Playwright tests, the server must be actively running so the headless browser can visit the pages.
1. Open Terminal 1: Start the application server:
```bash
python -m uvicorn main:app
```

2. Open Terminal 2: Run the E2E test file.
```bash
pytest tests/test_e2e.py
```

The test suite covers:

- test_main.py: Validates core application startup and root route responses.

- test_operations.py: Unit tests for the core mathematical functions, including newly added advanced operations.

- test_users.py: Integration tests for registration, duplicate constraints, and JWT token generation.

- test_calculations.py: Integration tests validating the Calculation model, Factory pattern, and full BREAD lifecycle linked to JWT authentication.

- test_e2e.py: Accelerated Playwright tests utilizing backend API setup fixtures to rapidly simulate the complete BREAD UI lifecycle and validate error handling.


### Docker Hub & Deployment
This project is fully containerized and automatically built and pushed to Docker Hub upon every successful merge to the `main` branch via GitHub Actions.

View the docker hub repository at: https://hub.docker.com/r/akhalate/final_calculator

You can pull the latest built image directly from Docker Hub to run the application anywhere:
```bash
docker pull akhalate/final_calculator
```

To run the containerized application locally (Note: You must pass in your database credentials):
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://postgres:postgres@host.docker.internal:5432/calculator_db" \
  -e SECRET_KEY="your-secret-key" \
  akhalate/final_calculator:latest
```

### CI/CD Pipeline Architecture
The `.github/workflows/ci-cd.yml` file dictates the automated workflow:
1. Test Job: Spins up a fresh PostgreSQL service container, installs dependencies (including OS-level libraries required for Playwright headless testing via --with-deps), and executes the fully isolated Pytest suite.
2. Security Job: Runs bandit to scan the codebase for known vulnerabilities.
3. Deploy Job: Authenticates with Docker Hub and pushes the newly built image, tagged as `latest`, ensuring only code from the `main` branch is shipped to production.