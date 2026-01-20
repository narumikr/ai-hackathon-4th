"""Location API スキーマ"""

from pydantic import BaseModel, Field


class LocationSchema(BaseModel):
    """地理的位置スキーマ"""

    lat: float = Field(..., ge=-90, le=90, description="緯度")
    lng: float = Field(..., ge=-180, le=180, description="経度")
