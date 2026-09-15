# AI-Based Industrial Maintenance and Process Optimization System

AI-powered predictive maintenance dashboard.

## Technologies

- Python
- Streamlit
- FastAPI
- SQLAlchemy
- Pandas
- Plotly

## Project Structure

- `backend/` - FastAPI API, SQLAlchemy models, schemas and services.
- `frontend/` - Streamlit operations console.
- `ml/` - Feature engineering, training and inference.
- `docs/` - Project documentation and dashboard figures.

## Run locally

Install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Start the backend:

```powershell
uvicorn backend.api.main:app --reload
```

In a second terminal, start the frontend:

```powershell
streamlit run frontend/app.py
```

## Demo login

Use `admin` with password `FactoryOps@123` to access the Streamlit dashboard.
The login is a frontend session gate for the current demonstration; add backend
authentication before production use.
