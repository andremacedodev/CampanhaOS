from src.application.finance.dto import RemoveFinancePaymentInput
from src.application.finance.exceptions import FinancePaymentNotFoundError
from src.domain.finance.payment_repository import FinancePaymentRepository


class RemoveFinancePaymentUseCase:
    def __init__(self, payment_repository: FinancePaymentRepository) -> None:
        self._payment_repository = payment_repository

    async def execute(self, input_data: RemoveFinancePaymentInput) -> None:
        payment = await self._payment_repository.find_by_id(input_data.tenant_id, input_data.payment_id)
        if payment is None or payment.transaction_id != input_data.transaction_id:
            raise FinancePaymentNotFoundError

        await self._payment_repository.delete(input_data.tenant_id, input_data.payment_id)
