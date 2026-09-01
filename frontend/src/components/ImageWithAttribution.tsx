import type { ImageDto } from '../types'

interface Props {
  image: ImageDto
  className?: string
  showAttribution?: boolean
}

/**
 * Renders a real, freely-licensed photograph (Wikimedia Commons) with the
 * required author + licence attribution. We never hotlink without credit.
 */
export default function ImageWithAttribution({ image, className, showAttribution = true }: Props) {
  const src = image.thumbUrl || image.imageUrl
  return (
    <figure className={className}>
      <img
        src={src}
        alt={image.caption || 'Temple photograph'}
        loading="lazy"
        className="h-full w-full object-cover"
        referrerPolicy="no-referrer"
      />
      {showAttribution && (
        <figcaption className="mt-1 px-1 text-[11px] leading-snug text-stone">
          {image.author ? `Photo: ${image.author} · ` : 'Photo: '}
          {image.license ? <span className="text-gold-dark">{image.license}</span> : 'Wikimedia Commons'}
          {image.commonsUrl ? (
            <a href={image.commonsUrl} target="_blank" rel="noreferrer noopener" className="ml-1 underline hover:text-gold-dark">
              source
            </a>
          ) : null}
        </figcaption>
      )}
    </figure>
  )
}
