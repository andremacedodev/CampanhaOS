"""
Injeção de dependência (composition root) do módulo de veículos.
"""

from typing import Annotated

from fastapi import Depends

from src.application.vehicles.create_vehicle import CreateVehicleUseCase
from src.application.vehicles.delete_vehicle import DeleteVehicleUseCase
from src.application.vehicles.get_photo_download_url import GetVehiclePhotoDownloadUrlUseCase
from src.application.vehicles.get_vehicle import GetVehicleUseCase
from src.application.vehicles.list_vehicles import ListVehiclesUseCase
from src.application.vehicles.remove_photo import RemoveVehiclePhotoUseCase
from src.application.vehicles.update_vehicle import UpdateVehicleUseCase
from src.application.vehicles.upload_photo import UploadVehiclePhotoUseCase
from src.infrastructure.database.repositories.vehicle_repository import SqlAlchemyVehicleRepository
from src.presentation.api.dependencies import DbSession
from src.presentation.api.finance_dependencies import FileStorageDep
from src.presentation.api.voters_dependencies import VoterRepositoryDep


def get_vehicle_repository(session: DbSession) -> SqlAlchemyVehicleRepository:
    return SqlAlchemyVehicleRepository(session)


VehicleRepositoryDep = Annotated[SqlAlchemyVehicleRepository, Depends(get_vehicle_repository)]


def get_create_vehicle_use_case(
    vehicle_repository: VehicleRepositoryDep, voter_repository: VoterRepositoryDep
) -> CreateVehicleUseCase:
    return CreateVehicleUseCase(vehicle_repository, voter_repository)


def get_get_vehicle_use_case(vehicle_repository: VehicleRepositoryDep) -> GetVehicleUseCase:
    return GetVehicleUseCase(vehicle_repository)


def get_list_vehicles_use_case(vehicle_repository: VehicleRepositoryDep) -> ListVehiclesUseCase:
    return ListVehiclesUseCase(vehicle_repository)


def get_update_vehicle_use_case(
    vehicle_repository: VehicleRepositoryDep, voter_repository: VoterRepositoryDep
) -> UpdateVehicleUseCase:
    return UpdateVehicleUseCase(vehicle_repository, voter_repository)


def get_delete_vehicle_use_case(vehicle_repository: VehicleRepositoryDep) -> DeleteVehicleUseCase:
    return DeleteVehicleUseCase(vehicle_repository)


def get_upload_vehicle_photo_use_case(
    vehicle_repository: VehicleRepositoryDep, file_storage: FileStorageDep
) -> UploadVehiclePhotoUseCase:
    return UploadVehiclePhotoUseCase(vehicle_repository, file_storage)


def get_remove_vehicle_photo_use_case(
    vehicle_repository: VehicleRepositoryDep, file_storage: FileStorageDep
) -> RemoveVehiclePhotoUseCase:
    return RemoveVehiclePhotoUseCase(vehicle_repository, file_storage)


def get_vehicle_photo_download_url_use_case(
    vehicle_repository: VehicleRepositoryDep, file_storage: FileStorageDep
) -> GetVehiclePhotoDownloadUrlUseCase:
    return GetVehiclePhotoDownloadUrlUseCase(vehicle_repository, file_storage)