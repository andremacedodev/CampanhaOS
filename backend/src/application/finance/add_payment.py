"""
Caso de uso: registrar um pagamento individual contra uma despesa.

Permite quitação parcial em várias partes — cada chamada aqui cria um
FinancePayment separado, o status "pago/parcial/pendente/atrasado" é
sempre recalculado a partir da soma de TODOS os pagamentos já
registrados, nunca escolhido manualmente.
"""

from src.application.finance.dto import AddFinancePaymentInput, FinancePaymentOutput
from src.application.finance.exceptions import FinanceTransactionNotFoundError
from src.application.finance.mapper import payment_to_output
from src.domain.finance.entities import FinancePayment, PaymentsOnlyForExpensesError
from src.domain.finance.payment_repository import FinancePaymentRepository
from src.domain.finance.repository import FinanceRepository


class AddFinancePaymentUseCase:
    def __init__(self, finance_repository: FinanceRepository, payment_repository: FinancePaymentRepository) -> None:
        self._finance_repository = finance_repository
        self._payment_repository = payment_repository

    async def execute(self, input_data: AddFinancePaymentInput) -> FinancePaymentOutput:
        transaction = await self._finance_repository.find_by_id(input_data.tenant_id, input_data.transaction_id)
        if transaction is None or transaction.is_deleted:
            raise FinanceTransactionNotFoundError

        # Checagem explícita ANTES de criar o pagamento — receita/doação
        # não têm esse controle nessa versão (decisão de escopo do
        # usuário). FinancePayment.create() não sabe o TIPO da
        # transação (não tem acesso a ela), por isso a checagem mora
        # aqui na aplicação, não no próprio FinancePayment.
        if transaction.type != "despesa":
            raise PaymentsOnlyForExpensesError

        payment = FinancePayment.create(
            tenant_id=input_data.tenant_id,
            transaction_id=input_data.transaction_id,
            created_by_user_id=input_data.created_by_user_id,
            amount=input_data.amount,
            paid_at=input_data.paid_at,
        )
        await self._payment_repository.save(payment)
        return payment_to_output(payment)
