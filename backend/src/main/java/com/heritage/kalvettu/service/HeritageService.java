package com.heritage.kalvettu.service;

import com.heritage.kalvettu.domain.*;
import com.heritage.kalvettu.dto.*;
import com.heritage.kalvettu.repository.*;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

/**
 * Assembles response DTOs from the verified domain data.
 * No data transformation beyond mapping; nothing is invented here.
 */
@Service
public class HeritageService {

    private final TempleRepository templeRepository;
    private final InscriptionRepository inscriptionRepository;
    private final ImageRepository imageRepository;
    private final DynastyRepository dynastyRepository;
    private final RulerRepository rulerRepository;
    private final DistrictRepository districtRepository;
    private final InscriptionLocationRepository locationRepository;

    public HeritageService(TempleRepository templeRepository,
                           InscriptionRepository inscriptionRepository,
                           ImageRepository imageRepository,
                           DynastyRepository dynastyRepository,
                           RulerRepository rulerRepository,
                           DistrictRepository districtRepository,
                           InscriptionLocationRepository locationRepository) {
        this.templeRepository = templeRepository;
        this.inscriptionRepository = inscriptionRepository;
        this.imageRepository = imageRepository;
        this.dynastyRepository = dynastyRepository;
        this.rulerRepository = rulerRepository;
        this.districtRepository = districtRepository;
        this.locationRepository = locationRepository;
    }

    public List<TempleCard> listTemples(String q, String district, String dynasty) {
        return templeRepository.findAll().stream()
                .filter(t -> q == null || q.isBlank() ||
                        matches(t.getNameEn(), q) || matches(t.getNameTa(), q) ||
                        matches(t.getDeity(), q) || matches(t.getTown(), q) ||
                        matches(t.getAlternateNames(), q))
                .filter(t -> district == null || district.isBlank() || district.equals(t.getDistrictSlug()))
                .filter(t -> dynasty == null || dynasty.isBlank() || dynasty.equals(t.getDynastySlug()))
                .map(this::toCard)
                .toList();
    }

    public Optional<TempleDetail> getTemple(String slug) {
        return templeRepository.findBySlug(slug).map(t -> new TempleDetail(
                toCard(t),
                toImageDtos(imageRepository.findByEntity("TEMPLE", slug)),
                inscriptionRepository.findByTempleSlug(slug).stream().map(this::toInsCard).toList(),
                locationRepository.findByTempleSlug(slug).stream().map(this::toLocDto).toList(),
                t.getDynastySlug() == null ? null : dynastyRepository.findBySlug(t.getDynastySlug()).map(this::toDynastyDto).orElse(null),
                t.getDistrictSlug() == null ? null : districtRepository.findBySlug(t.getDistrictSlug()).map(this::toDistrictDto).orElse(null)
        ));
    }

    public List<InscriptionCard> listInscriptions(String q, String temple, String dynasty,
                                                 String ruler, String district) {
        return inscriptionRepository.findAll().stream()
                .filter(i -> temple == null || temple.isBlank() || temple.equals(i.getTempleSlug()))
                .filter(i -> dynasty == null || dynasty.isBlank() || dynasty.equals(i.getDynastySlug()))
                .filter(i -> ruler == null || ruler.isBlank() || ruler.equals(i.getRulerSlug()))
                .filter(i -> {
                    if (district == null || district.isBlank()) return true;
                    return templeRepository.findBySlug(i.getTempleSlug())
                            .map(t -> district.equals(t.getDistrictSlug())).orElse(false);
                })
                .filter(i -> q == null || q.isBlank() ||
                        matches(i.getTitle(), q) || matches(i.getTranslation(), q) ||
                        matches(i.getSimpleExplanation(), q) || matches(i.getSiiReference(), q) ||
                        matches(i.getAreNumber(), q) || matches(i.getPhysicalLocation(), q))
                .map(this::toInsCard)
                .toList();
    }

    public Optional<InscriptionDetail> getInscription(String slug) {
        return inscriptionRepository.findBySlug(slug).map(i -> new InscriptionDetail(
                i.getId(), i.getSlug(), i.getTempleSlug(), i.getTitle(), i.getTitleTa(),
                i.getReferenceId(), i.getAreNumber(), i.getSiiReference(), i.getEpigraphiaIndica(),
                i.getRulerSlug(), i.getDynastySlug(), i.getRegnalYear(), i.getDateNote(),
                i.getLanguage(), i.getScript(), i.getPhysicalLocation(),
                i.getOriginalText(), i.getOriginalTextSource(), i.getTransliteration(),
                i.getTranslation(), i.getTranslationSource(), i.getSimpleExplanation(),
                i.getHistoricalSignificance(), i.getSourceCitation(), i.getSourceUrl(),
                i.getVerified(), toImageDtos(imageRepository.findByEntity("INSCRIPTION", slug)),
                templeRepository.findBySlug(i.getTempleSlug()).map(this::toCard).orElse(null)
        ));
    }

    public List<DynastyDto> listDynasties() {
        return dynastyRepository.findAll().stream().map(this::toDynastyDto).toList();
    }

    public List<RulerDto> listRulers(String dynasty) {
        if (dynasty == null || dynasty.isBlank()) {
            return rulerRepository.findAll().stream().map(this::toRulerDto).toList();
        }
        return rulerRepository.findByDynastySlug(dynasty).stream().map(this::toRulerDto).toList();
    }

    public List<DistrictDto> listDistricts() {
        return districtRepository.findAll().stream().map(this::toDistrictDto).toList();
    }

    public List<InscriptionLocationDto> locationsForTemple(String templeSlug) {
        return locationRepository.findByTempleSlug(templeSlug).stream().map(this::toLocDto).toList();
    }

    public List<TimelineEvent> timeline() {
        return timelineBuilder();
    }

    // ---------- mappers ----------

    private TempleCard toCard(Temple t) {
        return new TempleCard(t.getId(), t.getSlug(), t.getNameEn(), t.getNameTa(), t.getTown(),
                t.getDistrictSlug(), t.getDynastySlug(), t.getDeity(), t.getPeriodNote(),
                t.getConsecrationYear(), t.getLat(), t.getLng(), t.getSummary(),
                t.getUnescoWorldHeritage(), t.getAsiMonument(),
                firstImageUrl(t.getSlug()));
    }

    private InscriptionCard toInsCard(Inscription i) {
        return new InscriptionCard(i.getId(), i.getSlug(), i.getTempleSlug(), i.getTitle(), i.getTitleTa(),
                i.getReferenceId(), i.getAreNumber(), i.getSiiReference(), i.getRulerSlug(),
                i.getDynastySlug(), i.getRegnalYear(), i.getLanguage(), i.getScript(),
                i.getPhysicalLocation(), firstInscriptionImageUrl(i.getSlug()), i.getVerified());
    }

    private InscriptionLocationDto toLocDto(InscriptionLocation l) {
        return new InscriptionLocationDto(l.getId(), l.getInscriptionSlug(), l.getTempleSlug(),
                l.getLabel(), l.getDescription(), l.getArea(), l.getMapX(), l.getMapY(),
                l.getCoordinateSystem(), l.getLat(), l.getLng());
    }

    private DynastyDto toDynastyDto(Dynasty d) {
        return new DynastyDto(d.getId(), d.getSlug(), d.getNameEn(), d.getNameTa(), d.getStartYear(),
                d.getEndYear(), d.getCapital(), d.getDescription(), d.getSourceNote());
    }

    private RulerDto toRulerDto(Ruler r) {
        return new RulerDto(r.getId(), r.getSlug(), r.getNameEn(), r.getNameTa(), r.getDynastySlug(),
                r.getReignStart(), r.getReignEnd(), r.getCapital(), r.getNote(), r.getSourceNote());
    }

    private DistrictDto toDistrictDto(District d) {
        return new DistrictDto(d.getId(), d.getSlug(), d.getNameEn(), d.getHeadquarters(), d.getLat(), d.getLng(), d.getNote());
    }

    private List<ImageDto> toImageDtos(List<Image> images) {
        return images.stream().map(im -> new ImageDto(im.getId(), im.getEntityType(), im.getEntitySlug(),
                im.getCategory(), im.getImageUrl(), im.getThumbUrl(), im.getWidth(), im.getHeight(),
                im.getAuthor(), im.getLicense(), im.getLicenseUrl(), im.getCommonsUrl(), im.getCaption())).toList();
    }

    private String firstImageUrl(String templeSlug) {
        return imageRepository.findByEntity("TEMPLE", templeSlug).stream().findFirst()
                .map(im -> im.getThumbUrl() != null ? im.getThumbUrl() : im.getImageUrl()).orElse(null);
    }

    private String firstInscriptionImageUrl(String inscriptionSlug) {
        return imageRepository.findByEntity("INSCRIPTION", inscriptionSlug).stream().findFirst()
                .map(im -> im.getThumbUrl() != null ? im.getThumbUrl() : im.getImageUrl()).orElse(null);
    }

    private boolean matches(String value, String q) {
        if (value == null) return false;
        return value.toLowerCase().contains(q.toLowerCase());
    }

    // Timeline is assembled from verified dates in the dataset.
    private List<TimelineEvent> timelineBuilder() {
        // Built lazily from dynasties + rulers + temple consecrations + inscriptions.
        java.util.List<TimelineEvent> events = new java.util.ArrayList<>();
        templeRepository.findAll().forEach(t -> {
            if (t.getConsecrationYear() != null) {
                events.add(new TimelineEvent(
                        String.valueOf(t.getConsecrationYear()),
                        t.getNameEn() + " — consecrated/built",
                        (t.getPatron() != null ? "Patron: " + t.getPatron() + ". " : "") +
                                (t.getPeriodNote() != null ? t.getPeriodNote() : ""),
                        "TEMPLE", t.getSlug(),
                        "See temple record and cited sources."));
            }
        });
        rulerRepository.findAll().forEach(r -> {
            if (r.getReignStart() != null) {
                events.add(new TimelineEvent(
                        String.valueOf(r.getReignStart()),
                        r.getNameEn() + " — reign begins",
                        (r.getDynastySlug() != null ? "Dynasty: " + r.getDynastySlug() + ". " : "") +
                                (r.getNote() != null ? r.getNote() : ""),
                        "RULER", r.getSlug(),
                        r.getSourceNote()));
            }
        });
        events.sort((a, b) -> {
            try { return Integer.compare(Integer.parseInt(a.year()), Integer.parseInt(b.year())); }
            catch (NumberFormatException e) { return a.year().compareTo(b.year()); }
        });
        return events;
    }
}
