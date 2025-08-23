# Gemini Context: API de Logística

## Project Overview

This project is a RESTful API built with Python and FastAPI. Its primary purpose is to serve as a wrapper and integration point for the Envia.com logistics services. The API provides endpoints for quoting shipments, with plans to add functionality for creating shipping labels and tracking packages.

**Key Technologies:**
- **Language:** Python 3.11+
- **API Framework:** FastAPI
- **Web Server:** Uvicorn
- **Data Validation:** Pydantic
- **HTTP Client:** Requests
- **Environment/Package Manager:** UV
- **Testing:** Pytest

**Architecture:**
The application follows a simple microservice architecture. It separates the API interface (FastAPI endpoints in `app/main.py`) from external service clients (`app/client_envia.py`) and data schemas (`app/schemas.py`). Configuration is managed via environment variables loaded into a Pydantic `Settings` model (`app/config.py`), which is injected into endpoints using FastAPI's dependency injection system.

## Building and Running

### 1. Environment Setup

The project uses `uv` to manage the virtual environment and dependencies.

```bash
# Create the virtual environment
python -m venv .venv

# Activate the environment
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
```

### 2. Installing Dependencies

Dependencies are specified in `requirements.txt` and can be installed using `uv`.

```bash
# Install dependencies
uv pip install -r requirements.txt
```

### 3. Running the Application

The application is served using Uvicorn. For development, run the following command from the project root:

```bash
# Run the development server with auto-reload
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

### 4. Running Tests

The project uses `pytest` for testing. Tests are located in the `tests/` directory.

```bash
# Run the test suite
pytest
```

## Development Conventions

- **Configuration:** All configuration is handled through environment variables (see `.env.example` if present, or `app/config.py`). Do not use hardcoded secrets or keys.
- **Data Models:** All API request and response bodies are strictly defined using Pydantic models located in `app/schemas.py`.
- **Testing:** New features should be accompanied by tests. The `fastapi.testclient.TestClient` is used for endpoint testing, and `unittest.mock` or `pytest.monkeypatch` should be used to mock external services like the Envia.com API.
- **API Documentation:** FastAPI automatically generates OpenAPI documentation. Ensure endpoints have clear descriptions, summaries, and tags to keep the documentation useful. Access it at `/docs` when the server is running.
