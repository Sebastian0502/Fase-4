import re
from abc import ABC, abstractmethod
from decimal import Decimal
from enum import Enum
from typing import overload
from uuid import uuid4

from Excepciones import (
    CalculoError,
    ErrorSistema,
    OperacionNoPermitidaError,
    ServicioNoDisponibleError,
    ValidacionError,
)
from Utilidades import logger, texto, numero, entero_positivo


class Entidad(ABC):
    def __init__(self):
        self.__id = str(uuid4())

    @property
    def id(self):
        return self.__id

    @abstractmethod
    def describir(self):
        pass


class Cliente(Entidad):
    def __init__(self, nombre, correo, telefono):
        super().__init__()
        nombre = texto(nombre, "Nombre")
        correo = texto(correo, "Correo").lower()
        telefono = texto(telefono, "Teléfono")

        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo):
            raise ValidacionError("Correo inválido.")
        if not re.fullmatch(r"\+?[0-9]{7,15}", telefono):
            raise ValidacionError(
                "El teléfono debe tener entre 7 y 15 dígitos."
            )

        self.__nombre = nombre
        self.__correo = correo
        self.__telefono = telefono

    @property
    def nombre(self):
        return self.__nombre

    @property
    def correo(self):
        return self.__correo

    @property
    def telefono(self):
        return self.__telefono

    def describir(self):
        return f"Cliente: {self.nombre} | {self.correo}"


class Servicio(Entidad):
    def __init__(self, nombre, tarifa):
        super().__init__()
        self.__nombre = texto(nombre, "Servicio")
        self.__tarifa = numero(tarifa, "Tarifa", Decimal("0.01"))
        self.__activo = True

    @property
    def nombre(self):
        return self.__nombre

    @property
    def tarifa(self):
        return self.__tarifa

    @property
    def activo(self):
        return self.__activo

    def cambiar_disponibilidad(self, activo):
        if type(activo) is not bool:
            raise ValidacionError("La disponibilidad debe ser booleana.")
        self.__activo = activo

    @abstractmethod
    def validar_parametros(self, parametros):
        pass

    @abstractmethod
    def costo_base(self, duracion, parametros):
        pass

    @overload
    def calcular_costo(self, duracion) -> Decimal:
        ...

    @overload
    def calcular_costo(
        self, duracion, *, impuesto=0, descuento=0, **parametros
    ) -> Decimal:
        ...

    def calcular_costo(
        self, duracion, *, impuesto=0, descuento=0, **parametros
    ):
        horas = numero(duracion, "Duración", Decimal("0.01"))
        impuesto = numero(impuesto, "Impuesto")
        descuento = numero(descuento, "Descuento")

        if impuesto > 1 or descuento > 1:
            raise ValidacionError(
                "Impuesto y descuento deben estar entre 0 y 1."
            )

        self.validar_parametros(parametros)

        try:
            base = self.costo_base(horas, parametros)
            if not isinstance(base, Decimal):
                raise CalculoError("El costo base debe ser Decimal.")
            if not base.is_finite() or base < 0:
                raise CalculoError("Costo base inconsistente.")

            total = base * (Decimal("1") - descuento) * (Decimal("1") + impuesto)
            return total.quantize(Decimal("0.01"))
        except ArithmeticError as exc:
            raise CalculoError("No se pudo calcular el costo.") from exc


class Sala(Servicio):
    def __init__(self, nombre, tarifa, capacidad):
        super().__init__(nombre, tarifa)
        self.__capacidad = entero_positivo(capacidad, "Capacidad")

    def validar_parametros(self, parametros):
        if set(parametros) - {"personas"}:
            raise ValidacionError("Parámetros de sala desconocidos.")
        personas = entero_positivo(
            parametros.get("personas", 1), "Personas"
        )
        if personas > self.__capacidad:
            raise ValidacionError("Se supera la capacidad de la sala.")

    def costo_base(self, duracion, parametros):
        return self.tarifa * duracion

    def describir(self):
        return f"Sala: {self.nombre} | Capacidad: {self.__capacidad}"


class Equipo(Servicio):
    def __init__(self, nombre, tarifa, unidades):
        super().__init__(nombre, tarifa)
        self.__unidades = entero_positivo(unidades, "Unidades")

    def validar_parametros(self, parametros):
        if set(parametros) - {"cantidad"}:
            raise ValidacionError("Parámetros de equipo desconocidos.")
        cantidad = entero_positivo(
            parametros.get("cantidad", 1), "Cantidad"
        )
        if cantidad > self.__unidades:
            raise ServicioNoDisponibleError("No hay suficientes equipos.")

    def costo_base(self, duracion, parametros):
        return self.tarifa * duracion * parametros.get("cantidad", 1)

    def describir(self):
        return f"Equipo: {self.nombre} | Unidades: {self.__unidades}"


class Asesoria(Servicio):
    def __init__(self, nombre, tarifa, especialidad):
        super().__init__(nombre, tarifa)
        self.__especialidad = texto(especialidad, "Especialidad")

    def validar_parametros(self, parametros):
        if set(parametros) - {"urgente"}:
            raise ValidacionError("Parámetros de asesoría desconocidos.")
        if type(parametros.get("urgente", False)) is not bool:
            raise ValidacionError("Urgente debe ser booleano.")

    def costo_base(self, duracion, parametros):
        factor = (
            Decimal("1.25")
            if parametros.get("urgente", False)
            else Decimal("1")
        )
        return self.tarifa * duracion * factor

    def describir(self):
        return (
            f"Asesoría: {self.nombre} | "
            f"Especialidad: {self.__especialidad}"
        )


class Estado(Enum):
    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    COMPLETADA = "Completada"
    CANCELADA = "Cancelada"


class Reserva(Entidad):
    def __init__(
        self,
        cliente,
        servicio,
        duracion,
        *,
        impuesto=0,
        descuento=0,
        **parametros
    ):
        super().__init__()

        if not isinstance(cliente, Cliente):
            raise ValidacionError("Cliente inválido.")
        if not isinstance(servicio, Servicio):
            raise ValidacionError("Servicio inválido.")

        self.__cliente = cliente
        self.__servicio = servicio
        self.__duracion = numero(duracion, "Duración", Decimal("0.01"))
        self.__total = servicio.calcular_costo(
            self.__duracion,
            impuesto=impuesto,
            descuento=descuento,
            **parametros
        )
        self.__estado = Estado.PENDIENTE

    @property
    def servicio(self):
        return self.__servicio

    @property
    def estado(self):
        return self.__estado

    @property
    def total(self):
        return self.__total

    def confirmar(self):
        if self.estado is not Estado.PENDIENTE:
            raise OperacionNoPermitidaError(
                "Solo se confirman reservas pendientes."
            )
        if not self.servicio.activo:
            raise ServicioNoDisponibleError("Servicio desactivado.")
        self.__estado = Estado.CONFIRMADA

    def cancelar(self):
        if self.estado not in (
            Estado.PENDIENTE,
            Estado.CONFIRMADA,
        ):
            raise OperacionNoPermitidaError(
                "La reserva ya está cerrada."
            )
        self.__estado = Estado.CANCELADA

    def procesar(self):
        if self.estado is not Estado.CONFIRMADA:
            raise OperacionNoPermitidaError(
                "Primero debe confirmar la reserva."
            )

        try:
            if not self.servicio.activo:
                raise ServicioNoDisponibleError("Servicio desactivado.")
            if not self.total.is_finite() or self.total < 0:
                raise CalculoError("Importe inconsistente.")
        except ErrorSistema as exc:
            raise ProcesamientoError(
                "Procesamiento fallido; la reserva sigue confirmada."
            ) from exc
        else:
            self.__estado = Estado.COMPLETADA
        finally:
            logger.info(
                "Finalizó intento de procesamiento: %s",
                self.id
            )

    def describir(self):
        return (
            f"Reserva {self.id} | "
            f"{self.__cliente.nombre} | "
            f"{self.servicio.nombre} | "
            f"{self.estado.value} | "
            f"Total: {self.total}"
        )
