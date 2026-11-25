// Colores para el cubo 3D y las tarjetas (cambia según el id del producto)
export const PALETA = ['#6366f1', '#ec4899', '#14b8a6', '#f59e0b', '#8b5cf6', '#0ea5e9', '#22c55e', '#ef4444']
export const colorDe = (p) => (p ? PALETA[p.id % PALETA.length] : PALETA[0])
