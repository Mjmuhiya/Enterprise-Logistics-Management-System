from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.models import User
from app.main import current_user

router = APIRouter(prefix="/api/v1/routing", tags=["Route Optimisation"])


class RouteStop(BaseModel):
    shipment_id: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class RoutePlan(BaseModel):
    stops: list[RouteStop] = Field(min_length=1)


def nearest_neighbour(stops: list[RouteStop]) -> list[RouteStop]:
    """Simple deterministic baseline for route optimisation demos."""
    remaining = stops.copy()
    ordered = [remaining.pop(0)]
    while remaining:
        current = ordered[-1]
        next_stop = min(
            remaining,
            key=lambda stop: (stop.latitude - current.latitude) ** 2
            + (stop.longitude - current.longitude) ** 2,
        )
        remaining.remove(next_stop)
        ordered.append(next_stop)
    return ordered


@router.post("/optimise")
def optimise_route(payload: RoutePlan, user: User = Depends(current_user)):
    ordered = nearest_neighbour(payload.stops)
    return {
        "algorithm": "nearest-neighbour baseline",
        "stop_count": len(ordered),
        "ordered_stops": ordered,
        "note": "Production routing can replace this baseline with a road-network optimisation service.",
    }
