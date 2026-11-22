import logging
from decimal import Decimal, InvalidOperation
from typing import Any

from Excepciones import ValidacionError


logger = logging.getLogger("SoftwareFJ")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    handler = logging.FileHandler(
        "software_fj.log",
        encoding="utf-8"
    )
handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    ))
logger.addHandler(handler)


def texto(valor, campo):
    if not isinstance(valor, str) or not valor.strip():
        raise ValidacionError(
            f"{campo}: se requiere texto no vacío."
        )
    return valor.strip()


def numero(valor, campo, minimo=Decimal("0")):
    if isinstance(valor, bool):
        raise ValidacionError(
            f"{campo}: no admite booleanos."
        )

    if not isinstance(valor, (str, int, float, Decimal)):
        raise ValidacionError(
            f"{campo}: tipo numérico inválido."
        )

    try:
        resultado = Decimal(str(valor))
    except (InvalidOperation, ValueError) as exc:
        raise ValidacionError(
            f"{campo}: número inválido."
        ) from exc

    if not resultado.is_finite() or resultado < minimo:
        raise ValidacionError(
            f"{campo}: debe ser finito y no menor que {minimo}."
        )

    return resultado


def entero_positivo(valor, campo):
    if type(valor) is not int or valor <= 0:
        raise ValidacionError(
            f"{campo}: debe ser un entero positivo."
        )
    return valor
