"""Match EV/ICE vehicles to duty cycle requirements."""
from sqlalchemy.orm import Session
from app.models.reference_data import EVVehicle, ICEVehicle
from app.schemas.inputs import DutyCycle


RANGE_BUFFER = 1.15  # 15% range buffer over required daily distance


class NoCandidateError(Exception):
    pass


def select_ev(duty_cycle: DutyCycle, db: Session, ev_model_id: int | None = None) -> EVVehicle:
    if ev_model_id:
        vehicle = db.query(EVVehicle).filter(EVVehicle.id == ev_model_id).first()
        if vehicle:
            return vehicle

    query = db.query(EVVehicle).filter(
        EVVehicle.range_km >= duty_cycle.daily_distance_km * RANGE_BUFFER,
        EVVehicle.payload_lbs >= duty_cycle.max_payload_lbs,
    )
    if duty_cycle.vehicle_category:
        query = query.filter(EVVehicle.category == duty_cycle.vehicle_category)
    if duty_cycle.refrigeration_required:
        query = query.filter(EVVehicle.has_refrigeration == True)

    candidates = query.order_by(EVVehicle.msrp_cad.asc()).all()
    if not candidates:
        # Relax category filter
        candidates = (
            db.query(EVVehicle)
            .filter(
                EVVehicle.range_km >= duty_cycle.daily_distance_km * RANGE_BUFFER,
                EVVehicle.payload_lbs >= duty_cycle.max_payload_lbs,
            )
            .order_by(EVVehicle.msrp_cad.asc())
            .all()
        )
    if not candidates:
        # Return best match by range even if it doesn't fully qualify
        candidates = db.query(EVVehicle).order_by(EVVehicle.range_km.desc()).limit(1).all()
    if not candidates:
        raise NoCandidateError("No EV vehicles found in database")
    return candidates[0]


def select_ice(duty_cycle: DutyCycle, db: Session, ice_model_id: int | None = None) -> ICEVehicle:
    if ice_model_id:
        vehicle = db.query(ICEVehicle).filter(ICEVehicle.id == ice_model_id).first()
        if vehicle:
            return vehicle

    query = db.query(ICEVehicle).filter(
        ICEVehicle.payload_lbs >= duty_cycle.max_payload_lbs,
    )
    if duty_cycle.vehicle_category:
        query = query.filter(ICEVehicle.category == duty_cycle.vehicle_category)

    candidates = query.order_by(ICEVehicle.msrp_cad.asc()).all()
    if not candidates:
        candidates = (
            db.query(ICEVehicle)
            .filter(ICEVehicle.payload_lbs >= duty_cycle.max_payload_lbs)
            .order_by(ICEVehicle.msrp_cad.asc())
            .all()
        )
    if not candidates:
        candidates = db.query(ICEVehicle).order_by(ICEVehicle.msrp_cad.asc()).limit(1).all()
    if not candidates:
        raise NoCandidateError("No ICE vehicles found in database")
    return candidates[0]
