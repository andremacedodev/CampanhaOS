from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class VehicleCreateRequest(BaseModel):
    plate: str = Field(..., min_length=7, max_length=8)
    owner_name: str = Field(..., min_length=1, max_length=255)
    stickered_at: date
    voter_id: UUID | None = None
    model: str | None = Field(None, max_length=100)
    city: str | None = Field(None, max_length=255)


class VehicleUpdateRequest(BaseModel):
    plate: str | None = Field(None, min_length=7, max_length=8)
    owner_name: str | None = Field(None, min_length=1, max_length=255)
    stickered_at: date | None = None
    voter_id: UUID | None = None
    model: str | None = Field(None, max_length=100)
    city: str | None = Field(None, max_length=255)


class VehicleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_by_user_id: UUID
    plate: str
    owner_name: str
    voter_id: UUID | None
    model: str | None
    city: str | None
    stickered_at: date
    created_at: datetime
    updated_at: datetime
    photo_filename: str | None
    photo_content_type: str | None
    photo_size_bytes: int | None


class VehicleListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[VehicleResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class VehiclePhotoDownloadResponse(BaseModel):
    download_url: str
    filename: str
