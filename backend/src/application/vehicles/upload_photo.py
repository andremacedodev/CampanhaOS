"""
Caso de uso: enviar (ou substituir) a foto de um veículo adesivado.

Mesma lógica já testada no módulo financeiro (UploadFinanceAttachmentUseCase)
— validação de tamanho/tipo ANTES do upload, e o antigo só é apagado do
R2 DEPOIS do novo já estar salvo com sucesso.
"""

import uuid
from dataclasses import dataclass
from uuid import UUID

from src.application.shared.exceptions import ApplicationError
from src.application.shared.file_storage_port import FileStoragePort
from src.application.vehicles.exceptions import UnsupportedPhotoTypeError, VehicleNotFoundError
from src.domain.vehicles.entities import MAX_PHOTO_SIZE_BYTES
from src.domain.vehicles.repository import VehicleRepository
from src.infrastructure.storage.file_signature import detect_content_type

_EXTENSION_BY_CONTENT_TYPE = {"image/jpeg": ".jpg", "image/png": ".png"}


class VehiclePhotoTooLargeError(ApplicationError):
    def __init__(self) -> None:
        super().__init__(f"Arquivo muito grande — limite de {MAX_PHOTO_SIZE_BYTES / 1024 / 1024:.0f}MB")


@dataclass(frozen=True)
class UploadVehiclePhotoInput:
    tenant_id: UUID
    vehicle_id: UUID
    filename: str
    file_bytes: bytes


class UploadVehiclePhotoUseCase:
    def __init__(self, vehicle_repository: VehicleRepository, file_storage: FileStoragePort) -> None:
        self._vehicle_repository = vehicle_repository
        self._file_storage = file_storage

    async def execute(self, input_data: UploadVehiclePhotoInput) -> None:
        vehicle = await self._vehicle_repository.find_by_id(input_data.tenant_id, input_data.vehicle_id)
        if vehicle is None or vehicle.is_deleted:
            raise VehicleNotFoundError

        if len(input_data.file_bytes) > MAX_PHOTO_SIZE_BYTES:
            raise VehiclePhotoTooLargeError

        real_content_type = detect_content_type(input_data.file_bytes)
        # Detecção de assinatura reconhece PDF também — mas foto de
        # veículo só aceita JPEG/PNG, então rejeita PDF aqui mesmo que a
        # assinatura seja válida (é um PDF de verdade, só não é o tipo
        # certo pra ESTE contexto).
        if real_content_type is None or real_content_type not in _EXTENSION_BY_CONTENT_TYPE:
            raise UnsupportedPhotoTypeError

        extension = _EXTENSION_BY_CONTENT_TYPE[real_content_type]
        storage_key = f"vehicle-photos/{input_data.tenant_id}/{input_data.vehicle_id}/{uuid.uuid4()}{extension}"

        previous_storage_key = vehicle.photo_storage_key

        await self._file_storage.upload(storage_key, input_data.file_bytes, real_content_type)

        vehicle.attach_photo(
            storage_key=storage_key,
            filename=input_data.filename,
            content_type=real_content_type,
            size_bytes=len(input_data.file_bytes),
        )
        await self._vehicle_repository.save(vehicle)

        if previous_storage_key:
            await self._file_storage.delete(previous_storage_key)
