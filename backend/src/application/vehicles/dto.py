from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID


@dataclass(frozen=True)
class CreateVehicleInput:
    tenant_id: UUID
    created_by_user_id: UUID
    plate: str
    owner_name: str
    stickered_at: date
    voter_id: UUID | None = None
    model: str | None = None
    city: str | None = None


@dataclass(frozen=True)
class UpdateVehicleInput:
    tenant_id: UUID
    vehicle_id: UUID
    plate: str | None = None
    owner_name: str | None = None
    stickered_at: date | None = None
    voter_id: UUID | None = None
    model: str | None = None
    city: str | None = None


@dataclass(frozen=True)
class GetVehicleInput:
    tenant_id: UUID
    vehicle_id: UUID


@dataclass(frozen=True)
class DeleteVehicleInput:
    tenant_id: UUID
    vehicle_id: UUID


@dataclass(frozen=True)
class ListVehiclesInput:
    tenant_id: UUID
    search_text: str | None = None
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True)
class VehicleOutput:
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


@dataclass(frozen=True)
class ListVehiclesOutput:
    items: list[VehicleOutput]
    total: int
    page: int
    page_size: int
    total_pages: int


@dataclass(frozen=True)
class UploadVehiclePhotoInput:
    tenant_id: UUID
    vehicle_id: UUID
    filename: str
    file_bytes: bytes


@dataclass(frozen=True)
class RemoveVehiclePhotoInput:
    tenant_id: UUID
    vehicle_id: UUID


@dataclass(frozen=True)
class GetVehiclePhotoDownloadUrlInput:
    tenant_id: UUID
    vehicle_id: UUID


@dataclass(frozen=True)
class GetVehiclePhotoDownloadUrlOutput:
    download_url: str
    filename: str


@dataclass(frozen=True)
class GetTotalVehicleCountInput:
    tenant_id: UUID
