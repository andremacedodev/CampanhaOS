from src.application.shared.exceptions import ApplicationError


class FinanceTransactionNotFoundError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("Lançamento financeiro não encontrado")


class FinanceAttachmentNotFoundError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("Anexo não encontrado")


class FinancePaymentNotFoundError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("Pagamento não encontrado")


class UnsupportedFileTypeError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("Tipo de arquivo não reconhecido — apenas JPEG, PNG ou PDF são aceitos")
