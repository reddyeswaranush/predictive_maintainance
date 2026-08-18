from fastapi import FastAPI
from backend.database.connection import Base, engine

# Import all models so SQLAlchemy creates tables
from backend.models.machine import Machine
from backend.models.sensor import Sensor
from backend.models.telemetry import Telemetry
from backend.models.prediction import Prediction
from backend.models.maintenance import Maintenance
from backend.models.notification import Notification
from backend.models.inventory import Inventory
from backend.models.incident import Incident

# Import routers
from backend.api.routers.machine import router as machine_router
from backend.api.routers.sensor import router as sensor_router
from backend.api.routers.telemetry import router as telemetry_router
from backend.api.routers.prediction import router as prediction_router
from backend.api.routers.maintenance import router as maintenance_router
from backend.api.routers.notification import router as notification_router
from backend.api.routers.inventory import router as inventory_router
from backend.api.routers.incident import router as incident_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FactoryOps AI Backend",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "FactoryOps AI Backend is running successfully!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": "connected"
    }


# Register Routers
app.include_router(machine_router)
app.include_router(sensor_router)
app.include_router(telemetry_router)
app.include_router(prediction_router)
app.include_router(maintenance_router)
app.include_router(notification_router)
app.include_router(inventory_router)
app.include_router(incident_router)