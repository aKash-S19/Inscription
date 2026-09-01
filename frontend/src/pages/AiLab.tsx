import { useState } from 'react'
import SectionHeading from '../components/SectionHeading'
import { api } from '../services/api'
import type { ChatMessage, IngestResponse, TranslateResponse } from '../types'

type Tab = 'chat' | 'translate' | 'ingest'

const languages = [
  'English', 'Tamil', 'Hindi', 'Telugu', 'Kannada', 'Malayalam',
  'French', 'German', 'Spanish', 'Arabic',
]

const inputCls =
  'w-full rounded-sm border border-gold/30 bg-white px-3 py-2 text-sm text-charcoal placeholder:text-charcoal/40 focus:border-gold focus:outline-none'
const btnCls =
  'rounded-sm bg-gold-dark px-5 py-2.5 text-sm font-semibold text-ivory transition hover:bg-gold focus:outline-none disabled:cursor-not-allowed disabled:opacity-50'
const chipCls = (active: boolean) =>
  `rounded-full px-3 py-1 text-xs font-medium transition ${active ? 'bg-gold-dark text-ivory' : 'bg-charcoal/10 text-charcoal hover:bg-charcoal/20'}`

export default function AiLab() {
  const [tab, setTab] = useState<Tab>('chat')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  // Chat state
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [chatInput, setChatInput] = useState('')
  const [language, setLanguage] = useState('English')

  // Translate state
  const [transText, setTransText] = useState('')
  const [transLang, setTransLang] = useState('English')
  const [translation, setTranslation] = useState<TranslateResponse | null>(null)

  // Ingest state
  const [ingImage, setIngImage] = useState<File | null>(null)
  const [ingText, setIngText] = useState('')
  const [ingTemple, setIngTemple] = useState('')
  const [ingest, setIngest] = useState<IngestResponse | null>(null)
  const [imgPreview, setImgPreview] = useState('')

  async function sendChat() {
    const text = chatInput.trim()
    if (!text || busy) return
    const history = [...messages, { role: 'user' as const, content: text }]
    setMessages(history)
    setChatInput('')
    setError('')
    setBusy(true)
    try {
      const res = await api.aiChat(history, language)
      setMessages([...history, { role: 'assistant', content: res.answer }])
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Chat failed')
    } finally {
      setBusy(false)
    }
  }

  async function doTranslate() {
    const text = transText.trim()
    if (!text || busy) return
    setError('')
    setBusy(true)
    try {
      setTranslation(await api.aiTranslate(text, transLang))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Translation failed')
    } finally {
      setBusy(false)
    }
  }

  function onImagePicked(f: File) {
    setIngImage(f)
    setImgPreview(URL.createObjectURL(f))
  }

  async function doIngest() {
    if (busy) return
    setError('')
    setBusy(true)
    try {
      let imageBase64: string | undefined
      let mimeType: string | undefined
      if (ingImage) {
        const buf = await ingImage.arrayBuffer()
        const bytes = new Uint8Array(buf)
        let bin = ''
        for (const b of bytes) bin += String.fromCharCode(b)
        imageBase64 = btoa(bin)
        mimeType = ingImage.type || 'image/jpeg'
      }
      const res = await api.aiIngest({
        imageBase64,
        mimeType,
        text: ingText.trim() || undefined,
        templeName: ingTemple.trim() || undefined,
      })
      setIngest(res)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ingestion failed')
    } finally {
      setBusy(false)
    }
  }

  const tabs: { id: Tab; label: string }[] = [
    { id: 'chat', label: 'Ask the archive' },
    { id: 'translate', label: 'Translate a kalvettu' },
    { id: 'ingest', label: 'Add a kalvettu (AI)' },
  ]

  return (
    <div className="heritage-bg">
      <div className="bg-charcoal py-12 text-ivory">
        <div className="container-page">
          <p className="label-eyebrow text-gold-light">Kalvettu AI</p>
          <h1 className="mt-2 font-display text-4xl font-semibold sm:text-5xl">AI assistant</h1>
          <p className="mt-3 max-w-2xl text-ivory/75">
            Ask questions grounded in the verified archive, translate and explain any kalvettu
            into any language, or turn a photo of an inscription into a structured record.
          </p>
        </div>
      </div>

      <div className="container-page max-w-4xl py-10">
        <div className="mb-8 flex flex-wrap gap-2">
          {tabs.map((t) => (
            <button
              key={t.id}
              className={chipCls(tab === t.id)}
              onClick={() => setTab(t.id)}
              disabled={busy}
            >
              {t.label}
            </button>
          ))}
        </div>

        {error && (
          <div className="mb-6 rounded-sm border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {tab === 'chat' && (
          <div className="card-surface p-6">
            <SectionHeading eyebrow="Grounded Q&A" title="Ask anything about the archive" />
            {messages.length === 0 ? (
              <p className="mt-2 text-sm text-ink/70">
                Try e.g. "What did Rajaraja I give to the Thanjavur temple?" or "Which inscriptions
                mention the Chera campaign?"
              </p>
            ) : (
              <div className="mt-4 max-h-96 space-y-3 overflow-y-auto pr-2">
                {messages.map((m, i) => (
                  <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[80%] rounded-sm px-4 py-2.5 text-sm leading-relaxed ${m.role === 'user' ? 'bg-gold-dark text-ivory' : 'bg-charcoal/10 text-ink'}`}>
                      <p className="whitespace-pre-wrap">{m.content}</p>
                    </div>
                  </div>
                ))}
                {busy && <p className="text-sm text-ink/60">Thinking…</p>}
              </div>
            )}

            <div className="mt-6 grid gap-3 sm:grid-cols-[1fr_auto_auto]">
              <textarea
                className={inputCls}
                rows={2}
                placeholder="Ask about temples, inscriptions, rulers, dynasties…"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChat() } }}
              />
              <select className={inputCls} value={language} onChange={(e) => setLanguage(e.target.value)}>
                {languages.map((l) => <option key={l}>{l}</option>)}
              </select>
              <button className={btnCls} onClick={sendChat} disabled={busy || !chatInput.trim()}>
                Ask
              </button>
            </div>
          </div>
        )}

        {tab === 'translate' && (
          <div className="card-surface p-6">
            <SectionHeading eyebrow="Translate & explain" title="Kalvettu in any language" />
            <textarea
              className={inputCls}
              rows={5}
              placeholder="Paste the kalvettu text (Tamil / Grantha, or a transcription) here…"
              value={transText}
              onChange={(e) => setTransText(e.target.value)}
            />
            <div className="mt-3 grid gap-3 sm:grid-cols-[1fr_auto]">
              <select className={inputCls} value={transLang} onChange={(e) => setTransLang(e.target.value)}>
                {languages.map((l) => <option key={l}>{l}</option>)}
              </select>
              <button className={btnCls} onClick={doTranslate} disabled={busy || !transText.trim()}>
                Translate & explain
              </button>
            </div>

            {translation && (
              <div className="mt-6 space-y-4 text-sm leading-relaxed text-ink/85">
                <div>
                  <h3 className="font-display text-lg font-semibold text-charcoal">Translation ({translation.targetLanguage})</h3>
                  <p className="mt-1 whitespace-pre-wrap">{translation.translation}</p>
                </div>
                <div>
                  <h3 className="font-display text-lg font-semibold text-charcoal">Plain-language explanation</h3>
                  <p className="mt-1 whitespace-pre-wrap">{translation.explanation}</p>
                </div>
              </div>
            )}
          </div>
        )}

        {tab === 'ingest' && (
          <div className="card-surface p-6">
            <SectionHeading eyebrow="AI data ingestion" title="Photo → structured record" />
            <p className="mt-2 text-sm text-ink/70">
              Upload a photo of an inscription (or paste its text). Gemini reads it and produces a
              draft record for review.
            </p>

            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <label className="block cursor-pointer rounded-sm border border-dashed border-gold/40 bg-white px-4 py-6 text-center text-sm text-charcoal/70 hover:border-gold">
                {ingImage ? `Selected: ${ingImage.name}` : 'Click to upload an inscription photo'}
                <input type="file" accept="image/*" className="hidden" onChange={(e) => { const f = e.target.files?.[0]; if (f) onImagePicked(f) }} />
              </label>
              <div className="rounded-sm border border-gold/30 bg-white p-2">
                {imgPreview ? (
                  <img src={imgPreview} alt="preview" className="h-36 w-full rounded-sm object-contain" />
                ) : (
                  <p className="grid h-36 place-items-center text-xs text-charcoal/50">Image preview</p>
                )}
              </div>
            </div>

            <textarea
              className={inputCls + ' mt-4'}
              rows={3}
              placeholder="Optional: paste the transcription text here…"
              value={ingText}
              onChange={(e) => setIngText(e.target.value)}
            />
            <input
              className={inputCls + ' mt-3'}
              placeholder="Optional: known temple / find-spot, e.g. Brihadisvara Temple, Thanjavur"
              value={ingTemple}
              onChange={(e) => setIngTemple(e.target.value)}
            />
            <button className={btnCls + ' mt-4'} onClick={doIngest} disabled={busy || (!ingImage && !ingText.trim())}>
              Extract record
            </button>

            {ingest && (
              <div className="mt-6 space-y-4 border-t border-gold/20 pt-4 text-sm leading-relaxed text-ink/85">
                <div>
                  <h3 className="font-display text-lg font-semibold text-charcoal">{ingest.title || 'Extracted kalvettu'}</h3>
                  <p className="mt-1 text-xs text-ink/60">{ingest.language} · {ingest.script}</p>
                </div>
                {ingest.translation && (
                  <div><h4 className="font-semibold text-charcoal">Translation</h4><p className="mt-0.5 whitespace-pre-wrap">{ingest.translation}</p></div>
                )}
                {ingest.simpleExplanation && (
                  <div><h4 className="font-semibold text-charcoal">Simple explanation</h4><p className="mt-0.5 whitespace-pre-wrap">{ingest.simpleExplanation}</p></div>
                )}
                {ingest.historicalSignificance && (
                  <div><h4 className="font-semibold text-charcoal">Historical significance</h4><p className="mt-0.5 whitespace-pre-wrap">{ingest.historicalSignificance}</p></div>
                )}
                {ingest.ruler && <div><h4 className="font-semibold text-charcoal">Ruler</h4><p className="mt-0.5">{ingest.ruler}</p></div>}
                {ingest.notes && <div><h4 className="font-semibold text-charcoal">Notes</h4><p className="mt-0.5 whitespace-pre-wrap">{ingest.notes}</p></div>}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}