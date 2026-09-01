from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.telemetry import Telemetry
from ml.predict import predict_metro_telemetry, predict_telemetry
from backend.schemas.prediction import (
    MetroTelemetryInput,
    PredictionCreate,
    PredictionUpdate,
    PredictionResponse,
)

from backend.services.prediction_service import (
    get_all_predictions,
    get_prediction_by_id,
    create_prediction,
    update_prediction,
    delete_prediction,
)

router = APIRouter(
    prefix="/predictions",
    tags=["Predictions"]
)


@router.post("/generate-metro", response_model=PredictionResponse)
def generate_metro_prediction(
    telemetry: MetroTelemetryInput,
    db: Session = Depends(get_db),
):
    values = telemetry.model_dump(exclude={"machine_id"})
    prediction = predict_metro_telemetry(values)
    return create_prediction(
        db,
        PredictionCreate(machine_id=telemetry.machine_id, **prediction),
    )


@router.post("/generate/{machine_id}", response_model=PredictionResponse)
def generate_prediction(machine_id: int, db: Session = Depends(get_db)):
    telemetry = (
        db.query(Telemetry)
        .filter(Telemetry.machine_id == machine_id)
        .order_by(Telemetry.id.desc())
        .first()
    )
    if telemetry is None:
        raise HTTPException(
            status_code=404,
            detail="No telemetry found for this machine",
        )

    values = {
        column: getattr(telemetry, column)
        for column in (
            "temperature",
            "pressure",
            "vibration",
            "voltage",
            "current",
            "power",
            "rpm",
            "humidity",
            "oil_level",
        )
    }
    prediction = predict_telemetry(values)
    return create_prediction(
        db,
        PredictionCreate(machine_id=machine_id, **prediction),
    )


@router.get("/", response_model=list[PredictionResponse])
def read_predictions(db: Session = Depends(get_db)):
    return get_all_predictions(db)


@router.get("/{prediction_id}", response_model=PredictionResponse)
def read_prediction(prediction_id: int, db: Session = Depends(get_db)):
    prediction = get_prediction_by_id(db, prediction_id)

    if prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")

    return prediction


@router.post("/", response_model=PredictionResponse)
def add_prediction(
    prediction: PredictionCreate,
    db: Session = Depends(get_db)
):
    return create_prediction(db, prediction)


@router.put("/{prediction_id}", response_model=PredictionResponse)
def edit_prediction(
    prediction_id: int,
    prediction: PredictionUpdate,
    db: Session = Depends(get_db)
):
    updated = update_prediction(db, prediction_id, prediction)

    if updated is None:
        raise HTTPException(status_code=404, detail="Prediction not found")

    return updated


@router.delete("/{prediction_id}")
def remove_prediction(
    prediction_id: int,
    db: Session = Depends(get_db)
):
    deleted = delete_prediction(db, prediction_id)

    if deleted is None:
        raise HTTPException(status_code=404, detail="Prediction not found")

    return {"message": "Prediction deleted successfully"}