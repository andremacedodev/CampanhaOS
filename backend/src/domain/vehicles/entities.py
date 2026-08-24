"""
Entidade de domínio: StickeredVehicle (veículo adesivado).

Proprietário pode ser um Voter já cadastrado (`voter_id`) OU só um nome
livre (`owner_name`) — a pessoa não precisa estar cadastrada como
eleitor pra ter o carro registrado aqui. `owner_name` é sempre
obrigatório (mesmo com `voter_id` preenchido) — evita ter que ir buscar
o nome em outro lugar toda vez que só precisa exibir a lista.
"""

import re
from dataclasses import dataclass
from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from src.domain.shared.exceptions import DomainError

# Cobre os dois formatos de placa brasileira:
# - Antigo: 3 letras + 4 dígitos (ABC1234)
# - Mercosul: 3 letras + 1 dígito + 1 letra + 2 dígitos (ABC1D23)
# A 5ª posição é o que diferencia (dígito no antigo, letra no Mercosul) —
# por isso aceita letra OU dígito ali, e dígito fixo nas duas últimas.
_PLATE_PATTERN = re.compile(r"^[A-Z]{3}\d[A-Z0-9]\d{2}$")

VALID_PHOTO_CONTENT_TYPES = frozenset({"image/jpeg", "image/png"})
MAX_PHOTO_SIZE_BYTES = 10 * 1024 * 1024  # 10MB


class InvalidPlateError(DomainError):
    def __init__(self, value: str) -> None:
        super().__init__(f"Placa '{value}' inválida — formato esperado: ABC1234 ou ABC1D23 (Mercosul)")


class InvalidOwnerNameError(DomainError):
    def __init__(self) -> None:
        super().__init__("Nome do proprietário não pode ser vazio")


class InvalidPhotoError(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


def _normalize_plate(raw_plate: str) -> str:
    return raw_plate.strip().upper().replace("-", "").replace(" ", "")


@dataclass
class StickeredVehicle:
    id: UUID
    tenant_id: UUID
    created_by_user_id: UUID
    plate: str
    owner_name: str
    voter_id: UUID | None
    model: str | None
    city: str | None
    stickered_at: date
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    photo_storage_key: str | None = None
    photo_filename: str | None = None
    photo_content_type: str | None = None
    photo_size_bytes: int | None = None

    @staticmethod
    def create(
        tenant_id: UUID,
        created_by_user_id: UUID,
        plate: str,
        owner_name: str,
        stickered_at: date,
        voter_id: UUID | None = None,
        model: str | None = None,
        city: str | None = None,
    ) -> "StickeredVehicle":
        normalized_plate = _normalize_plate(plate)
        StickeredVehicle._validate_plate(normalized_plate)
        StickeredVehicle._validate_owner_name(owner_name)

        now = datetime.now(UTC)
        return StickeredVehicle(
            id=uuid4(),
            tenant_id=tenant_id,
            created_by_user_id=created_by_user_id,
            plate=normalized_plate,
            owner_name=owner_name.strip(),
            voter_id=voter_id,
            model=model.strip() if model else None,
            city=city.strip() if city else None,
            stickered_at=stickered_at,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _validate_plate(plate: str) -> None:
        if not _PLATE_PATTERN.match(plate):
            raise InvalidPlateError(plate)

    @staticmethod
    def _validate_owner_name(owner_name: str) -> None:
        if not owner_name or not owner_name.strip():
            raise InvalidOwnerNameError

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def update_details(
        self,
        *,
        plate: str | None = None,
        owner_name: str | None = None,
        model: str | None = None,
        city: str | None = None,
        stickered_at: date | None = None,
        voter_id: UUID | None = None,
    ) -> None:
        if plate is not None:
            normalized_plate = _normalize_plate(plate)
            StickeredVehicle._validate_plate(normalized_plate)
            self.plate = normalized_plate
        if owner_name is not None:
            StickeredVehicle._validate_owner_name(owner_name)
            self.owner_name = owner_name.strip()
        if model is not None:
            self.model = model.strip() or None
        if city is not None:
            self.city = city.strip() or None
        if stickered_at is not None:
            self.stickered_at = stickered_at
        if voter_id is not None:
            self.voter_id = voter_id

        self.updated_at = datetime.now(UTC)

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(UTC)

    def attach_photo(self, storage_key: str, filename: str, content_type: str, size_bytes: int) -> None:
        """Mesma regra do anexo financeiro: substitui a foto anterior, um anexo só por vez."""
        if content_type not in VALID_PHOTO_CONTENT_TYPES:
            raise InvalidPhotoError(f"Tipo de arquivo '{content_type}' não permitido. Aceitos: JPEG, PNG.")
        if size_bytes <= 0:
            raise InvalidPhotoError("Arquivo vazio")
        if size_bytes > MAX_PHOTO_SIZE_BYTES:
            raise InvalidPhotoError(
                f"Arquivo muito grande ({size_bytes / 1024 / 1024:.1f}MB) — limite de "
                f"{MAX_PHOTO_SIZE_BYTES / 1024 / 1024:.0f}MB"
            )

        self.photo_storage_key = storage_key
        self.photo_filename = filename
        self.photo_content_type = content_type
        self.photo_size_bytes = size_bytes
        self.updated_at = datetime.now(UTC)

    def remove_photo(self) -> None:
        self.photo_storage_key = None
        self.photo_filename = None
        self.photo_content_type = None
        self.photo_size_bytes = None
        self.updated_at = datetime.now(UTC)
