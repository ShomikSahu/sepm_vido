from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.volcanic_system import VolcanicSystemResponse, VolcanicSystemDetailResponse
from app.schemas.spatial import SystemSpatialObservationsResponse
from app.schemas.timeline import TimelineResponse
from app.repositories import VolcanicSystemRepository, CelestialBodyRepository
from app.services import SpatialService, TimelineService
from app.db.database import db_manager

router = APIRouter(prefix="/volcanic-systems", tags=["Volcanic Systems"])


@router.get("", response_model=List[VolcanicSystemResponse], summary="List volcanic systems")
def list_volcanic_systems(
    celestial_body_id: Optional[str] = Query(default=None, description="Filter by celestial body ID e.g. 'earth', 'mars'")
):
    """Lists volcanic systems, optionally filtered by celestial body."""
    repo = VolcanicSystemRepository(db_manager)
    if celestial_body_id:
        systems = repo.get_by_celestial_body(celestial_body_id)
    else:
        systems = repo.get_all()
    return [VolcanicSystemResponse.model_validate(sys.to_dict()) for sys in systems]


@router.get("/{system_id}", response_model=VolcanicSystemDetailResponse, summary="Get volcanic system details")
def get_volcanic_system(system_id: str):
    """Retrieves detailed information for a specific volcanic system, including parent body context."""
    vs_repo = VolcanicSystemRepository(db_manager)
    cb_repo = CelestialBodyRepository(db_manager)

    system = vs_repo.get_by_id(system_id)
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Volcanic system with ID '{system_id}' not found",
        )

    sys_dict = system.to_dict()
    body = cb_repo.get_by_id(system.celestial_body_id)
    if body:
        sys_dict["celestial_body"] = body.to_dict()

    return VolcanicSystemDetailResponse.model_validate(sys_dict)


@router.get("/{system_id}/spatial", response_model=SystemSpatialObservationsResponse, summary="Get system spatial observations")
def get_system_spatial_observations(system_id: str):
    """Retrieves observations for a system with resolved spatial locations and fallback source tags."""
    vs_repo = VolcanicSystemRepository(db_manager)
    if not vs_repo.get_by_id(system_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Volcanic system with ID '{system_id}' not found",
        )

    spatial_service = SpatialService(db_manager)
    res = spatial_service.get_spatial_observations_for_system(system_id)
    return SystemSpatialObservationsResponse.model_validate(res)


@router.get("/{system_id}/timeline", response_model=TimelineResponse, summary="Get system chronological timeline")
def get_system_timeline(system_id: str):
    """Retrieves unified dual-lane and interleaved chronological timeline feed for a volcanic system."""
    vs_repo = VolcanicSystemRepository(db_manager)
    if not vs_repo.get_by_id(system_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Volcanic system with ID '{system_id}' not found",
        )

    timeline_service = TimelineService(db_manager)
    res = timeline_service.get_timeline_for_system(system_id)
    return TimelineResponse.model_validate(res)
