from src.application.finance.dto import FinanceTransactionOutput, GetFinanceTransactionInput
from src.application.finance.exceptions import FinanceTransactionNotFoundError
from src.application.finance.mapper import transaction_to_output
from src.domain.finance.attachment_repository import FinanceAttachmentRepository
from src.domain.finance.repository import FinanceRepository


class GetFinanceTransactionUseCase:
    def __init__(
        self, finance_repository: FinanceRepository, attachment_repository: FinanceAttachmentRepository
    ) -> None:
        self._finance_repository = finance_repository
        self._attachment_repository = attachment_repository

    async def execute(self, input_data: GetFinanceTransactionInput) -> FinanceTransactionOutput:
        transaction = await self._finance_repository.find_by_id(
            input_data.tenant_id, input_data.transaction_id
        )
        if transaction is None or transaction.is_deleted:
            raise FinanceTransactionNotFoundError

        attachment_count = await self._attachment_repository.count_by_transaction(
            input_data.tenant_id, input_data.transaction_id
        )
        return transaction_to_output(transaction, attachment_count=attachment_count)
