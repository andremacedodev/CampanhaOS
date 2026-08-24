from src.application.vehicles.dto import ListVehiclesInput, ListVehiclesOutput
from src.application.vehicles.mapper import vehicle_to_output
from src.domain.vehicles.repository import VehicleFilter, VehicleRepository


class ListVehiclesUseCase:
    def __init__(self, vehicle_repository: VehicleRepository) -> None:
        self._vehicle_repository = vehicle_repository

    async def execute(self, input_data: ListVehiclesInput) -> ListVehiclesOutput:
        page = await self._vehicle_repository.list_paginated(
            tenant_id=input_data.tenant_id,
            filters=VehicleFilter(search_text=input_data.search_text),
            page=input_data.page,
            page_size=input_data.page_size,
        )
        return ListVehiclesOutput(
            items=[vehicle_to_output(v) for v in page.items],
            total=page.total,
            page=page.page,
            page_size=page.page_size,
            total_pages=page.total_pages,
        )
