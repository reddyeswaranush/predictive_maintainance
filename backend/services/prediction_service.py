from sqlalchemy.orm import Session
from backend.models.prediction import Prediction
from backend.schemas.prediction import PredictionCreate, PredictionUpdate


def get_all_predictions(db: Session):
    return db.query(Prediction).all()


def get_prediction_by_id(db: Session, prediction_id: int):
    return db.query(Prediction).filter(
        Prediction.id == prediction_id
    ).first()


def create_prediction(db: Session, prediction: PredictionCreate):
    db_prediction = Prediction(**prediction.model_dump())
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction


def update_prediction(db: Session, prediction_id: int, prediction: PredictionUpdate):
    db_prediction = get_prediction_by_id(db, prediction_id)

    if not db_prediction:
        return None

    for key, value in prediction.model_dump(exclude_unset=True).items():
        setattr(db_prediction, key, value)

    db.commit()
    db.refresh(db_prediction)
    return db_prediction


def delete_prediction(db: Session, prediction_id: int):
    db_prediction = get_prediction_by_id(db, prediction_id)

    if not db_prediction:
        return None

    db.delete(db_prediction)
    db.commit()
    return db_prediction