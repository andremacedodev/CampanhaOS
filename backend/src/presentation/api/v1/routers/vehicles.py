"""
Router de veículos adesivados.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from src.application.vehicles.create_vehicle import CreateVehicleUseCase
from src.application.vehicles.delete_vehicle import DeleteVehicleUseCase
from src.application.vehicles.dto import (
    CreateVehicleInput,
    DeleteVehicleInput,
    GetVehicleInput,
    ListVehiclesInput,
    RemoveVehiclePhotoInput,
    UpdateVehicleInput,
)
from src.application.vehicles.get_photo_download_url import (
    GetVehiclePhotoDownloadUrlInput,
    GetVehiclePhotoDownloadUrlUseCase,
)
from src.application.vehicles.get_vehicle import GetVehicleUseCase
from src.application.vehicles.list_vehicles import ListVehiclesUseCase
from src.application.vehicles.remove_photo import RemoveVehiclePhotoUseCase
from src.application.vehicles.update_vehicle import UpdateVehicleUseCase
from src.application.vehicles.upload_photo import UploadVehiclePhotoInput, UploadVehiclePhotoUseCase
from src.presentation.api.dependencies import CurrentUser, DbSession
from src.presentation.api.vehicles_dependencies import (
    get_create_vehicle_use_case,
    get_delete_vehicle_use_case,
    get_get_vehicle_use_case,
    get_list_vehicles_use_case,
    get_remove_vehicle_photo_use_case,
    get_update_vehicle_use_case,
    get_upload_vehicle_photo_use_case,
    get_vehicle_photo_download_url_use_case,
)
from src.presentation.api.v1.schemas.vehicles import (
    VehicleCreateRequest,
    VehicleListResponse,
    VehiclePhotoDownloadResponse,
    VehicleResponse,
    VehicleUpdateRequest,
)

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    current_user: CurrentUser,
    request: VehicleCreateRequest,
    session: DbSession,
    use_case: Annotated[CreateVehicleUseCase, Depends(get_create_vehicle_use_case)],
) -> VehicleResponse:
    output = await use_case.execute(
        CreateVehicleInput(
            tenant_id=current_user.tenant_id,
            created_by_user_id=current_user.id,
            plate=request.plate,
            owner_name=request.owner_name,
            stickered_at=request.stickered_at,
            voter_id=request.voter_id,
            model=request.model,
            city=request.city,
        )
    )
    await session.commit()
    return VehicleResponse.model_validate(output)


@router.get("", response_model=VehicleListResponse)
async def list_vehicles(
    current_user: CurrentUser,
    use_case: Annotated[ListVehiclesUseCase, Depends(get_list_vehicles_use_case)],
    search: str | None = Query(None, description="Busca por placa, proprietário ou modelo"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> VehicleListResponse:
    output = await use_case.execute(
        ListVehiclesInput(tenant_id=current_user.tenant_id, search_text=search, page=page, page_size=page_size)
    )
    return VehicleListResponse.model_validate(output)


@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: UUID,
    current_user: CurrentUser,
    use_case: Annotated[GetVehicleUseCase, Depends(get_get_vehicle_use_case)],
) -> VehicleResponse:
    output = await use_case.execute(GetVehicleInput(tenant_id=current_user.tenant_id, vehicle_id=vehicle_id))
    return VehicleResponse.model_validate(output)


@router.patch("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: UUID,
    current_user: CurrentUser,
    request: VehicleUpdateRequest,
    session: DbSession,
    use_case: Annotated[UpdateVehicleUseCase, Depends(get_update_vehicle_use_case)],
) -> VehicleResponse:
    output = await use_case.execute(
        UpdateVehicleInput(
            tenant_id=current_user.tenant_id,
            vehicle_id=vehicle_id,
            plate=request.plate,
            owner_name=request.owner_name,
            stickered_at=request.stickered_at,
            voter_id=request.voter_id,
            model=request.model,
            city=request.city,
        )
    )
    await session.commit()
    return VehicleResponse.model_validate(output)


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
    vehicle_id: UUID,
    current_user: CurrentUser,
    session: DbSession,
    use_case: Annotated[DeleteVehicleUseCase, Depends(get_delete_vehicle_use_case)],
) -> None:
    await use_case.execute(DeleteVehicleInput(tenant_id=current_user.tenant_id, vehicle_id=vehicle_id))
    await session.commit()


@router.post("/{vehicle_id}/photo", response_model=VehicleResponse)
async def upload_vehicle_photo(
    vehicle_id: UUID,
    current_user: CurrentUser,
    session: DbSession,
    use_case: Annotated[UploadVehiclePhotoUseCase, Depends(get_upload_vehicle_photo_use_case)],
    get_use_case: Annotated[GetVehicleUseCase, Depends(get_get_vehicle_use_case)],
    file: UploadFile = File(...),
) -> VehicleResponse:
    file_bytes = await file.read()
    await use_case.execute(
        UploadVehiclePhotoInput(
            tenant_id=current_user.tenant_id,
            vehicle_id=vehicle_id,
            filename=file.filename or "foto",
            file_bytes=file_bytes,
        )
    )
    # IMPORTANTE: busca de novo ANTES do commit, não depois — mesmo bug
    # de RLS já corrigido no módulo financeiro (o contexto de tenant do
    # RLS tem escopo de transação, é descartado no commit; buscar depois
    # rodaria sem contexto nenhum e o RLS bloquearia tudo).
    output = await get_use_case.execute(
        GetVehicleInput(tenant_id=current_user.tenant_id, vehicle_id=vehicle_id)
    )
    await session.commit()
    return VehicleResponse.model_validate(output)


@router.delete("/{vehicle_id}/photo", status_code=status.HTTP_204_NO_CONTENT)
async def remove_vehicle_photo(
    vehicle_id: UUID,
    current_user: CurrentUser,
    session: DbSession,
    use_case: Annotated[RemoveVehiclePhotoUseCase, Depends(get_remove_vehicle_photo_use_case)],
) -> None:
    await use_case.execute(RemoveVehiclePhotoInput(tenant_id=current_user.tenant_id, vehicle_id=vehicle_id))
    await session.commit()


@router.get("/{vehicle_id}/photo/download-url", response_model=VehiclePhotoDownloadResponse)
async def get_vehicle_photo_download_url(
    vehicle_id: UUID,
    current_user: CurrentUser,
    use_case: Annotated[GetVehiclePhotoDownloadUrlUseCase, Depends(get_vehicle_photo_download_url_use_case)],
) -> VehiclePhotoDownloadResponse:
    output = await use_case.execute(
        GetVehiclePhotoDownloadUrlInput(tenant_id=current_user.tenant_id, vehicle_id=vehicle_id)
    )
    return VehiclePhotoDownloadResponse(download_url=output.download_url, filename=output.filename)
