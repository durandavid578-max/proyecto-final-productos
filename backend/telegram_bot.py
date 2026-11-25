"""
Bot de Telegram: recibe mensajes y responde usando el mismo asistente de IA.

Funciona con "webhook": Telegram envía cada mensaje a nuestra API en
/telegram/webhook y nosotros respondemos con sendMessage.
"""
import os

import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

BIENVENIDA = (
    "¡Hola! 👋 Soy el asistente del Catálogo de Productos.\n\n"
    "Pregúntame por precios o stock, por ejemplo:\n"
    "• ¿Cuánto cuesta el pañal NeneSoft M?\n"
    "• ¿Qué productos tienen stock?\n"
    "• ¿Cuál es el producto más barato?\n\n"
    "Comando: /productos para ver la lista completa."
)


def activo() -> bool:
    return bool(TELEGRAM_BOT_TOKEN)


def enviar_mensaje(chat_id: int, texto: str):
    try:
        requests.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": texto}, timeout=15)
    except requests.RequestException as e:
        print("Error enviando mensaje a Telegram:", e)


def configurar_webhook(url_publica: str) -> dict:
    """Le dice a Telegram a qué dirección debe enviar los mensajes."""
    r = requests.post(
        f"{API}/setWebhook",
        json={"url": f"{url_publica.rstrip('/')}/telegram/webhook", "drop_pending_updates": True},
        timeout=15,
    )
    return r.json()


def lista_productos(productos) -> str:
    if not productos:
        return "Aún no hay productos registrados."
    lineas = [f"• {p.name} — Bs {float(p.price):.2f} (stock: {p.stock})" for p in productos]
    return "📦 Productos disponibles:\n\n" + "\n".join(lineas)
