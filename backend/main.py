import os
from typing import List

import requests
from fastapi import FastAPI, Depends, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db

# Crea la tabla en Supabase automáticamente si aún no existe
try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print("Aviso: no se pudo verificar la tabla al iniciar:", e)

app = FastAPI(
    title="API de Catálogo de Productos",
    version="1.0.0",
    description=(
        "Servicio backend del Proyecto Final.\n\n"
        "- **Base de datos:** PostgreSQL en Supabase (tabla `products`)\n"
        "- **Servidor:** FastAPI desplegado en Render\n\n"
        "Para probar: abre un endpoint, presiona **Try it out** y luego **Execute**."
    ),
    openapi_tags=[
        {"name": "Estado", "description": "Comprobar que la API está encendida"},
        {"name": "Productos", "description": "Ver y registrar productos del catálogo"},
    ],
)

# Habilitar CORS para permitir llamadas desde Vercel o desarrollo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción puedes acotarlo al dominio de Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CAMPOS = {"name": "nombre", "price": "precio", "stock": "stock", "image_url": "URL de imagen"}


# Mensajes de error de validación en español
@app.exception_handler(RequestValidationError)
async def errores_en_espanol(request: Request, exc: RequestValidationError):
    errores = []
    for e in exc.errors():
        campo = CAMPOS.get(str(e["loc"][-1]), str(e["loc"][-1]))
        tipo = e["type"]
        if tipo == "missing":
            msg = f"El campo '{campo}' es obligatorio."
        elif tipo == "greater_than_equal":
            msg = f"El campo '{campo}' no puede ser negativo."
        elif tipo == "string_too_short":
            msg = f"El campo '{campo}' no puede estar vacío."
        elif tipo in ("float_parsing", "int_parsing", "int_from_float"):
            msg = f"El campo '{campo}' debe ser un número válido."
        else:
            msg = f"El campo '{campo}' no es válido."
        errores.append(msg)
    return JSONResponse(status_code=422, content={"detalle": errores})


SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def avisar_slack(producto: models.Product):
    """Herramienta 2 (Slack - Opción B): envía un aviso al canal cuando se crea un producto."""
    if not SLACK_WEBHOOK_URL:
        return
    try:
        requests.post(
            SLACK_WEBHOOK_URL,
            json={"text": f"¡Nuevo producto registrado en el inventario! 🛒 {producto.name} - Bs {producto.price} (stock: {producto.stock})"},
            timeout=5,
        )
    except requests.RequestException:
        pass  # Si Slack falla, el producto igual se guarda


@app.get("/", tags=["Estado"], summary="Estado de la API")
def raiz():
    return {"mensaje": "API de productos funcionando", "documentacion": "/docs"}


# 1. Obtener todos los productos
@app.get(
    "/api/v1/products",
    response_model=List[schemas.ProductResponse],
    tags=["Productos"],
    summary="Listar productos",
    description="Devuelve todos los productos guardados en Supabase, del más nuevo al más antiguo.",
    response_description="Lista de productos",
)
def list_products(db: Session = Depends(get_db)):
    return db.query(models.Product).order_by(models.Product.id.desc()).all()


# 2. Registrar un nuevo producto
@app.post(
    "/api/v1/products",
    response_model=schemas.ProductResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Productos"],
    summary="Registrar producto",
    description="Guarda un producto nuevo en Supabase y devuelve el producto con su ID asignado.",
    response_description="Producto creado correctamente",
)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    nuevo_producto = models.Product(**product.model_dump())
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
    avisar_slack(nuevo_producto)
    return nuevo_producto
