# Documentación Técnica

## Tecnologías

- **Lenguaje**: Python 3.11+
- **Framework API**: FastAPI
- **Servidor ASGI**: Uvicorn
- **Gestor de Paquetes y Entorno**: UV
- **Cliente HTTP**: Requests

## Arquitectura

La API sigue una arquitectura de microservicio simple. La lógica de negocio está separada de la capa de presentación (endpoints de FastAPI). Se utilizarán modelos de Pydantic para la validación de datos de entrada y salida.
