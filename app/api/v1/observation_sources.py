from typing import List
from fastapi import APIRouter, HTTPException, status
from app.schemas.observation_source import ObservationSourceResponse
from app.repositories import ObservationSourceRepository
from app.db.database import db_manager

router = APIRouter(prefix="/observation-sources", tags=["Observation Sources"])


@router.get("", response_model=List[ObservationSourceResponse], summary="List observation sources")
def list_observation_sources():
    """Lists sensor platforms and observatories."""
    repo = ObservationSourceRepository(db_manager)
    sources = repo.get_all()
    return [ObservationSourceResponse.model_validate(s.to_dict()) for s in sources]


@router.get("/{source_id}", response_model=ObservationSourceResponse, summary="Get observation source by ID")
def get_observation_source(source_id: str):
    """Retrieves metadata for a specific observation source."""
    repo = ObservationSourceRepository(db_manager)
    source = repo.get_by_id(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Observation source with ID '{source_id}' not found",
        )
    return ObservationSourceResponse.model_validate(source.to_dict())
