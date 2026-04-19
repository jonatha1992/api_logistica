from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, String, Text,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class Negocio(Base):
    __tablename__ = "negocios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    api_key = Column(String(64), unique=True, index=True, nullable=False)

    # Credenciales Mercado Pago (encriptadas con Fernet)
    mp_access_token_enc = Column(Text, nullable=True)

    # URL a la que se notifica cuando un pago es aprobado
    webhook_notificacion = Column(String(500), nullable=True)

    # Credenciales SMTP (smtp_pass_enc encriptado con Fernet)
    smtp_host = Column(String(200), nullable=True)
    smtp_port = Column(Integer, default=587)
    smtp_user = Column(String(200), nullable=True)
    smtp_pass_enc = Column(Text, nullable=True)
    smtp_from = Column(String(200), nullable=True)

    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    transacciones = relationship("Transaccion", back_populates="negocio")
    plantillas = relationship("PlantillaEmail", back_populates="negocio")
    audit_logs = relationship("AuditLog", back_populates="negocio")


class Transaccion(Base):
    __tablename__ = "transacciones"

    id = Column(Integer, primary_key=True, index=True)
    negocio_id = Column(Integer, ForeignKey("negocios.id"), nullable=False)

    preference_id = Column(String(200), unique=True, index=True, nullable=True)
    payment_id = Column(String(200), nullable=True, index=True)
    external_reference = Column(String(200), nullable=True, index=True)

    amount = Column(Float, nullable=False)
    description = Column(String(500), nullable=True)
    customer_email = Column(String(200), nullable=True)

    # pending | approved | rejected | cancelled | in_process
    status = Column(String(50), default="pending", nullable=False)

    init_point = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)  # JSON serializado

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    negocio = relationship("Negocio", back_populates="transacciones")


class PlantillaEmail(Base):
    __tablename__ = "plantillas_email"

    id = Column(Integer, primary_key=True, index=True)
    negocio_id = Column(Integer, ForeignKey("negocios.id"), nullable=False)

    slug = Column(String(100), nullable=False)          # ej: "recupero-clave", "pago-confirmado"
    asunto = Column(String(500), nullable=False)         # soporta {{ variables }}
    cuerpo_html = Column(Text, nullable=False)           # soporta {{ variables }}

    activa = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    negocio = relationship("Negocio", back_populates="plantillas")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    negocio_id = Column(Integer, ForeignKey("negocios.id"), nullable=True)

    endpoint = Column(String(200), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    negocio = relationship("Negocio", back_populates="audit_logs")
