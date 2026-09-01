import SectionHeading from '../components/SectionHeading'

const sources = [
  {
    name: 'Archaeological Survey of India (ASI)',
    url: 'https://asi.nic.in/',
    note: 'Monument status, conservation, and published epigraphic reports.',
  },
  {
    name: 'South Indian Inscriptions (SII)',
    url: 'https://archive.org/details/south-indian-inscriptions',
    note: 'Primary edition & translation of Tamil and Sanskrit inscriptions (Vols. I, II, XII, etc.). Public domain scans via archive.org.',
  },
  {
    name: 'Annual Report on (South) Indian Epigraphy (ARE/ARIE)',
    url: 'https://epigraphia.blogspot.com/',
    note: 'Annual lists of newly noticed inscriptions with find-spots and reference numbers (e.g. Darasuram ARE 16–27 of 1908).',
  },
  {
    name: 'Epigraphia Indica',
    url: 'https://epigraphia.blogspot.com/',
    note: 'Scholarly journal of Indian inscriptions with annotated translations.',
  },
  {
    name: 'UNESCO World Heritage Centre',
    url: 'https://whc.unesco.org/',
    note: 'Great Living Chola Temples (ref. 250) and Group of Monuments at Mahabalipuram (ref. 249).',
  },
  {
    name: 'Tamil Nadu Department of Archaeology',
    url: 'https://www.tnarch.gov.in/',
    note: 'State archaeological publications and temple surveys.',
  },
  {
    name: 'Wikimedia Commons',
    url: 'https://commons.wikimedia.org/',
    note: 'Freely-licensed photographs, each credited with author and licence in the gallery.',
  },
]

export default function About() {
  return (
    <div className="heritage-bg">
      <div className="bg-charcoal py-12 text-ivory">
        <div className="container-page">
          <p className="label-eyebrow text-gold-light">About & sources</p>
          <h1 className="mt-2 font-display text-4xl font-semibold sm:text-5xl">Why this archive exists</h1>
        </div>
      </div>

      <div className="container-page max-w-4xl space-y-10 py-12">
        <section>
          <SectionHeading eyebrow="Purpose" title="Bringing the stone voice to the present" />
          <p className="text-lg leading-relaxed text-ink/85">
            For a thousand years, our ancestors recorded their history, administration, devotion, and achievement
            on the walls of Tamil temples. <span lang="ta">கல்வெட்டு</span> (kalvettu) — "the engraved stone" — is
            that record. This project connects the physical temple, the exact spot of an inscription, the original
            image, its transcription and translation, and the authoritative source, so that this knowledge reaches
            the present generation intact.
          </p>
        </section>

        <section className="card-surface border-gold/30 p-6">
          <h2 className="font-display text-2xl font-semibold text-charcoal">Our data policy</h2>
          <ul className="mt-4 space-y-3 text-sm leading-relaxed text-ink/85">
            <li><strong className="text-gold-dark">No fabrication.</strong> We do not invent historical data, translations, or image URLs.</li>
            <li><strong className="text-gold-dark">Every fact is sourced.</strong> Each inscription retains its publication reference (SII volume/number, ARE number, or Epigraphia Indica).</li>
            <li><strong className="text-gold-dark">Unverified = unavailable.</strong> Where a fact, translation, image, or physical location cannot be verified from a primary/authoritative source, it is marked as not recorded — never guessed.</li>
            <li><strong className="text-gold-dark">Real photographs only.</strong> Images are from Wikimedia Commons with author + licence attribution; no AI-generated imagery.</li>
            <li><strong className="text-gold-dark">Small and accurate.</strong> A modest, verified dataset is preferred over a large fabricated one. More temples and inscriptions will be added as they are verified.</li>
          </ul>
        </section>

        <section>
          <SectionHeading eyebrow="Authorities" title="Sources we rely on" />
          <div className="grid gap-4 sm:grid-cols-2">
            {sources.map((s) => (
              <a key={s.name} href={s.url} target="_blank" rel="noreferrer noopener" className="card-surface block p-5 transition hover:border-gold">
                <h3 className="font-display text-lg font-semibold text-charcoal">{s.name}</h3>
                <p className="mt-1 text-sm text-ink/75">{s.note}</p>
                <span className="mt-2 inline-block text-xs font-medium text-gold-dark">Visit ↗</span>
              </a>
            ))}
          </div>
        </section>

        <section>
          <SectionHeading eyebrow="The journey" title="How to read a record" />
          <div className="flex flex-wrap items-center gap-2 text-sm">
            {['Temple', 'Inscription location', 'Original image', 'Transcription', 'Translation', 'Historical meaning', 'Source'].map((step, i) => (
              <span key={step} className="flex items-center gap-2">
                <span className="rounded-sm bg-charcoal px-3 py-1.5 text-ivory-card">{i + 1}. {step}</span>
                {i < 6 && <span className="text-gold">→</span>}
              </span>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}
