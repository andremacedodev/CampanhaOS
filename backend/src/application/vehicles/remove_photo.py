from src.application.shared.file_storage_port import FileStoragePort
from src.application.vehicles.dto import RemoveVehiclePhotoInput
from src.application.vehicles.exceptions import NoPhotoError, VehicleNotFoundError
from src.domain.vehicles.repository import VehicleRepository


class RemoveVehiclePhotoUseCase:
    def __init__(self, vehicle_repository: VehicleRepository, file_storage: FileStoragePort) -> None:
        self._vehicle_repository = vehicle_repository
        self._file_storage = file_storage

    async def execute(self, input_data: RemoveVehiclePhotoInput) -> None:
        vehicle = await self._vehicle_repository.find_by_id(input_data.tenant_id, input_data.vehicle_id)
        if vehicle is None or vehicle.is_deleted:
            raise VehicleNotFoundError

        if vehicle.photo_storage_key is None:
            raise NoPhotoError

        storage_key = vehicle.photo_storage_key
        vehicle.remove_photo()
        await self._vehicle_repository.save(vehicle)

        await self._file_storage.delete(storage_key)
