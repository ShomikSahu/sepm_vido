from fastapi import APIRouter
from app.api.v1.celestial_bodies import router as celestial_bodies_router
from app.api.v1.volcanic_systems import router as volcanic_systems_router
from app.api.v1.observation_sources import router as observation_sources_router
from app.api.v1.observations import router as observations_router
from app.api.v1.volcanic_events import router as volcanic_events_router
from app.api.v1.observation_event_links import router as observation_event_links_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(celestial_bodies_router)
api_v1_router.include_router(volcanic_systems_router)
api_v1_router.include_router(observation_sources_router)
api_v1_router.include_router(observations_router)
api_v1_router.include_router(volcanic_events_router)
api_v1_router.include_router(observation_event_links_router)
