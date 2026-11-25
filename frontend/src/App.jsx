import { useEffect, useState } from 'react'
import { getProducts, createProduct } from './api'
import { ProductForm } from './components/ProductForm'
import { ProductGrid } from './components/ProductGrid'
import { Product3DViewer } from './components/Product3DViewer'

function Resumen({ icono, titulo, valor }) {
  return (
    <div className="bg-slate-900/80 rounded-2xl p-4 ring-1 ring-white/10">
      <p className="text-sm text-slate-400">{icono} {titulo}</p>
      <p className="text-2xl font-bold text-white mt-1">{valor}</p>
    </div>
  )
}

export default function App() {
  const [products, setProducts] = useState([])
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [aviso, setAviso] = useState('')

  // Cargar productos al abrir la página (GET)
  const cargar = async () => {
    try {
      setError('')
      const data = await getProducts()
      setProducts(data)
      setSelected((s) => s ?? data[0] ?? null)
    } catch (e) {
      setError('No se pudo conectar con la API. Si está en Render (plan gratis), espera un minuto y vuelve a cargar.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { cargar() }, [])

  // Guardar producto nuevo (POST)
  const crear = async (product) => {
    try {
      setError('')
      const nuevo = await createProduct(product)
      setProducts((prev) => [nuevo, ...prev])
      setSelected(nuevo)
      setAviso(`✅ "${nuevo.name}" se guardó correctamente.`)
      setTimeout(() => setAviso(''), 3500)
      return true
    } catch (e) {
      setError(e.message)
      return false
    }
  }

  const stockTotal = products.reduce((t, p) => t + Number(p.stock || 0), 0)
  const valorTotal = products.reduce((t, p) => t + Number(p.price) * Number(p.stock || 0), 0)

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 bg-[radial-gradient(ellipse_at_top,_rgba(99,102,241,0.18),_transparent_60%)]">
      <header className="px-6 pt-10 pb-6 max-w-6xl mx-auto">
        <h1 className="text-3xl sm:text-4xl font-extrabold">
          🛒 Catálogo de <span className="bg-gradient-to-r from-indigo-400 to-fuchsia-400 bg-clip-text text-transparent">Productos</span>
        </h1>
        <p className="text-slate-400 mt-2">Registra productos y míralos en 3D. Los datos se guardan en la nube en tiempo real.</p>
      </header>

      <main className="max-w-6xl mx-auto px-6 pb-12 space-y-8">
        {error && <div className="bg-red-900/40 ring-1 ring-red-700 text-red-200 rounded-xl p-3">⚠️ {error}</div>}
        {aviso && <div className="bg-emerald-900/40 ring-1 ring-emerald-700 text-emerald-200 rounded-xl p-3">{aviso}</div>}

        <section className="grid gap-4 sm:grid-cols-3">
          <Resumen icono="📦" titulo="Productos registrados" valor={products.length} />
          <Resumen icono="📊" titulo="Unidades en stock" valor={stockTotal} />
          <Resumen icono="💰" titulo="Valor del inventario" valor={`Bs ${valorTotal.toFixed(2)}`} />
        </section>

        <section className="grid gap-6 md:grid-cols-2">
          <ProductForm onCreate={crear} />
          <div className="space-y-2">
            <h2 className="text-lg font-semibold">
              ⭐ Producto destacado: <span className="text-indigo-300">{selected?.name ?? '—'}</span>
            </h2>
            <Product3DViewer product={selected} />
          </div>
        </section>

        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Productos ({products.length})</h2>
            <button onClick={cargar} className="text-sm text-indigo-300 hover:text-indigo-200 bg-slate-900 ring-1 ring-white/10 px-3 py-1.5 rounded-lg">
              ↻ Actualizar
            </button>
          </div>
          {loading ? <p className="text-slate-400">Cargando productos…</p> : <ProductGrid products={products} selected={selected} onSelect={setSelected} />}
        </section>
      </main>

      <footer className="text-center text-xs text-slate-500 pb-8">
        Proyecto Final · React + Vite + Tailwind · API FastAPI (Render) · Base de datos Supabase
      </footer>
    </div>
  )
}
