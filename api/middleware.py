from fastapi import Depends, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from .database import SessionLocal, get_db
from .models import AuditLog, Negocio


def get_tenant(
    authorization: str = Header(..., description="Bearer <API_KEY_DEL_NEGOCIO>"),
    db: Session = Depends(get_db),
) -> Negocio:
    """
    Dependency que valida la API key y retorna el Negocio correspondiente.
    Inyecta dinámicamente el contexto del tenant para cada petición.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Formato inválido. Usar: Authorization: Bearer <API_KEY>",
        )

    api_key = authorization.removeprefix("Bearer ").strip()

    negocio = (
        db.query(Negocio)
        .filter(Negocio.api_key == api_key, Negocio.activo == True)  # noqa: E712
        .first()
    )

    if not negocio:
        raise HTTPException(status_code=401, detail="API key inválida o negocio inactivo")

    return negocio


async def audit_log_middleware(request: Request, call_next):
    """
    Middleware HTTP que registra cada interacción autenticada en audit_logs.
    Permite debugear si un correo o pago falló en un negocio específico.
    """
    response = await call_next(request)

    negocio: Negocio | None = getattr(request.state, "negocio", None)
    if negocio is not None:
        db = SessionLocal()
        try:
            log = AuditLog(
                negocio_id=negocio.id,
                endpoint=str(request.url.path),
                method=request.method,
                status_code=response.status_code,
            )
            db.add(log)
            db.commit()
        except Exception:
            pass
        finally:
            db.close()

    return response


async def set_tenant_state_middleware(request: Request, call_next):
    """
    Middleware auxiliar: resuelve la API key y guarda el Negocio en request.state
    para que audit_log_middleware pueda accederlo.
    """
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        api_key = auth.removeprefix("Bearer ").strip()
        db = SessionLocal()
        try:
            negocio = (
                db.query(Negocio)
                .filter(Negocio.api_key == api_key, Negocio.activo == True)  # noqa: E712
                .first()
            )
            if negocio:
                request.state.negocio = negocio
        finally:
            db.close()

    return await call_next(request)
