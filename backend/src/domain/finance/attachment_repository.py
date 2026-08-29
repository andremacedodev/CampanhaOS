"""
Porta (interface) do repositório de FinanceAttachment.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.finance.entities import FinanceAttachment


class FinanceAttachmentRepository(ABC):
    @abstractmethod
    async def save(self, attachment: FinanceAttachment) -> None: ...

    @abstractmethod
    async def find_by_id(self, tenant_id: UUID, attachment_id: UUID) -> FinanceAttachment | None: ...

    @abstractmethod
    async def list_by_transaction(self, tenant_id: UUID, transaction_id: UUID) -> list[FinanceAttachment]: ...

    @abstractmethod
    async def count_by_transaction(self, tenant_id: UUID, transaction_id: UUID) -> int:
        """Usado pra checar o limite de anexos ANTES de permitir um upload novo."""

    @abstractmethod
    async def delete(self, tenant_id: UUID, attachment_id: UUID) -> None:
        """Remove a referência do banco — quem chama é responsável por apagar o arquivo do R2 separadamente."""
