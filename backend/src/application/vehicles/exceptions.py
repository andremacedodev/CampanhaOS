from src.application.shared.exceptions import ApplicationError


class VehicleNotFoundError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("Veículo não encontrado")


class NoPhotoError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("Este veículo não tem nenhuma foto")


class UnsupportedPhotoTypeError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("Tipo de arquivo não reconhecido — apenas JPEG ou PNG são aceitos")
