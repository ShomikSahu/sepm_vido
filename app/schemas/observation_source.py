from pydantic import BaseModel, Field, ConfigDict
from app.models.observation_source import PlatformType, ObservationSource


class ObservationSourceResponse(BaseModel):
    """API response model for ObservationSource entities."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique source identifier e.g. 'src-sentinel-2'")
    name: str = Field(..., description="Source or instrument name")
    platform_type: PlatformType = Field(..., description="Platform type (SATELLITE_ORBITER, GROUND_OBSERVATORY, etc.)")
    operator_agency: str = Field(..., description="Operating organization e.g. 'ESA', 'NASA', 'INGV'")

    @classmethod
    def from_domain(cls, source: ObservationSource) -> "ObservationSourceResponse":
        return cls.model_validate(source.to_dict())
