import os
from cryptography.fernet import Fernet
from django.db import models


def _fernet():
    key = os.environ.get('ENCRYPTION_KEY', '')
    if not key:
        raise RuntimeError('ENCRYPTION_KEY no configurado en variables de entorno')
    return Fernet(key.encode() if isinstance(key, str) else key)


class EncryptedField(models.TextField):
    """
    Campo que encripta con Fernet al guardar en DB y desencripta al leer.
    Los valores sensibles (tokens MP, contraseñas SMTP) nunca se persisten en plain text.
    """

    def from_db_value(self, value, expression, connection):
        if not value:
            return value
        try:
            return _fernet().decrypt(value.encode()).decode()
        except Exception:
            return value  # fallback si el valor no está encriptado (migración)

    def get_prep_value(self, value):
        if not value:
            return value
        return _fernet().encrypt(value.encode()).decode()

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        return name, path, args, kwargs
