import sqlite3
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.volcanic_event import VolcanicEventCreateRequest, VolcanicEventResponse
from app.repositories import VolcanicEventRepository
from app.services import EventService
from app.db.database import db_manager

router = APIRouter(prefix="/volcanic-events", tags=["Volcanic Events"])


@router.post("", response_model=VolcanicEventResponse, status_code=status.HTTP_201_CREATED, summary="Create a volcanic event")
def create_volcanic_event(request: VolcanicEventCreateRequest):
    """
    Creates a new physical VolcanicEvent.
    Supports bounded events (start_time and end_time) and ongoing active events (end_time = NULL).
    """
    event_service = EventService(db_manager)
    payload = request.model_dump()

    try:
        evt = event_service.validate_and_create_event(payload)
        return VolcanicEventResponse.from_domain(evt)
    except ValueError as e:
        err_msg = str(e)
        if "already exists" in err_msg or "UNIQUE constraint failed" in err_msg:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Database integrity conflict: {str(e)}")


@router.get("/{event_id}", response_model=VolcanicEventResponse, summary="Get volcanic event by ID")
def get_volcanic_event(event_id: str):
    """Retrieves a specific volcanic event by ID."""
    repo = VolcanicEventRepository(db_manager)
    evt = repo.get_by_id(event_id)
    if not evt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Volcanic event with ID '{event_id}' not found",
        )
    return VolcanicEventResponse.from_domain(evt)


@router.get("", response_model=List[VolcanicEventResponse], summary="List volcanic events")
def list_volcanic_events(
    volcanic_system_id: Optional[str] = Query(default=None, description="Filter by volcanic system ID"),
    ongoing_only: bool = Query(default=False, description="If True, returns only active ongoing events (end_time IS NULL)"),
):
    """Lists volcanic events, optionally filtered by system or active ongoing status."""
    repo = VolcanicEventRepository(db_manager)
    if ongoing_only:
        events = repo.get_ongoing_events()
        if volcanic_system_id:
            events = [e for e in events if e.volcanic_system_id == volcanic_system_id]
    elif volcanic_system_id:
        events = repo.get_by_system(volcanic_system_id)
    else:
        events = repo.get_all()

    return [VolcanicEventResponse.from_domain(e) for e in events]
