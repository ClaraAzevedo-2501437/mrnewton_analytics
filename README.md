# MrNewton Analytics Provider

Backend service for MrNewton Analytics Provider in the Inven!RA architecture. Calculates and provides quantitative and qualitative metrics about student performance from submission data.

## Tech Stack

- **Python 3.11+**
- **FastAPI** - Modern web framework for APIs
- **Uvicorn** - ASGI server
- **MongoDB Atlas** - Cloud database
- **Motor** - Async MongoDB driver
- **httpx** - Async HTTP client for Activity API integration
- **Pydantic** - Data validation

## Setup

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

### Configuration

The application connects to MongoDB Atlas and the Activity API. Set environment variables if needed:
```bash
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/
ACTIVITY_API_URL=http://localhost:5000/api/v1
```

Default connections:
- MongoDB Atlas: Pre-configured cluster
- Activity API: `http://localhost:5000/api/v1`

### Run

```bash
python run.py
```

Server runs on: **http://localhost:8000**

**Note:** Ensure the MrNewton Activity API is running on `http://localhost:5000`.

## API Documentation

Interactive API docs:
- **Swagger UI:** http://localhost:8000/api-docs
- **ReDoc:** http://localhost:8000/redoc

## Main Endpoints

### Contract Management
- `GET /api/v1/analytics/contract` - Get analytics contract (available metrics)
- `POST /api/v1/analytics/contract` - Create/update analytics contract

### Metrics
- `GET /api/v1/analytics/instances/{instance_id}/students/{student_id}/metrics` - Get student metrics
- `GET /api/v1/analytics/instances/{instance_id}/metrics` - Get all students metrics for instance

### Health
- `GET /health` - Service health check

## Metrics Calculation

### Quantitative Metrics
- **total_attempts** - Total number of attempts
- **total_time_seconds** - Total time spent (seconds)
- **average_time_per_attempt** - Average time per attempt
- **number_of_correct_answers** - Number of correct answers
- **final_score** - Final score (0-1)
- **activity_success** - Pass/fail based on approval threshold

### Qualitative Metrics
- **answer_rationale** - Student's textual explanations/rationale

## Database Structure

**Database:** `mrnewton-analytics` (MongoDB Atlas)

**Collections:**
- **`analyticsContract`** - Defines available metrics
- **`analytics`** - Cached calculated metrics (by instance_id + student_id)

## Integration

Consumes Activity API endpoints:
- `GET /api/v1/submissions/instance/{instanceId}/student/{studentId}` - Get student submission
- `GET /api/v1/submissions/instance/{instanceId}` - Get all instance submissions
- `GET /api/v1/deploy/{instanceId}` - Get instance info
- `GET /api/v1/config/{activityId}` - Get activity configuration

## Architecture

- **Routers:** API endpoints
- **Services:** Metrics calculation logic
- **Clients:** HTTP client for Activity API
- **Repositories:** Data access (MongoDB)
- **Models:** Pydantic schemas for validation
