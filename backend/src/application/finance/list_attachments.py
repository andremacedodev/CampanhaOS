from src.application.finance.dto import FinanceAttachmentOutput, ListFinanceAttachmentsInput
from src.application.finance.exceptions import FinanceTransactionNotFoundError
from src.application.finance.mapper import attachment_to_output
from src.domain.finance.attachment_repository import FinanceAttachmentRepository
from src.domain.finance.repository import FinanceRepository


class ListFinanceAttachmentsUseCase:
    def __init__(
        self, finance_repository: FinanceRepository, attachment_repository: FinanceAttachmentRepository
    ) -> None:
        self._finance_repository = finance_repository
        self._attachment_repository = attachment_repository

    async def execute(self, input_data: ListFinanceAttachmentsInput) -> list[FinanceAttachmentOutput]:
        transaction = await self._finance_repository.find_by_id(input_data.tenant_id, input_data.transaction_id)
        if transaction is None or transaction.is_deleted:
            raise FinanceTransactionNotFoundError

        attachments = await self._attachment_repository.list_by_transaction(
            input_data.tenant_id, input_data.transaction_id
        )
        return [attachment_to_output(a) for a in attachments]
