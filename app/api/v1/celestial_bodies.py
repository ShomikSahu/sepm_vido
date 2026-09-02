from typing import List
from fastapi import APIRouter, HTTPException, status
from app.schemas.celestial_body import CelestialBodyResponse
from app.repositories import CelestialBodyRepository
from app.db.database import db_manager

router = APIRouter(prefix="/celestial-bodies", tags=["Celestial Bodies"])


@router.get("", response_model=List[CelestialBodyResponse], summary="List all celestial bodies")
def list_celestial_bodies():
    """Retrieves all celestial bodies (planets and moons) configured in the observatory."""
    repo = CelestialBodyRepository(db_manager)
    bodies = repo.get_all()
    return [CelestialBodyResponse.model_validate(b.to_dict()) for b in bodies]


@router.get("/{body_id}", response_model=CelestialBodyResponse, summary="Get celestial body by ID")
def get_celestial_body(body_id: str):
    """Retrieves metadata for a specific celestial body."""
    repo = CelestialBodyRepository(db_manager)
    body = repo.get_by_id(body_id)
    if not body:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Celestial body with ID '{body_id}' not found",
        )
    return CelestialBodyResponse.model_validate(body.to_dict())
