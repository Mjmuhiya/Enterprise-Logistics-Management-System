from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import current_user
from app.models import Driver, Route, RouteStop, Shipment, User, Vehicle

router = APIRouter(prefix="/api/v1/routing", tags=["Route Optimisation"])


class RouteStopInput(BaseModel):
    shipment_id: UUID
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class RoutePlan(BaseModel):
    stops: list[RouteStopInput] = Field(min_length=1)
    driver_id: UUID | None = None
    vehicle_id: UUID | None = None
    route_date: date | None = None


def nearest_neighbour(stops: list[RouteStopInput]) -> list[RouteStopInput]:
    remaining = stops.copy()
    ordered = [remaining.pop(0)]
    while remaining:
        current = ordered[-1]
        next_stop = min(remaining, key=lambda stop: (stop.latitude-current.latitude) ** 2 + (stop.longitude-current.longitude) ** 2)
        remaining.remove(next_stop)
        ordered.append(next_stop)
    return ordered


@router.post("/optimise", status_code=status.HTTP_201_CREATED)
def optimise_route(payload: RoutePlan, _: User = Depends(current_user), db: Session = Depends(get_db)):
    if payload.driver_id and not db.get(Driver, payload.driver_id):
        raise HTTPException(status_code=404, detail="Driver not found")
    if payload.vehicle_id and not db.get(Vehicle, payload.vehicle_id):
        raise HTTPException(status_code=404, detail="Vehicle not found")
    for stop in payload.stops:
        if not db.get(Shipment, stop.shipment_id):
            raise HTTPException(status_code=404, detail=f"Shipment {stop.shipment_id} not found")

    ordered = nearest_neighbour(payload.stops)
    route = Route(
        driver_id=payload.driver_id,
        vehicle_id=payload.vehicle_id,
        route_date=payload.route_date or date.today(),
        optimisation_method="Nearest Neighbour baseline",
        estimated_duration_minutes=max(30, len(ordered) * 20),
    )
    db.add(route)
    db.flush()
    for sequence, stop in enumerate(ordered, start=1):
        db.add(RouteStop(route_id=route.id, shipment_id=stop.shipment_id, stop_sequence=sequence))
    db.commit()
    db.refresh(route)
    return {
        "route_id": str(route.id),
        "algorithm": route.optimisation_method,
        "stop_count": len(ordered),
        "ordered_stops": [{"shipment_id": str(stop.shipment_id), "sequence": i} for i, stop in enumerate(ordered, start=1)],
        "route_date": route.route_date,
        "estimated_duration_minutes": route.estimated_duration_minutes,
        "note": "Baseline optimisation; production deployments should integrate a road-network routing engine.",
    }
