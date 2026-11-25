"""
Asistente de IA (Gemini) que responde preguntas sobre los productos.

Cómo funciona:
1. Lee todos los productos de la base de datos (Supabase).
2. Se los pasa a Gemini como "contexto" junto con la pregunta del usuario.
3. Gemini responde en español usando SOLO esos datos (precios y stock reales).
4. Si Gemini está saturado, prueba con otros modelos; y si ninguno responde,
   contesta con una respuesta básica armada directamente desde la base de datos.
"""
import os
import time
import unicodedata

import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
API_BASE = "https://generativelanguage.googleapis.com/v1beta"
HEADERS = {"x-goog-api-key": GEMINI_API_KEY, "Content-Type": "application/json"}

# Modelo preferido (se puede cambiar con la variable GEMINI_MODEL)
MODELO_PREFERIDO = os.getenv("GEMINI_MODEL", "gemini-flash-latest").strip()
_modelos_disponibles: list[str] | None = None

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
    return "\n".join(f"- {p.name}: precio Bs {float(p.price):.2f}, stock {p.stock} unidades" for p in productos)


def _modelos_a_probar() -> list[str]:
    """Modelo preferido + otros modelos Flash disponibles en la cuenta (por si uno está saturado)."""
    global _modelos_disponibles
    if _modelos_disponibles is None:
        _modelos_disponibles = []
        try:
            r = requests.get(f"{API_BASE}/models", headers=HEADERS, params={"pageSize": 200}, timeout=15)
            r.raise_for_status()
            for m in r.json().get("models", []):
                nombre = m["name"].replace("models/", "")
                if (
                    "generateContent" in m.get("supportedGenerationMethods", [])
                    and "flash" in nombre
                    and not any(x in nombre for x in ("image", "tts", "live", "audio", "exp", "preview-tts"))
                ):
                    _modelos_disponibles.append(nombre)
        except Exception as e:
            print("Aviso: no se pudo listar modelos de Gemini:", e)
    lista = [MODELO_PREFERIDO] + [m for m in _modelos_disponibles if m != MODELO_PREFERIDO]
    return lista[:6]


def _llamar_gemini(modelo: str, prompt: str) -> requests.Response:
    return requests.post(
        f"{API_BASE}/models/{modelo}:generateContent",
        headers=HEADERS,
        json={
            "systemInstruction": {"parts": [{"text": INSTRUCCIONES}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        },
        timeout=30,
    )


def _sin_tildes(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", t.lower()) if unicodedata.category(c) != "Mn")


def respuesta_basica(pregunta: str, productos) -> str:
    """Respuesta de respaldo sin IA: busca el producto mencionado directamente en la base de datos."""
    if not productos:
        return "Aún no hay productos registrados."
    q = _sin_tildes(pregunta)
    palabras = [w for w in q.replace("?", " ").replace("¿", " ").split() if len(w) > 2]
    puntajes = [(sum(w in _sin_tildes(p.name) for w in palabras), p) for p in productos]
    mejor = max((pt for pt, _ in puntajes), default=0)
    encontrados = [p for pt, p in puntajes if pt == mejor and pt > 0]
    if "barat" in q:
        p = min(productos, key=lambda x: float(x.price))
        return f"El producto más barato es {p.name}: Bs {float(p.price):.2f} (stock: {p.stock})."
    if "car" in q.split() or "mas caro" in q:
        p = max(productos, key=lambda x: float(x.price))
        return f"El producto más caro es {p.name}: Bs {float(p.price):.2f} (stock: {p.stock})."
    if "mas stock" in q or "mayor stock" in q:
        p = max(productos, key=lambda x: x.stock)
        return f"El producto con más stock es {p.name}: {p.stock} unidades."
    if encontrados:
        return "\n".join(
            f"{p.name}: Bs {float(p.price):.2f} — {'stock: ' + str(p.stock) + ' unidades' if p.stock > 0 else 'agotado'}"
            for p in encontrados
        )
    return "Estos son los productos disponibles:\n" + "\n".join(
        f"• {p.name} — Bs {float(p.price):.2f} (stock: {p.stock})" for p in productos
    )


def responder(pregunta: str, productos) -> str:
    if not GEMINI_API_KEY:
        return respuesta_basica(pregunta, productos)

    prompt = f"Lista de productos disponibles:\n{_texto_productos(productos)}\n\nPregunta del cliente: {pregunta}"

    for modelo in _modelos_a_probar():
        for intento in range(2):
            try:
                r = _llamar_gemini(modelo, prompt)
            except requests.RequestException as e:
                print(f"Gemini ({modelo}) sin conexión:", type(e).__name__)
                break
            if r.status_code == 200:
                try:
                    partes = r.json()["candidates"][0]["content"]["parts"]
                    texto = "".join(p.get("text", "") for p in partes).strip()
                    if texto:
                        return texto
                except (KeyError, IndexError):
                    pass
                break
            print(f"Gemini ({modelo}) respondió {r.status_code}")
            if r.status_code in (500, 503) and intento == 0:
                time.sleep(1.5)  # saturado: esperar un poco y reintentar una vez
                continue
            break  # 404, 429, 403...: pasar al siguiente modelo

    # Ningún modelo respondió: respuesta directa desde la base de datos
    return respuesta_basica(pregunta, productos)
