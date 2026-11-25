import { useEffect, useRef, useState } from 'react'
import { askAssistant } from '../api'

const SUGERENCIAS = ['¿Qué productos hay?', '¿Cuál es el más barato?', '¿Qué producto tiene más stock?']

export function ChatAsistente() {
  const [mensajes, setMensajes] = useState([
    { de: 'bot', texto: '¡Hola! 👋 Soy el asistente de IA. Pregúntame por precios o stock de los productos.' },
  ])
  const [texto, setTexto] = useState('')
  const [pensando, setPensando] = useState(false)
  const fin = useRef(null)

  useEffect(() => {
    fin.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }, [mensajes, pensando])

  const enviar = async (pregunta) => {
    const q = pregunta.trim()
    if (!q || pensando) return
    setMensajes((m) => [...m, { de: 'yo', texto: q }])
    setTexto('')
    setPensando(true)
    try {
      const respuesta = await askAssistant(q)
      setMensajes((m) => [...m, { de: 'bot', texto: respuesta }])
    } catch (e) {
      setMensajes((m) => [...m, { de: 'bot', texto: '⚠️ No pude conectarme con el asistente. Intenta de nuevo.' }])
    } finally {
      setPensando(false)
    }
  }

  return (
    <div className="bg-slate-900/80 rounded-2xl ring-1 ring-white/10 flex flex-col h-[28rem]">
      <div className="px-5 py-4 border-b border-white/10">
        <h2 className="text-lg font-semibold text-white">🤖 Asistente de IA</h2>
        <p className="text-sm text-slate-400">Consulta la base de datos con Gemini · también en Telegram</p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {mensajes.map((m, i) => (
          <div key={i} className={`flex ${m.de === 'yo' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[85%] whitespace-pre-line rounded-2xl px-4 py-2 text-sm ${
                m.de === 'yo' ? 'bg-indigo-600 text-white rounded-br-sm' : 'bg-slate-800 text-slate-100 rounded-bl-sm'
              }`}
            >
              {m.texto}
            </div>
          </div>
        ))}
        {pensando && <div className="text-sm text-slate-400">El asistente está pensando…</div>}
        <div ref={fin} />
      </div>

      <div className="px-4 pb-2 flex flex-wrap gap-2">
        {SUGERENCIAS.map((s) => (
          <button key={s} onClick={() => enviar(s)} className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1 rounded-full">
            {s}
          </button>
        ))}
      </div>

      <form
        onSubmit={(e) => { e.preventDefault(); enviar(texto) }}
        className="flex gap-2 p-4 border-t border-white/10"
      >
        <input
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          placeholder="Escribe tu pregunta…"
          className="flex-1 rounded-xl bg-slate-800/70 border border-slate-700 px-4 py-2 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <button type="submit" disabled={pensando} className="rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 px-4 font-medium text-white">
          Enviar
        </button>
      </form>
    </div>
  )
}
