**# Predictive Maintenance**



**AI-powered predictive maintenance dashboard.**



**## Technologies**

**- Python**

**- Streamlit**

**- FastAPI**

**- SQLAlchemy**

**- Pandas**

**- Plotly**



**## Project Structure**



**backend/** - FastAPI API, SQLAlchemy models, schemas and services.

**frontend/** - Streamlit operations console (`app.py`).

**ml/** - Reserved for feature engineering, training and inference.

**docs/** - Project documentation and dashboard figures.

## Run locally

Start the backend from the project root:

```powershell
uvicorn backend.api.main:app --reload
```

In a second terminal, start the Streamlit frontend:

```powershell
streamlit run frontend/app.py
```

## Demo login

Use `admin` with password `FactoryOps@123` to access the Streamlit dashboard.
The login is a frontend session gate for the current demonstration; add backend authentication before production use.

