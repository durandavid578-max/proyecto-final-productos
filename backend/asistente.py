"""
Asistente de IA (Gemini) que responde preguntas sobre los productos.

Cómo funciona:
1. Lee todos los productos de la base de datos (Supabase).
2. Se los pasa a Gemini como "contexto" junto con la pregunta del usuario.
3. Gemini responde en español usando SOLO esos datos (precios y stock reales).
"""
import os

import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
API_BASE = "https://generativelanguage.googleapis.com/v1beta"

# Modelo a usar: se puede cambiar con la variable GEMINI_MODEL.
# "gemini-flash-latest" siempre apunta al modelo Flash más reciente.
_modelo = os.getenv("GEMINI_MODEL", "gemini-flash-latest").strip()

INSTRUCCIONES = (
    "Eres el asistente virtual de un catálogo de productos. "
    "Responde SIEMPRE en español, de forma breve, amable y clara. "
    "Usa ÚNICAMENTE la lista de productos que te doy (nombre, precio en bolivianos y stock). "
    "Si te preguntan por un producto que no está en la lista, di que no está registrado. "
    "No inventes precios ni cantidades. Los precios están en bolivianos (Bs)."
)


def _texto_productos(productos) -> str:
    if not productos:
        return "No hay productos registrados todavía."
    lineas = [
        f"- {p.name}: precio Bs {float(p.price):.2f}, stock {p.stock} unidades"
        for p in productos
    ]
    return "\n".join(lineas)


def _buscar_modelo_flash() -> str | None:
    """Si el modelo configurado no existe, busca automáticamente un modelo Flash disponible."""
    r = requests.get(f"{API_BASE}/models", params={"key": GEMINI_API_KEY, "pageSize": 100}, timeout=15)
    r.raise_for_status()
    candidatos = [
        m["name"].replace("models/", "")
        for m in r.json().get("models", [])
        if "generateContent" in m.get("supportedGenerationMethods", [])
        and "flash" in m["name"]
        and "lite" not in m["name"]
        and "image" not in m["name"]
        and "tts" not in m["name"]
        and "live" not in m["name"]
    ]
    return candidatos[0] if candidatos else None


def _llamar_gemini(modelo: str, prompt: str) -> requests.Response:
    return requests.post(
        f"{API_BASE}/models/{modelo}:generateContent",
        params={"key": GEMINI_API_KEY},
        json={
            "systemInstruction": {"parts": [{"text": INSTRUCCIONES}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        },
        timeout=40,
    )


def responder(pregunta: str, productos) -> str:
    global _modelo
    if not GEMINI_API_KEY:
        return "El asistente de IA no está configurado (falta la variable GEMINI_API_KEY)."

    prompt = f"Lista de productos disponibles:\n{_texto_productos(productos)}\n\nPregunta del cliente: {pregunta}"

    try:
        r = _llamar_gemini(_modelo, prompt)
        if r.status_code == 404:  # el modelo no existe: buscar otro automáticamente
            nuevo = _buscar_modelo_flash()
            if nuevo:
                _modelo = nuevo
                r = _llamar_gemini(_modelo, prompt)
        if r.status_code == 429:
            return "El asistente está recibiendo muchas consultas. Intenta de nuevo en un minuto."
        r.raise_for_status()
        partes = r.json()["candidates"][0]["content"]["parts"]
        return "".join(p.get("text", "") for p in partes).strip() or "No pude generar una respuesta."
    except Exception as e:
        print("Error con Gemini:", e)
        return "Lo siento, el asistente no pudo responder en este momento. Intenta de nuevo."
