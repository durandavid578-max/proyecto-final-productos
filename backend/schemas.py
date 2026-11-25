from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


# Base compartida
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, title="Nombre", description="Nombre del producto", examples=["Pañal NeneSoft M"])
    price: float = Field(..., ge=0, title="Precio", description="Precio en bolivianos (no puede ser negativo)", examples=[85.0])
    stock: int = Field(0, ge=0, title="Stock", description="Cantidad disponible", examples=[20])
    image_url: Optional[str] = Field(None, title="URL de imagen", description="Enlace a una foto del producto (opcional)", examples=[None])


# Datos requeridos al crear un producto (POST)
class ProductCreate(ProductBase):
    model_config = ConfigDict(
        json_schema_extra={"example": {"name": "Pañal NeneSoft M", "price": 85, "stock": 20, "image_url": None}}
    )


# Formato de respuesta que envía la API (incluye el id asignado por Supabase)
class ProductResponse(ProductBase):
    id: int = Field(..., title="ID", description="Número único asignado por la base de datos")

    model_config = ConfigDict(from_attributes=True)
