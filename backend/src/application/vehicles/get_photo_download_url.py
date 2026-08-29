from src.application.shared.file_storage_port import FileStoragePort
from src.application.vehicles.dto import GetVehiclePhotoDownloadUrlInput, GetVehiclePhotoDownloadUrlOutput
from src.application.vehicles.exceptions import NoPhotoError, VehicleNotFoundError
from src.domain.vehicles.repository import VehicleRepository


class GetVehiclePhotoDownloadUrlUseCase:
    def __init__(self, vehicle_repository: VehicleRepository, file_storage: FileStoragePort) -> None:
        self._vehicle_repository = vehicle_repository
        self._file_storage = file_storage

    async def execute(self, input_data: GetVehiclePhotoDownloadUrlInput) -> GetVehiclePhotoDownloadUrlOutput:
        vehicle = await self._vehicle_repository.find_by_id(input_data.tenant_id, input_data.vehicle_id)
        if vehicle is None or vehicle.is_deleted:
            raise VehicleNotFoundError

        if vehicle.photo_storage_key is None or vehicle.photo_filename is None:
            raise NoPhotoError

        download_url = await self._file_storage.generate_download_url(vehicle.photo_storage_key)
        return GetVehiclePhotoDownloadUrlOutput(download_url=download_url, filename=vehicle.photo_filename)
