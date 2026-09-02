from typing import Dict, Any, List, Optional
from app.db.database import DatabaseManager, db_manager
from app.models.observation import Observation
from app.models.volcanic_system import VolcanicSystem
from app.models.celestial_body import CelestialBody
from app.repositories import (
    ObservationRepository,
    VolcanicSystemRepository,
    CelestialBodyRepository,
)


class SpatialService:
    """Business service for resolving spatial positions and coordinate fallbacks for presentation layers."""

    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db if db is not None else db_manager
        self.obs_repo = ObservationRepository(self.db)
        self.vs_repo = VolcanicSystemRepository(self.db)
        self.cb_repo = CelestialBodyRepository(self.db)

    def resolve_observation_spatial_location(
        self, observation: Observation, volcanic_system: Optional[VolcanicSystem] = None
    ) -> Dict[str, Any]:
        """
        Resolves the spatial coordinate payload for an observation following approved fallback rules:
        1. Observation coordinates -> source = "OBSERVATION"
        2. Parent VolcanicSystem coordinates -> source = "VOLCANO_FALLBACK"
        3. Neither available -> source = "UNLOCATED"
        """
        if volcanic_system is None and observation.volcanic_system_id:
            volcanic_system = self.vs_repo.get_by_id(observation.volcanic_system_id)

        celestial_body: Optional[CelestialBody] = None
        if volcanic_system and volcanic_system.celestial_body_id:
            celestial_body = self.cb_repo.get_by_id(volcanic_system.celestial_body_id)

        # Apply fallback logic
        fallback_res = observation.resolve_spatial_location(volcanic_system)

        return {
            "observation_id": observation.id,
            "volcanic_system_id": observation.volcanic_system_id,
            "volcanic_system_name": volcanic_system.name if volcanic_system else None,
            "celestial_body_id": celestial_body.id if celestial_body else None,
            "celestial_body_name": celestial_body.name if celestial_body else None,
            "coordinate_system": celestial_body.coordinate_system if celestial_body else "UNKNOWN",
            "longitude_convention": celestial_body.longitude_convention.value if celestial_body else "UNKNOWN",
            "latitude": fallback_res["latitude"],
            "longitude": fallback_res["longitude"],
            "spatial_source": fallback_res["source"],
            "media_path": observation.media_path,
            "summary": observation.summary,
            "timestamp": observation.timestamp,
        }

    def get_spatial_observations_for_system(self, system_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Retrieves and resolves spatial locations for all observations belonging to a volcanic system."""
        volcanic_system = self.vs_repo.get_by_id(system_id)
        observations = self.obs_repo.get_by_system(system_id)

        located: List[Dict[str, Any]] = []
        unlocated: List[Dict[str, Any]] = []

        for obs in observations:
            resolved = self.resolve_observation_spatial_location(obs, volcanic_system)
            if resolved["spatial_source"] == "UNLOCATED":
                unlocated.append(resolved)
            else:
                located.append(resolved)

        return {
            "located_observations": located,
            "unlocated_observations": unlocated,
        }

    def get_spatial_observations_for_body(self, celestial_body_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Retrieves and resolves spatial locations for all observations under a target celestial body."""
        systems = self.vs_repo.get_by_celestial_body(celestial_body_id)
        system_map = {sys.id: sys for sys in systems}

        all_located: List[Dict[str, Any]] = []
        all_unlocated: List[Dict[str, Any]] = []

        for sys_id, sys in system_map.items():
            obs_list = self.obs_repo.get_by_system(sys_id)
            for obs in obs_list:
                resolved = self.resolve_observation_spatial_location(obs, sys)
                if resolved["spatial_source"] == "UNLOCATED":
                    all_unlocated.append(resolved)
                else:
                    all_located.append(resolved)

        return {
            "located_observations": all_located,
            "unlocated_observations": all_unlocated,
        }
