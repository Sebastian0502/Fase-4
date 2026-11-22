"""Error general del sistema."""
class ErrorSistema(Exception):
    """Error general del sistema."""
    pass


class ValidacionError(ErrorSistema):
    pass


class NoEncontradoError(ErrorSistema):
    pass


class OperacionNoPermitidaError(ErrorSistema):
    pass


class ServicioNoDisponibleError(ErrorSistema):
    pass


class CalculoError(ErrorSistema):
    pass


class ProcesamientoError(ErrorSistema):
    pass
