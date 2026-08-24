"""
Porta (interface) do repositório de StickeredVehicle.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from src.domain.vehicles.entities import StickeredVehicle


@dataclass(frozen=True)
class VehicleFilter:
    search_text: str | None = None  # busca em placa, nome do proprietário, ou modelo


@dataclass(frozen=True)
class VehiclePage:
    items: list[StickeredVehicle]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        if self.page_size == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size


class VehicleRepository(ABC):
    @abstractmethod
    async def save(self, vehicle: StickeredVehicle) -> None: ...

    @abstractmethod
    async def find_by_id(self, tenant_id: UUID, vehicle_id: UUID) -> StickeredVehicle | None: ...

    @abstractmethod
    async def list_paginated(
        self, tenant_id: UUID, filters: VehicleFilter, page: int, page_size: int
    ) -> VehiclePage: ...

    @abstractmethod
    async def count_total(self, tenant_id: UUID) -> int:
        """Contagem total de veículos ativos — usada no painel do início ("quantidade circulando")."""
