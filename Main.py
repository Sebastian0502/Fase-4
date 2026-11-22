import logging

from entidades import Cliente
from excepciones import ErrorSistema
from reserva import Reserva
from servicios import (
        AlquilerEquipos,
        AsesoriaEspecializada,
        ReservaSalas,
    )
from sistema import SistemaSoftwareFJ


logging.basicConfig(
        filename="software_fj.log",
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        encoding="utf-8",
    )


def ejecutar_pruebas() -> None:
        sistema = SistemaSoftwareFJ()

        print("=== Demostración de Software FJ ===")

        # 1. Registro correcto de cliente.
        try:
            cliente = Cliente(
                "C001",
                "Ana Pérez",
                "ana@example.com",
            )
            sistema.registrar_cliente(cliente)
        except ErrorSistema as exc:
            logging.exception("No se pudo registrar el cliente.")
            print(f"Error controlado: {exc}")
        else:
            print("1. Cliente válido registrado.")

        # 2. Cliente inválido.
        try:
            Cliente("C002", "A", "correo-invalido")
        except ErrorSistema as exc:
            logging.exception("Intento de crear cliente inválido.")
            print(f"2. Cliente inválido rechazado: {exc}")

        # 3. Registro de otro cliente válido.
        try:
            cliente2 = Cliente(
                "C003",
                "Luis Gómez",
                "luis@example.com",
            )
            sistema.registrar_cliente(cliente2)
            print("3. Segundo cliente válido registrado.")
        except ErrorSistema as exc:
            logging.exception("Error al registrar segundo cliente.")
            print(f"Error controlado: {exc}")

       # 4, 5 y 6. Registro de servicios especializados.
servicios = [
    ReservaSalas("S001", 50, 20),
    AlquilerEquipos("S002", 30, 5),
    AsesoriaEspecializada(
        "S003",
        40,
        "Consultoría tecnológica",
    ),
]

for servicio in servicios:
    sistema.registrar_servicio(servicio)
