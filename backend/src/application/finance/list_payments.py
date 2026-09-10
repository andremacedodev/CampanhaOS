from src.application.finance.dto import FinancePaymentOutput, ListFinancePaymentsInput
from src.application.finance.exceptions import FinanceTransactionNotFoundError
from src.application.finance.mapper import payment_to_output
from src.domain.finance.payment_repository import FinancePaymentRepository
from src.domain.finance.repository import FinanceRepository


class ListFinancePaymentsUseCase:
    def __init__(self, finance_repository: FinanceRepository, payment_repository: FinancePaymentRepository) -> None:
        self._finance_repository = finance_repository
        self._payment_repository = payment_repository

    async def execute(self, input_data: ListFinancePaymentsInput) -> list[FinancePaymentOutput]:
        transaction = await self._finance_repository.find_by_id(input_data.tenant_id, input_data.transaction_id)
        if transaction is None or transaction.is_deleted:
            raise FinanceTransactionNotFoundError

        payments = await self._payment_repository.list_by_transaction(
            input_data.tenant_id, input_data.transaction_id
        )
        return [payment_to_output(p) for p in payments]
