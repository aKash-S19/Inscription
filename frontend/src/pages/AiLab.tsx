import { useState } from 'react'
import { Link } from 'react-router-dom'
import SectionHeading from '../components/SectionHeading'
import { api } from '../services/api'
import type { ChatMessage, ChatResponse, IngestResponse, TranslateResponse } from '../types'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

type Tab = 'chat' | 'translate' | 'ingest'

const suggestedQuestions = [
  'What did Rajaraja I donate to the Brihadeesvara Temple?',
  'Which inscriptions mention donations from the Chera campaign?',
  'Show inscriptions from the Chola period and their rulers.',
  'What does the Chidambaram inscription tell us about temple administration?',
  'Tell me about the war-trophy dvarapala inscription at Darasuram.'
]

const languages = [
  'English', 'Tamil', 'Hindi', 'Telugu', 'Kannada', 'Malayalam',
  'French', 'German', 'Spanish'
]

const inputCls =
  'w-full rounded-md border border-gold/30 bg-ivory-card px-4 py-3 text-sm text-charcoal placeholder:text-stone/60 focus:border-gold focus:ring-1 focus:ring-gold/40 focus:outline-none transition'
const btnGoldCls =
  'inline-flex items-center justify-center gap-2 rounded-sm bg-gold-dark px-6 py-3 text-sm font-semibold tracking-wide text-ivory transition hover:bg-gold focus:outline-none focus:ring-2 focus:ring-gold/50 disabled:cursor-not-allowed disabled:opacity-50'

export default function AiLab() {
  const [tab, setTab] = useState<Tab>('chat')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  // 1. Chat State
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [chatInput, setChatInput] = useState('')
  const [chatResponse, setChatResponse] = useState<ChatResponse | null>(null)
  const [language, setLanguage] = useState('English')

  // 2. Translate State
  const [transText, setTransText] = useState('')
  const [transLang, setTransLang] = useState('English')
  const [transImage, setTransImage] = useState<File | null>(null)
  const [transImgPreview, setTransImgPreview] = useState('')
  const [translation, setTranslation] = useState<TranslateResponse | null>(null)

  // 3. Ingest State
  const [ingImage, setIngImage] = useState<File | null>(null)
  const [ingText, setIngText] = useState('')
  const [ingTemple, setIngTemple] = useState('')
  const [ingLocation, setIngLocation] = useState('')
  const [ingNotes, setIngNotes] = useState('')
  const [ingest, setIngest] = useState<IngestResponse | null>(null)
  const [imgPreview, setImgPreview] = useState('')

  // Downscale photos client-side to keep under request size limits
  async function imageToPreparedData(file: File): Promise<{ base64: string; mime: string }> {
    try {
      const bitmap = await createImageBitmap(file)
      const MAX_DIM = 1600
      const scale = Math.min(1, MAX_DIM / Math.max(bitmap.width, bitmap.height))
      if (scale >= 1) {
        bitmap.close()
        return await fileToBase64(file, file.type || 'image/jpeg')
      }
      const canvas = document.createElement('canvas')
      canvas.width = Math.round(bitmap.width * scale)
      canvas.height = Math.round(bitmap.height * scale)
      canvas.getContext('2d')?.drawImage(bitmap, 0, 0, canvas.width, canvas.height)
      bitmap.close()
      const blob = await canvasToBlob(canvas)
      return await fileToBase64(blob, 'image/jpeg')
    } catch {
      return await fileToBase64(file, file.type || 'image/jpeg')
    }
  }

  function fileToBase64(blob: Blob, mime: string): Promise<{ base64: string; mime: string }> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onerror = () => reject(new Error('Could not read the image file'))
      reader.onload = () => {
        const result = reader.result as string
        resolve({ base64: result.slice(result.indexOf(',') + 1), mime })
      }
      reader.readAsDataURL(blob)
    })
  }

  function canvasToBlob(canvas: HTMLCanvasElement): Promise<Blob> {
    return new Promise((resolve, reject) => {
      canvas.toBlob((b) => (b ? resolve(b) : reject(new Error('Image processing failed'))), 'image/jpeg', 0.85)
    })
  }

  async function sendChat(questionOverride?: string) {
    const text = (questionOverride || chatInput).trim()
    if (!text || busy) return
    const history = [...messages, { role: 'user' as const, content: text }]
    setMessages(history)
    setChatInput('')
    setError('')
    setBusy(true)
    try {
      const res = await api.aiChat(history, language)
      setChatResponse(res)
      setMessages([...history, { role: 'assistant', content: res.answer }])
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Chat query failed.')
    } finally {
      setBusy(false)
    }
  }

  async function doTranslate() {
    if (busy || (!transText.trim() && !transImage)) return
    setError('')
    setBusy(true)
    try {
      let imageBase64: string | undefined
      let mimeType: string | undefined
      if (transImage) {
        const prepared = await imageToPreparedData(transImage)
        imageBase64 = prepared.base64
        mimeType = prepared.mime
      }
      const res = await api.aiTranslate({
        text: transText.trim(),
        targetLanguage: transLang,
        imageBase64,
        mimeType
      })
      setTranslation(res)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Translation failed.')
    } finally {
      setBusy(false)
    }
  }

  async function doIngest() {
    if (busy || (!ingImage && !ingText.trim())) return
    setError('')
    setBusy(true)
    try {
      let imageBase64: string | undefined
      let mimeType: string | undefined
      if (ingImage) {
        const prepared = await imageToPreparedData(ingImage)
        imageBase64 = prepared.base64
        mimeType = prepared.mime
      }
      const res = await api.aiIngest({
        imageBase64,
        mimeType,
        text: ingText.trim() || undefined,
        templeName: ingTemple.trim() || undefined,
        locationInTemple: ingLocation.trim() || undefined,
        notes: ingNotes.trim() || undefined,
      })
      setIngest(res)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Extraction failed.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="heritage-bg min-h-screen">
      {/* HERO SECTION */}
      <div className="relative overflow-hidden bg-charcoal py-14 text-ivory shadow-lg">
        <div className="absolute inset-0 opacity-20 heritage-bg" />
        <div
          className="absolute inset-0 opacity-20 pointer-events-none"
          style={{ backgroundImage: 'radial-gradient(circle at 75% 30%, rgba(176,141,54,0.4), transparent 50%)' }}
        />
        <div className="container-page relative">
          <p className="label-eyebrow text-gold-light tracking-[0.25em]">KALVETTU INTELLIGENCE</p>
          <h1 className="mt-3 font-english-display tracking-wide text-4xl font-semibold sm:text-5xl">Explore the archive with AI</h1>
          <p className="mt-4 max-w-3xl text-lg leading-relaxed text-ivory/80">
            Search verified temple and inscription records, understand historical sources,
            translate inscription text, and assist in creating new records. Grounded in primary epigraphic citations.
          </p>

          {/* Three Capabilities Banner */}
          <div className="mt-8 grid gap-4 sm:grid-cols-3">
            <button
              onClick={() => setTab('chat')}
              className={`rounded-lg p-4 text-left transition ${
                tab === 'chat'
                  ? 'border border-gold bg-gold/15 shadow-soft ring-1 ring-gold/40'
                  : 'border border-ivory/15 bg-charcoal-light/60 hover:border-gold/50'
              }`}
            >
              <div className="flex items-center gap-2">
                <h2 className="font-english-display tracking-wide text-lg font-semibold text-ivory">1. Ask the Archive</h2>
              </div>
              <p className="mt-1 text-xs text-ivory/70">
                Grounded Q&A using verified records from South Indian Inscriptions & ARE.
              </p>
            </button>

            <button
              onClick={() => setTab('translate')}
              className={`rounded-lg p-4 text-left transition ${
                tab === 'translate'
                  ? 'border border-gold bg-gold/15 shadow-soft ring-1 ring-gold/40'
                  : 'border border-ivory/15 bg-charcoal-light/60 hover:border-gold/50'
              }`}
            >
              <div className="flex items-center gap-2">
                <h2 className="font-english-display tracking-wide text-lg font-semibold text-ivory">2. Translate a Kalvettu</h2>
              </div>
              <p className="mt-1 text-xs text-ivory/70">
                Translate Tamil & Grantha text into any language with script detection.
              </p>
            </button>

            <button
              onClick={() => setTab('ingest')}
              className={`rounded-lg p-4 text-left transition ${
                tab === 'ingest'
                  ? 'border border-gold bg-gold/15 shadow-soft ring-1 ring-gold/40'
                  : 'border border-ivory/15 bg-charcoal-light/60 hover:border-gold/50'
              }`}
            >
              <div className="flex items-center gap-2">
                <h2 className="font-english-display tracking-wide text-lg font-semibold text-ivory">3. Add a Kalvettu (AI)</h2>
              </div>
              <p className="mt-1 text-xs text-ivory/70">
                AI-assisted draft extraction from photos for epigraphist moderation.
              </p>
            </button>
          </div>
        </div>
      </div>

      <div className="container-page max-w-5xl py-10">
        {error && (
          <div className="mb-6 rounded-md border border-red-300 bg-red-50 p-4 text-sm text-red-800 shadow-sm">
            <span className="font-semibold">Notice:</span> {error}
          </div>
        )}

        {/* 1. ASK THE ARCHIVE */}
        {tab === 'chat' && (
          <div className="card-surface p-6 sm:p-8">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-gold/20 pb-4">
              <div>
                <span className="label-eyebrow">RAG ARCHIVE SEARCH</span>
                <h2 className="font-english-display tracking-wide text-2xl font-semibold text-charcoal">Ask anything about the verified records</h2>
              </div>
              <div className="flex items-center gap-2 text-xs text-stone">
                <span>Multi-provider fallback:</span>
                <span className="rounded-full bg-gold/10 px-2.5 py-0.5 font-medium text-gold-dark">
                  Groq &middot; Cerebras &middot; Gemma &middot; Gemini
                </span>
              </div>
            </div>

            {/* Suggested Question Pills */}
            <div className="mt-5">
              <p className="text-xs font-semibold text-stone uppercase tracking-wide">Suggested questions from verified volumes:</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {suggestedQuestions.map((q) => (
                  <button
                    key={q}
                    onClick={() => sendChat(q)}
                    disabled={busy}
                    className="rounded-full border border-charcoal/15 bg-white px-3.5 py-1.5 text-xs text-charcoal transition hover:border-gold hover:bg-gold/5 hover:text-gold-dark"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>

            {/* Conversation Area */}
            <div className="mt-6 space-y-4">
              {messages.length === 0 ? (
                <div className="rounded-lg border border-dashed border-charcoal/15 bg-ivory-deep/40 p-8 text-center">
                  <p className="font-english-display tracking-wide text-lg font-medium text-charcoal">No questions asked yet</p>
                  <p className="mt-1 text-sm text-stone">
                    Type a question below or pick a suggested topic above to query the database.
                  </p>
                </div>
              ) : (
                <div className="max-h-[500px] space-y-4 overflow-y-auto pr-2">
                  {messages.map((m, i) => (
                    <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div
                        className={`max-w-[85%] rounded-lg p-4 text-sm leading-relaxed shadow-sm ${
                          m.role === 'user'
                            ? 'bg-charcoal text-ivory'
                            : 'border border-gold/30 bg-white text-charcoal'
                        }`}
                      >
                        {m.role === 'assistant' && (
                          <div className="mb-2 flex items-center justify-between border-b border-gold/15 pb-1 text-xs text-gold-dark">
                            <span className="font-semibold uppercase tracking-wider">Kalvettu Intelligence</span>
                            {chatResponse?.providerUsed && (
                              <span className="text-[11px] text-stone">Generated via: {chatResponse.providerUsed}</span>
                            )}
                          </div>
                        )}
                        {m.role === 'assistant' ? (
                          <div className="prose prose-stone prose-sm max-w-none prose-headings:font-english-display prose-headings:text-charcoal prose-a:text-gold-dark hover:prose-a:text-gold prose-table:text-sm prose-td:p-2 prose-th:p-2 prose-th:bg-ivory-deep prose-table:border-collapse prose-tr:border-b prose-tr:border-charcoal/10">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {m.content}
                            </ReactMarkdown>
                          </div>
                        ) : (
                          <p className="whitespace-pre-wrap">{m.content}</p>
                        )}

                        {/* Citations & Linked Sources */}
                        {m.role === 'assistant' && chatResponse?.sources && chatResponse.sources.length > 0 && (
                          <div className="mt-4 border-t border-gold/20 pt-3">
                            <p className="text-xs font-semibold text-charcoal uppercase tracking-wider">
                              Authoritative Sources Cited:
                            </p>
                            <ul className="mt-2 space-y-1.5 text-xs text-stone">
                              {chatResponse.sources.map((s, idx) => (
                                <li key={idx} className="flex items-start gap-1.5">
                                  <span className="text-gold-dark font-bold">&bull;</span>
                                  <span>
                                    <strong className="text-charcoal">{s.institution}</strong> - {s.reference}
                                    {s.url && (
                                      <a
                                        href={s.url}
                                        target="_blank"
                                        rel="noreferrer noopener"
                                        className="ml-1.5 text-gold-dark underline hover:text-gold"
                                      >
                                        [View Source &rarr;]
                                      </a>
                                    )}
                                  </span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* Related Temples / Inscriptions */}
                        {m.role === 'assistant' && (
                          (chatResponse?.relatedTemples?.length || chatResponse?.relatedInscriptions?.length) ? (
                            <div className="mt-3 flex flex-wrap gap-1.5 pt-2 text-xs">
                              {chatResponse.relatedTemples?.map((t) => (
                                <Link
                                  key={t}
                                  to={`/temples?q=${encodeURIComponent(t)}`}
                                  className="rounded-full bg-gold/10 px-2.5 py-0.5 text-gold-dark hover:bg-gold/20 transition"
                                >
                                  {t}
                                </Link>
                              ))}
                              {chatResponse.relatedInscriptions?.map((ins) => (
                                <Link
                                  key={ins}
                                  to={`/inscriptions?q=${encodeURIComponent(ins)}`}
                                  className="rounded-full bg-charcoal/10 px-2.5 py-0.5 text-charcoal hover:bg-charcoal/20 transition"
                                >
                                  {ins}
                                </Link>
                              ))}
                            </div>
                          ) : null
                        )}
                      </div>
                    </div>
                  ))}
                  {busy && (
                    <div className="flex justify-start">
                      <div className="rounded-lg border border-gold/30 bg-white p-4 text-sm text-stone shadow-sm">
                        <span className="inline-block animate-pulse">Searching verified archive records & consulting AI fallback chain&hellip;</span>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Input Bar */}
            <div className="mt-6 grid gap-3 sm:grid-cols-[1fr_auto_auto]">
              <textarea
                className={inputCls}
                rows={2}
                placeholder="Ask about temple endowments, kings, campaigns, silver/gold vessels, or administration…"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    sendChat()
                  }
                }}
              />
              <select
                className="rounded-md border border-gold/30 bg-ivory-card px-3 py-2 text-sm text-charcoal focus:border-gold focus:outline-none"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
              >
                {languages.map((l) => (
                  <option key={l} value={l}>{l}</option>
                ))}
              </select>
              <button
                className={btnGoldCls}
                onClick={() => sendChat()}
                disabled={busy || !chatInput.trim()}
              >
                {busy ? 'Searching…' : 'Ask Archive'}
              </button>
            </div>
          </div>
        )}

        {/* 2. TRANSLATE A KALVETTU */}
        {tab === 'translate' && (
          <div className="card-surface p-6 sm:p-8">
            <div className="border-b border-gold/20 pb-4">
              <span className="label-eyebrow">EPIGRAPHIC TRANSLATOR</span>
              <h2 className="font-english-display tracking-wide text-2xl font-semibold text-charcoal">Translate & explain an inscription</h2>
              <p className="mt-1 text-sm text-stone">
                Enter Tamil, Grantha, or romanised inscription text, or upload an inscription photograph for AI OCR analysis.
              </p>
            </div>

            <div className="mt-6 space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase text-charcoal">
                  Inscription Text (Tamil / Grantha / Transliteration)
                </label>
                <textarea
                  className={inputCls + ' mt-1'}
                  rows={4}
                  placeholder="e.g. Svasti Sri Udaiyar Sri Vijaya Rajendra devar Kalyanapuram erindu kodu vanda dvarapalar..."
                  value={transText}
                  onChange={(e) => setTransText(e.target.value)}
                />
              </div>

              {/* Optional Photo Upload */}
              <div>
                <label className="block text-xs font-semibold uppercase text-charcoal">
                  Or upload photograph of inscription (Optional OCR)
                </label>
                <div className="mt-1 flex flex-col sm:flex-row gap-3">
                  <label className="flex-1 cursor-pointer rounded-md border border-dashed border-gold/40 bg-white p-4 text-center text-sm text-charcoal hover:border-gold">
                    {transImage ? `Attached: ${transImage.name}` : 'Click to select an inscription photograph'}
                    <input
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={(e) => {
                        const f = e.target.files?.[0]
                        if (f) {
                          setTransImage(f)
                          setTransImgPreview(URL.createObjectURL(f))
                        }
                      }}
                    />
                  </label>
                  {transImgPreview && (
                    <div className="relative h-20 w-28 overflow-hidden rounded-md border border-gold/30">
                      <img src={transImgPreview} alt="Preview" className="h-full w-full object-cover" />
                      <button
                        onClick={() => { setTransImage(null); setTransImgPreview('') }}
                        className="absolute right-1 top-1 rounded-full bg-charcoal/70 px-1.5 py-0.5 text-[10px] text-white"
                      >
                        &times;
                      </button>
                    </div>
                  )}
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-3 pt-2">
                <label className="flex items-center gap-2 text-sm text-charcoal">
                  <span>Target Language:</span>
                  <select
                    className="rounded-md border border-gold/30 bg-ivory-card px-3 py-1.5 text-sm"
                    value={transLang}
                    onChange={(e) => setTransLang(e.target.value)}
                  >
                    {languages.map((l) => (
                      <option key={l} value={l}>{l}</option>
                    ))}
                  </select>
                </label>
                <button
                  className={btnGoldCls + ' ml-auto'}
                  onClick={doTranslate}
                  disabled={busy || (!transText.trim() && !transImage)}
                >
                  {busy ? 'Translating…' : 'Translate & Explain'}
                </button>
              </div>

              {/* Translation Output Card */}
              {translation && (
                <div className="mt-8 rounded-lg border border-gold/40 bg-white p-6 shadow-sm">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-gold/20 pb-3">
                    <div className="flex items-center gap-2">
                      <span className="rounded-full bg-gold/15 px-3 py-0.5 text-xs font-semibold text-gold-dark">
                        {translation.detectedLanguage} ({translation.detectedScript})
                      </span>
                      {translation.isDraft && (
                        <span className="rounded-full bg-amber-100 px-3 py-0.5 text-xs font-semibold text-amber-800">
                          AI-generated draft - requires verification
                        </span>
                      )}
                    </div>
                    {translation.providerUsed && (
                      <span className="text-xs text-stone">Engine: {translation.providerUsed}</span>
                    )}
                  </div>

                  <div className="mt-4 space-y-4 text-sm leading-relaxed text-charcoal">
                    <div>
                      <h4 className="font-semibold text-charcoal text-xs uppercase tracking-wider text-gold-dark">
                        Translation ({translation.targetLanguage})
                      </h4>
                      <p className="mt-1 text-base leading-relaxed text-charcoal/90">{translation.translation}</p>
                    </div>

                    <div>
                      <h4 className="font-semibold text-charcoal text-xs uppercase tracking-wider text-gold-dark">
                        Plain-Language Explanation
                      </h4>
                      <p className="mt-1 text-sm leading-relaxed text-charcoal/80">{translation.explanation}</p>
                    </div>

                    {translation.historicalContext && (
                      <div>
                        <h4 className="font-semibold text-charcoal text-xs uppercase tracking-wider text-gold-dark">
                          Historical Context
                        </h4>
                        <p className="mt-1 text-sm text-charcoal/80">{translation.historicalContext}</p>
                      </div>
                    )}

                    {translation.importantTerms && translation.importantTerms.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-charcoal text-xs uppercase tracking-wider text-gold-dark">
                          Key Epigraphic Terms
                        </h4>
                        <div className="mt-1.5 flex flex-wrap gap-1.5">
                          {translation.importantTerms.map((term, i) => (
                            <span key={i} className="rounded-md bg-ivory-deep px-2.5 py-1 text-xs text-charcoal">
                              {term}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 3. ADD A KALVETTU (AI-ASSISTED INGESTION) */}
        {tab === 'ingest' && (
          <div className="card-surface p-6 sm:p-8">
            <div className="border-b border-gold/20 pb-4">
              <div className="flex items-center gap-2">
                <span className="label-eyebrow">CONTRIBUTE TO ARCHIVE</span>
                <span className="rounded-full bg-amber-100 px-2.5 py-0.5 text-[11px] font-semibold text-amber-900">
                  DRAFT MODERATION WORKFLOW
                </span>
              </div>
              <h2 className="font-english-display tracking-wide text-2xl font-semibold text-charcoal">Add a Kalvettu (AI-Assisted)</h2>
              <p className="mt-1 text-sm text-stone">
                Upload a photograph or transcription of an inscription. The AI extracts a candidate structured record
                which is automatically saved as <strong className="text-charcoal">DRAFT</strong> in Supabase for human expert verification.
              </p>
            </div>

            <div className="mt-6 space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-xs font-semibold uppercase text-charcoal">
                    Inscription Photograph
                  </label>
                  <label className="mt-1 flex h-40 cursor-pointer flex-col items-center justify-center rounded-md border border-dashed border-gold/40 bg-white p-4 text-center text-sm text-charcoal hover:border-gold">
                    {ingImage ? ingImage.name : 'Click to upload inscription photo'}
                    <span className="mt-1 text-[11px] text-stone">Supports JPEG, PNG, WebP</span>
                    <input
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={(e) => {
                        const f = e.target.files?.[0]
                        if (f) {
                          setIngImage(f)
                          setImgPreview(URL.createObjectURL(f))
                        }
                      }}
                    />
                  </label>
                </div>

                <div>
                  <label className="block text-xs font-semibold uppercase text-charcoal">
                    Image Preview
                  </label>
                  <div className="mt-1 flex h-40 items-center justify-center overflow-hidden rounded-md border border-gold/30 bg-white">
                    {imgPreview ? (
                      <img src={imgPreview} alt="Preview" className="h-full w-full object-contain" />
                    ) : (
                      <p className="text-xs text-stone/50">No photo uploaded</p>
                    )}
                  </div>
                </div>
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                <div>
                  <label className="block text-xs font-semibold uppercase text-charcoal">
                    Associated Temple / Site
                  </label>
                  <input
                    className={inputCls + ' mt-1'}
                    placeholder="e.g. Brihadisvara Temple, Thanjavur"
                    value={ingTemple}
                    onChange={(e) => setIngTemple(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase text-charcoal">
                    Location in Temple
                  </label>
                  <input
                    className={inputCls + ' mt-1'}
                    placeholder="e.g. North wall of central shrine, second tier"
                    value={ingLocation}
                    onChange={(e) => setIngLocation(e.target.value)}
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase text-charcoal">
                  Transcription Text (Optional if photo is clear)
                </label>
                <textarea
                  className={inputCls + ' mt-1'}
                  rows={3}
                  placeholder="Paste known text or notes from ASI / SII volume..."
                  value={ingText}
                  onChange={(e) => setIngText(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase text-charcoal">
                  Archaeological Notes / References
                </label>
                <input
                  className={inputCls + ' mt-1'}
                  placeholder="e.g. Reference number, discoverer, publication notes..."
                  value={ingNotes}
                  onChange={(e) => setIngNotes(e.target.value)}
                />
              </div>

              <div className="pt-2">
                <button
                  className={btnGoldCls}
                  onClick={doIngest}
                  disabled={busy || (!ingImage && !ingText.trim())}
                >
                  {busy ? 'Extracting & Saving Draft…' : 'Extract Record (AI)'}
                </button>
              </div>

              {/* Extraction Review Card */}
              {ingest && (
                <div className="mt-8 rounded-lg border border-amber-300 bg-amber-50/50 p-6 shadow-sm">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-amber-200 pb-3">
                    <div className="flex items-center gap-2">
                      <span className="rounded-full bg-amber-200 px-3 py-0.5 text-xs font-bold text-amber-900">
                        STATUS: {ingest.verificationStatus || 'DRAFT'}
                      </span>
                      <span className="text-xs text-amber-800">
                        {ingest.statusMessage}
                      </span>
                    </div>
                  </div>

                  <div className="mt-4 space-y-3 text-sm text-charcoal">
                    <h3 className="font-english-display tracking-wide text-xl font-semibold text-charcoal">{ingest.title}</h3>
                    <p className="text-xs text-stone">
                      Language: <strong>{ingest.language}</strong> &middot; Script: <strong>{ingest.script}</strong>
                    </p>
                    {ingest.ruler && (
                      <p className="text-xs text-stone">Associated Ruler: <strong>{ingest.ruler}</strong></p>
                    )}
                    {ingest.translation && (
                      <div>
                        <h4 className="text-xs font-semibold uppercase text-gold-dark">Translation</h4>
                        <p className="mt-0.5 text-charcoal/90">{ingest.translation}</p>
                      </div>
                    )}
                    {ingest.simpleExplanation && (
                      <div>
                        <h4 className="text-xs font-semibold uppercase text-gold-dark">Explanation</h4>
                        <p className="mt-0.5 text-charcoal/80">{ingest.simpleExplanation}</p>
                      </div>
                    )}
                    {ingest.historicalSignificance && (
                      <div>
                        <h4 className="text-xs font-semibold uppercase text-gold-dark">Significance</h4>
                        <p className="mt-0.5 text-charcoal/80">{ingest.historicalSignificance}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}