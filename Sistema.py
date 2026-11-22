import logging

from entidades import Cliente
from excepciones import ErrorOperacion, ErrorValidacion
from reserva import Reserva
from servicios import Servicio


class SistemaSoftwareFJ:
        """Administra las listas en memoria."""

        def _init_(self):
            self.clientes: list[Cliente] = []
            self.servicios: list[Servicio] = []
            self.reservas: list[Reserva] = []

        def registrar_cliente(self, cliente: Cliente) -> None:
            if not isinstance(cliente, Cliente):
                raise ErrorValidacion("El objeto recibido no es un cliente.")

            if any(
                elemento.identificador == cliente.identificador
                for elemento in self.clientes
            ):
                raise ErrorOperacion(
                    "Ya existe un cliente con ese identificador."
                )

            self.clientes.append(cliente)
            logging.info("Cliente registrado: %s.", cliente.identificador)

        def registrar_servicio(self, servicio: Servicio) -> None:
            if not isinstance(servicio, Servicio):
                raise ErrorValidacion("El objeto recibido no es un servicio.")

            if any(
                elemento.identificador == servicio.identificador
                for elemento in self.servicios
            ):
                raise ErrorOperacion(
                    "Ya existe un servicio con ese identificador."
                )

            self.servicios.append(servicio)
            logging.info("Servicio registrado: %s.", servicio.identificador)

        def registrar_reserva(self, reserva: Reserva) -> None:
            if not isinstance(reserva, Reserva):
                raise ErrorValidacion("El objeto recibido no es una reserva.")

            if any(
                elemento.identificador == reserva.identificador
                for elemento in self.reservas
            ):
                raise ErrorOperacion(
                    "Ya existe una reserva con ese identificador."
                )

            self.reservas.append(reserva)
            logging.info("Reserva registrada: %s.", reserva.identificador)
