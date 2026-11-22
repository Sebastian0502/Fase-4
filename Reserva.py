import logging
from typing import Optional

from entidades import Cliente, Entidad
from excepciones import (
        ErrorOperacion,
        ErrorReserva,
        ErrorSistema,
        ErrorValidacion,
    )
from servicios import Servicio


class Reserva(Entidad):
        def _init_(
            self,
            identificador: str,
            cliente: Cliente,
            servicio: Servicio,
            duracion: float,
            parametros: Optional[dict] = None,
        ):
            super()._init_(identificador)

            if not isinstance(cliente, Cliente):
                raise ErrorValidacion("La reserva requiere un cliente válido.")

            if not isinstance(servicio, Servicio):
                raise ErrorValidacion("La reserva requiere un servicio válido.")

            self.cliente = cliente
            self.servicio = servicio
            self.duracion = duracion
            self.parametros = parametros or {}
            self.estado = "pendiente"
            self.total: Optional[float] = None

            try:
                self.servicio.validar_parametros(
                    self.duracion,
                    **self.parametros,
                )
            except Exception as exc:
                logging.exception(
                    "Error al crear la reserva %s",
                    identificador,
                )
                raise ErrorReserva(
                    f"No se pudo validar la reserva {identificador}."
                ) from exc

        def confirmar(self) -> None:
            try:
                if self.estado != "pendiente":
                    raise ErrorOperacion(
                        f"No se puede confirmar una reserva en estado "
                        f"'{self.estado}'."
                    )

                self.servicio.validar_disponibilidad()
                self.estado = "confirmada"
                logging.info("Reserva %s confirmada.", self.identificador)

            except ErrorSistema:
                logging.exception(
                    "Error al confirmar la reserva %s",
                    self.identificador,
                )
                raise

        def cancelar(self) -> None:
            try:
                if self.estado not in {"pendiente", "confirmada"}:
                    raise ErrorOperacion(
                        f"No se puede cancelar una reserva en estado "
                        f"'{self.estado}'."
                    )

                self.estado = "cancelada"
                logging.info("Reserva %s cancelada.", self.identificador)

            except ErrorSistema:
                logging.exception(
                    "Error al cancelar la reserva %s",
                    self.identificador,
                )
                raise

        def procesar(
            self,
            impuesto: float = 0.0,
            descuento: float = 0.0,
        ) -> float:
            try:
                if self.estado != "confirmada":
                    raise ErrorOperacion(
                        "Solo se pueden procesar reservas confirmadas."
                    )

                self.total = self.servicio.calcular_costo(
                    self.duracion,
                    impuesto,
                    descuento,
                )
                self.estado = "procesada"

                logging.info(
                    "Reserva %s procesada. Total: $%.2f.",
                    self.identificador,
                    self.total,
                )

                return self.total

            except ErrorSistema:
                logging.exception(
                    "Error al procesar la reserva %s",
                    self.identificador,
                )
                raise

            except Exception as exc:
                logging.exception(
                    "Error inesperado al procesar la reserva %s",
                    self.identificador,
                )
                raise ErrorReserva(
                    "Falló el procesamiento de la reserva."
                ) from exc

            finally:
                logging.info(
                    "Finalizó el intento de procesamiento de %s.",
                    self.identificador,
                )

        def describir(self) -> str:
            return (
                f"Reserva {self.identificador}: {self.cliente.nombre}, "
                f"{self.servicio.nombre}, estado {self.estado}"
            )
