// URL de la API en Render (se define en Vercel como VITE_API_URL)
const API_URL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')
const ENDPOINT = `${API_URL}/api/v1/products`

// GET: obtener todos los productos
export async function getProducts() {
  const res = await fetch(ENDPOINT)
  if (!res.ok) throw new Error(`Error ${res.status} al cargar los productos`)
  return res.json()
}

// POST: registrar un producto nuevo
export async function createProduct(product) {
  const res = await fetch(ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(product),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    const detalle = Array.isArray(data.detalle) ? data.detalle.join(' ') : ''
    throw new Error(detalle || `Error ${res.status} al guardar el producto`)
  }
  return res.json()
}

// POST: preguntar al asistente de IA (Gemini)
export async function askAssistant(pregunta) {
  const res = await fetch(`${API_URL}/api/v1/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pregunta }),
  })
  if (!res.ok) throw new Error(`Error ${res.status} al consultar al asistente`)
  const data = await res.json()
  return data.respuesta
}
