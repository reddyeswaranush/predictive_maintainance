from sqlalchemy.orm import Session
from backend.models.machine import Machine


def get_all_machines(db: Session):
    return db.query(Machine).all()


def get_machine_by_id(db: Session, machine_id: int):
    return db.query(Machine).filter(
        Machine.machine_id == machine_id
    ).first()


def create_machine(db: Session, machine):
    new_machine = Machine(
        machine_name=machine.machine_name,
        department=machine.department,
        location=machine.location,
        status=machine.status
    )

    db.add(new_machine)
    db.commit()
    db.refresh(new_machine)

    return new_machine


def update_machine(db: Session, machine_id: int, machine):
    db_machine = get_machine_by_id(db, machine_id)

    if not db_machine:
        return None

    db_machine.machine_name = machine.machine_name
    db_machine.department = machine.department
    db_machine.location = machine.location
    db_machine.status = machine.status

    db.commit()
    db.refresh(db_machine)

    return db_machine


def delete_machine(db: Session, machine_id: int):
    db_machine = get_machine_by_id(db, machine_id)

    if not db_machine:
        return None

    db.delete(db_machine)
    db.commit()

    return db_machine


def get_machines_by_location(db: Session, location: str):
    return db.query(Machine).filter(
        Machine.location == location
    ).all()


def count_machines_by_location(db: Session, location: str):
    return db.query(Machine).filter(
        Machine.location == location
    ).count()