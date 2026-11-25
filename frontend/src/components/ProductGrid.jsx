import { colorDe } from '../colors'

export function ProductGrid({ products, selected, onSelect }) {
  if (products.length === 0) {
    return (
      <div className="text-center py-12 bg-slate-900/60 rounded-2xl ring-1 ring-white/10">
        <p className="text-4xl mb-2">📭</p>
        <p className="text-slate-400">Aún no hay productos. ¡Registra el primero!</p>
      </div>
    )
  }
  return (
    <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
      {products.map((p) => {
        const activo = selected?.id === p.id
        return (
          <button
            key={p.id}
            onClick={() => onSelect(p)}
            className={`group text-left bg-slate-900/80 rounded-2xl overflow-hidden ring-1 transition hover:-translate-y-1 ${
              activo ? 'ring-2 ring-indigo-400 shadow-xl shadow-indigo-900/40' : 'ring-white/10 hover:ring-white/30'
            }`}
          >
            {p.image_url ? (
              <img src={p.image_url} alt={p.name} className="h-40 w-full object-cover" />
            ) : (
              <div className="h-40 w-full flex items-center justify-center text-5xl" style={{ background: `linear-gradient(135deg, ${colorDe(p)}55, ${colorDe(p)}15)` }}>
                📦
              </div>
            )}
            <div className="p-4 space-y-2">
              <h3 className="font-semibold text-white leading-tight">{p.name}</h3>
              <div className="flex items-center justify-between">
                <span className="text-xl font-bold text-indigo-300">Bs {Number(p.price).toFixed(2)}</span>
                <span
                  className={`text-xs px-2 py-1 rounded-full ${
                    p.stock > 10 ? 'bg-emerald-500/15 text-emerald-300' : p.stock > 0 ? 'bg-amber-500/15 text-amber-300' : 'bg-red-500/15 text-red-300'
                  }`}
                >
                  {p.stock > 0 ? `${p.stock} en stock` : 'Agotado'}
                </span>
              </div>
              <p className="text-xs text-slate-500">{activo ? '★ Producto destacado en 3D' : 'Clic para verlo en 3D'}</p>
            </div>
          </button>
        )
      })}
    </div>
  )
}
