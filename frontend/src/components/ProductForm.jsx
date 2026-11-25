import { useState } from 'react'

const vacio = { name: '', price: '', stock: '', image_url: '' }

export function ProductForm({ onCreate }) {
  const [form, setForm] = useState(vacio)
  const [enviando, setEnviando] = useState(false)

  const cambiar = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const enviar = async (e) => {
    e.preventDefault()
    setEnviando(true)
    const ok = await onCreate({
      name: form.name.trim(),
      price: Number(form.price),
      stock: Number(form.stock || 0),
      image_url: form.image_url.trim() || null,
    })
    if (ok) setForm(vacio)
    setEnviando(false)
  }

  const input =
    'w-full rounded-xl bg-slate-800/70 border border-slate-700 px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent'
  const label = 'block text-sm text-slate-300 mb-1'

  return (
    <form onSubmit={enviar} className="space-y-4 bg-slate-900/80 p-6 rounded-2xl ring-1 ring-white/10">
      <div>
        <h2 className="text-lg font-semibold text-white">➕ Registrar producto</h2>
        <p className="text-sm text-slate-400">Se guarda directamente en la base de datos.</p>
      </div>
      <div>
        <label className={label}>Nombre del producto</label>
        <input className={input} name="name" placeholder="Ej.: Pañal NeneSoft M" value={form.name} onChange={cambiar} required />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={label}>Precio (Bs)</label>
          <input className={input} name="price" type="number" step="0.01" min="0" placeholder="0.00" value={form.price} onChange={cambiar} required />
        </div>
        <div>
          <label className={label}>Stock</label>
          <input className={input} name="stock" type="number" min="0" placeholder="0" value={form.stock} onChange={cambiar} />
        </div>
      </div>
      <div>
        <label className={label}>Foto (enlace, opcional)</label>
        <input className={input} name="image_url" placeholder="https://..." value={form.image_url} onChange={cambiar} />
      </div>
      <button
        type="submit"
        disabled={enviando}
        className="w-full rounded-xl bg-gradient-to-r from-indigo-600 to-fuchsia-600 hover:from-indigo-500 hover:to-fuchsia-500 disabled:opacity-50 py-3 font-semibold text-white shadow-lg shadow-indigo-900/40 transition"
      >
        {enviando ? 'Guardando…' : 'Guardar producto'}
      </button>
    </form>
  )
}
