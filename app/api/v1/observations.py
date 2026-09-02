import sqlite3
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.observation import ObservationCreateRequest, ObservationResponse
from app.repositories import ObservationRepository, VolcanicSystemRepository
from app.services import ValidationService
from app.db.database import db_manager

router = APIRouter(prefix="/observations", tags=["Observations"])


@router.post("", response_model=ObservationResponse, status_code=status.HTTP_201_CREATED, summary="Create/ingest an observation")
def create_observation(request: ObservationCreateRequest):
    """
    Ingests a new scientific observation record.
    Performs full core and composite metadata facet validation via ValidationService.
    """
    val_service = ValidationService(db_manager)
    payload = request.model_dump()

    try:
        obs = val_service.ingest_observation(payload)
        return ObservationResponse.from_domain(obs)
    except ValueError as e:
        err_msg = str(e)
        if "already exists" in err_msg or "UNIQUE constraint failed" in err_msg:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Database integrity conflict: {str(e)}")


@router.get("/{observation_id}", response_model=ObservationResponse, summary="Get observation by ID")
def get_observation(observation_id: str):
    """Retrieves a specific observation record by ID."""
    repo = ObservationRepository(db_manager)
    obs = repo.get_by_id(observation_id)
    if not obs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Observation with ID '{observation_id}' not found",
        )
    return ObservationResponse.from_domain(obs)


@router.get("", response_model=List[ObservationResponse], summary="Search and filter observations")
def search_observations(
    volcanic_system_id: Optional[str] = Query(default=None, description="Filter by volcanic system ID"),
    celestial_body_id: Optional[str] = Query(default=None, description="Filter by celestial body ID"),
    source_id: Optional[str] = Query(default=None, description="Filter by source platform ID"),
    facet: Optional[str] = Query(default=None, description="Filter by active metadata facet ('IMAGE', 'THERMAL', 'PLANETARY_ORBITAL')"),
    start_date: Optional[str] = Query(default=None, description="Filter by start timestamp (ISO-8601)"),
    end_date: Optional[str] = Query(default=None, description="Filter by end timestamp (ISO-8601)"),
):
    """Searches and filters observations across volcanic systems, celestial bodies, facet categories, and date ranges."""
    obs_repo = ObservationRepository(db_manager)
    vs_repo = VolcanicSystemRepository(db_manager)

    # 1. Start with system or body filter
    if volcanic_system_id:
        results = obs_repo.get_by_system(volcanic_system_id)
    elif celestial_body_id:
        systems = vs_repo.get_by_celestial_body(celestial_body_id)
        results = []
        for sys in systems:
            results.extend(obs_repo.get_by_system(sys.id))
    elif facet:
        results = obs_repo.filter_by_facet(facet)
    elif start_date or end_date:
        results = obs_repo.filter_by_date_range(start_date, end_date)
    else:
        results = obs_repo.get_all()

    # 2. Apply secondary in-memory filters if multiple parameters provided
    filtered = []
    for obs in results:
        if source_id and obs.source_id != source_id:
            continue
        active_facets = obs.metadata.get("active_facets", []) if isinstance(obs.metadata, dict) else []
        if facet and facet not in active_facets:
            continue
        if start_date and obs.timestamp < start_date:
            continue
        if end_date and obs.timestamp > end_date:
            continue
        filtered.append(obs)

    return [ObservationResponse.from_domain(o) for o in filtered]
