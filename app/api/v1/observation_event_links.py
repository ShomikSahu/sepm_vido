from typing import List
from fastapi import APIRouter, HTTPException, status
from app.schemas.observation_event_link import (
    ObservationEventLinkCreateRequest,
    ObservationEventLinkResponse,
    ObservationEventLinkDetailResponse,
)
from app.services import EventService
from app.db.database import db_manager

router = APIRouter(tags=["Observation Event Links"])


@router.post("/observation-event-links", response_model=ObservationEventLinkResponse, status_code=status.HTTP_201_CREATED, summary="Link an observation to a volcanic event")
def create_observation_event_link(request: ObservationEventLinkCreateRequest):
    """
    Creates a contextual relationship link between an Observation and a VolcanicEvent.
    Enforces unique constraint checks and automatically calculates temporal_offset_hours.
    """
    event_service = EventService(db_manager)
    try:
        link = event_service.link_observation_to_event(
            link_id=request.id,
            observation_id=request.observation_id,
            event_id=request.event_id,
            relationship_type=request.relationship_type,
            notes=request.notes,
        )
        return ObservationEventLinkResponse.model_validate(link.to_dict())
    except ValueError as e:
        err_msg = str(e)
        if "already exists" in err_msg or "UNIQUE constraint failed" in err_msg:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err_msg)
        if "not found" in err_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)


@router.get("/observations/{observation_id}/links", response_model=List[ObservationEventLinkDetailResponse], summary="Get event links for an observation")
def get_observation_links(observation_id: str):
    """Retrieves linked event context for an observation."""
    event_service = EventService(db_manager)
    links = event_service.get_event_links_for_observation(observation_id)
    return [ObservationEventLinkDetailResponse.model_validate(l) for l in links]
