
import logging

from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.db import connection
from django.dispatch import receiver

logger = logging.getLogger("auditoria_seguridad")


def obtener_ip(request):
    if request is not None:
        return request.META.get("REMOTE_ADDR", "desconocida")
    return "desconocida"


def guardar_auditoria(accion, descripcion):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO auditoria
                (id_usuario, accion, descripcion)
                VALUES (NULL, %s, %s)
                """,
                [accion, descripcion],
            )
    except Exception:
        logger.exception(
            "No se pudo guardar el evento de auditoría: %s",
            accion,
        )


@receiver(user_logged_in)
def registrar_inicio_sesion(sender, request, user, **kwargs):
    descripcion = (
        f"Usuario Django: {user.username} "
        f"(ID: {user.pk}) | IP: {obtener_ip(request)}"
    )
    guardar_auditoria("INICIO_SESION", descripcion)
    logger.info("INICIO_SESION | %s", descripcion)


@receiver(user_logged_out)
def registrar_cierre_sesion(sender, request, user, **kwargs):
    nombre = user.username if user else "desconocido"
    identificador = user.pk if user else "desconocido"

    descripcion = (
        f"Usuario Django: {nombre} "
        f"(ID: {identificador}) | IP: {obtener_ip(request)}"
    )
    guardar_auditoria("CIERRE_SESION", descripcion)
    logger.info("CIERRE_SESION | %s", descripcion)


@receiver(user_login_failed)
def registrar_acceso_fallido(sender, credentials, request, **kwargs):
    nombre = credentials.get("username", "desconocido")
    descripcion = (
        f"Usuario declarado: {nombre} | "
        f"IP: {obtener_ip(request)}"
    )
    guardar_auditoria("ACCESO_FALLIDO", descripcion)
    logger.warning("ACCESO_FALLIDO | %s", descripcion)
