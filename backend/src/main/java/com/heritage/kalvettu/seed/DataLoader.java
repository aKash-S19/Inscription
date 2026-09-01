package com.heritage.kalvettu.seed;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.heritage.kalvettu.domain.*;
import com.heritage.kalvettu.repository.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;

/**
 * Loads the verified dataset (data/dataset.json) and, if present, the
 * validated Wikimedia Commons image list (data/commons_images.json) into the
 * database on startup. Idempotent: skips loading when temples already exist.
 *
 * Images are kept in a separate file so that the (slow, rate-limited) Commons
 * URL validation can be re-run independently of the textual dataset.
 */
@Component
public class DataLoader implements CommandLineRunner {

    private static final Logger log = LoggerFactory.getLogger(DataLoader.class);

    private final TempleRepository templeRepository;
    private final InscriptionRepository inscriptionRepository;
    private final ImageRepository imageRepository;
    private final DynastyRepository dynastyRepository;
    private final RulerRepository rulerRepository;
    private final DistrictRepository districtRepository;
    private final InscriptionLocationRepository locationRepository;
    private final ObjectMapper mapper = new ObjectMapper();

    public DataLoader(TempleRepository templeRepository, InscriptionRepository inscriptionRepository,
                      ImageRepository imageRepository, DynastyRepository dynastyRepository,
                      RulerRepository rulerRepository, DistrictRepository districtRepository,
                      InscriptionLocationRepository locationRepository) {
        this.templeRepository = templeRepository;
        this.inscriptionRepository = inscriptionRepository;
        this.imageRepository = imageRepository;
        this.dynastyRepository = dynastyRepository;
        this.rulerRepository = rulerRepository;
        this.districtRepository = districtRepository;
        this.locationRepository = locationRepository;
    }

    @Override
    public void run(String... args) throws Exception {
        if (templeRepository.count() > 0) {
            log.info("Dataset already present ({} temples); skipping seed.", templeRepository.count());
            return;
        }

        Map<String, Object> data = mapper.readValue(
                new ClassPathResource("data/dataset.json").getInputStream(),
                new TypeReference<Map<String, Object>>() {});

        List<Map<String, Object>> dynasties = (List<Map<String, Object>>) data.get("dynasties");
        if (dynasties != null) dynasties.forEach(d -> {
            Dynasty e = new Dynasty();
            e.setSlug((String) d.get("slug"));
            e.setNameEn((String) d.get("nameEn"));
            e.setNameTa((String) d.get("nameTa"));
            e.setStartYear(asInt(d.get("startYear")));
            e.setEndYear(asInt(d.get("endYear")));
            e.setCapital((String) d.get("capital"));
            e.setDescription((String) d.get("description"));
            e.setSourceNote((String) d.get("sourceNote"));
            dynastyRepository.save(e);
        });

        List<Map<String, Object>> rulers = (List<Map<String, Object>>) data.get("rulers");
        if (rulers != null) rulers.forEach(r -> {
            Ruler e = new Ruler();
            e.setSlug((String) r.get("slug"));
            e.setNameEn((String) r.get("nameEn"));
            e.setNameTa((String) r.get("nameTa"));
            e.setDynastySlug((String) r.get("dynastySlug"));
            e.setReignStart(asInt(r.get("reignStart")));
            e.setReignEnd(asInt(r.get("reignEnd")));
            e.setCapital((String) r.get("capital"));
            e.setNote((String) r.get("note"));
            e.setSourceNote((String) r.get("sourceNote"));
            rulerRepository.save(e);
        });

        List<Map<String, Object>> districts = (List<Map<String, Object>>) data.get("districts");
        if (districts != null) districts.forEach(d -> {
            District e = new District();
            e.setSlug((String) d.get("slug"));
            e.setNameEn((String) d.get("nameEn"));
            e.setHeadquarters((String) d.get("headquarters"));
            e.setLat(asDouble(d.get("lat")));
            e.setLng(asDouble(d.get("lng")));
            e.setNote((String) d.get("note"));
            districtRepository.save(e);
        });

        List<Map<String, Object>> temples = (List<Map<String, Object>>) data.get("temples");
        if (temples != null) temples.forEach(t -> {
            Temple e = new Temple();
            e.setSlug((String) t.get("slug"));
            e.setNameEn((String) t.get("nameEn"));
            e.setNameTa((String) t.get("nameTa"));
            e.setAlternateNames((String) t.get("alternateNames"));
            e.setDistrictSlug((String) t.get("districtSlug"));
            e.setTown((String) t.get("town"));
            e.setDeity((String) t.get("deity"));
            e.setDynastySlug((String) t.get("dynastySlug"));
            e.setPatron((String) t.get("patron"));
            e.setPeriodNote((String) t.get("periodNote"));
            e.setConsecrationYear(asInt(t.get("consecrationYear")));
            e.setLat(asDouble(t.get("lat")));
            e.setLng(asDouble(t.get("lng")));
            e.setUnescoWorldHeritage(asBool(t.get("unescoWorldHeritage")));
            e.setUnescoUrl((String) t.get("unescoUrl"));
            e.setAsiMonument(asBool(t.get("asiMonument")));
            e.setAsiUrl((String) t.get("asiUrl"));
            e.setManagedBy((String) t.get("managedBy"));
            e.setHistory((String) t.get("history"));
            e.setArchitecture((String) t.get("architecture"));
            e.setSummary((String) t.get("summary"));
            e.setVerified(asBool(t.get("verified"), true));
            e.setSourceNote((String) t.get("sourceNote"));
            templeRepository.save(e);
        });

        List<Map<String, Object>> inscriptions = (List<Map<String, Object>>) data.get("inscriptions");
        if (inscriptions != null) inscriptions.forEach(i -> {
            Inscription e = new Inscription();
            e.setSlug((String) i.get("slug"));
            e.setTempleSlug((String) i.get("templeSlug"));
            e.setTitle((String) i.get("title"));
            e.setTitleTa((String) i.get("titleTa"));
            e.setReferenceId((String) i.get("referenceId"));
            e.setAreNumber((String) i.get("areNumber"));
            e.setSiiReference((String) i.get("siiReference"));
            e.setEpigraphiaIndica((String) i.get("epigraphiaIndica"));
            e.setRulerSlug((String) i.get("rulerSlug"));
            e.setDynastySlug((String) i.get("dynastySlug"));
            e.setRegnalYear((String) i.get("regnalYear"));
            e.setDateNote((String) i.get("dateNote"));
            e.setLanguage((String) i.get("language"));
            e.setScript((String) i.get("script"));
            e.setPhysicalLocation((String) i.get("physicalLocation"));
            e.setOriginalText((String) i.get("originalText"));
            e.setOriginalTextSource((String) i.get("originalTextSource"));
            e.setTransliteration((String) i.get("transliteration"));
            e.setTranslation((String) i.get("translation"));
            e.setTranslationSource((String) i.get("translationSource"));
            e.setSimpleExplanation((String) i.get("simpleExplanation"));
            e.setHistoricalSignificance((String) i.get("historicalSignificance"));
            e.setSourceCitation((String) i.get("sourceCitation"));
            e.setSourceUrl((String) i.get("sourceUrl"));
            e.setVerified(asBool(i.get("verified"), true));
            inscriptionRepository.save(e);
        });

        List<Map<String, Object>> locations = (List<Map<String, Object>>) data.get("inscriptionLocations");
        if (locations != null) locations.forEach(l -> {
            InscriptionLocation e = new InscriptionLocation();
            e.setInscriptionSlug((String) l.get("inscriptionSlug"));
            e.setTempleSlug((String) l.get("templeSlug"));
            e.setLabel((String) l.get("label"));
            e.setDescription((String) l.get("description"));
            e.setArea((String) l.get("area"));
            e.setMapX(asDouble(l.get("mapX")));
            e.setMapY(asDouble(l.get("mapY")));
            e.setCoordinateSystem((String) l.get("coordinateSystem"));
            e.setLat(asDouble(l.get("lat")));
            e.setLng(asDouble(l.get("lng")));
            locationRepository.save(e);
        });

        loadImages();
        log.info("Seed complete: {} temples, {} inscriptions, {} dynasties, {} rulers, {} districts, {} locations.",
                temples == null ? 0 : temples.size(),
                inscriptions == null ? 0 : inscriptions.size(),
                dynasties == null ? 0 : dynasties.size(),
                rulers == null ? 0 : rulers.size(),
                districts == null ? 0 : districts.size(),
                locations == null ? 0 : locations.size());
    }

    @SuppressWarnings("unchecked")
    private void loadImages() throws Exception {
        ClassPathResource res = new ClassPathResource("data/commons_images.json");
        if (!res.exists()) {
            log.info("No data/commons_images.json found; skipping image seed.");
            return;
        }
        Map<String, List<Map<String, Object>>> byTemple = mapper.readValue(
                res.getInputStream(), new TypeReference<Map<String, List<Map<String, Object>>>>() {});

        // map temple slug -> entity slug used in dataset
        Map<String, String> slugMap = Map.of(
                "brihadisvara-thanjavur", "brihadisvara-thanjavur",
                "gangaikondacholapuram", "gangaikondacholapuram",
                "airavatesvara-darasuram", "airavatesvara-darasuram",
                "kailasanathar-kanchipuram", "kailasanathar-kanchipuram",
                "shore-mamallapuram", "shore-mamallapuram",
                "nataraja-chidambaram", "nataraja-chidambaram"
        );

        int count = 0;
        for (Map.Entry<String, List<Map<String, Object>>> entry : byTemple.entrySet()) {
            String entitySlug = slugMap.get(entry.getKey());
            if (entitySlug == null) continue;
            List<Map<String, Object>> imgs = entry.getValue();
            int idx = 0;
            for (Map<String, Object> im : imgs) {
                Image e = new Image();
                e.setEntityType("TEMPLE");
                e.setEntitySlug(entitySlug);
                e.setCategory(idx == 0 ? "exterior" : "detail");
                e.setCommonsFile((String) im.get("title"));
                e.setImageUrl((String) im.get("url"));
                e.setThumbUrl((String) im.get("thumb"));
                e.setWidth(asInt(im.get("width")));
                e.setHeight(asInt(im.get("height")));
                e.setAuthor((String) im.get("author"));
                e.setLicense((String) im.get("license"));
                e.setLicenseUrl((String) im.get("license_url"));
                e.setCommonsUrl((String) im.get("commons_url"));
                e.setCaption("Photograph from Wikimedia Commons: " + (String) im.get("title"));
                imageRepository.save(e);
                count++;
                idx++;
            }
        }
        log.info("Image seed complete: {} validated images.", count);
    }

    private Integer asInt(Object o) {
        return o == null ? null : ((Number) o).intValue();
    }

    private Double asDouble(Object o) {
        return o == null ? null : ((Number) o).doubleValue();
    }

    private Boolean asBool(Object o) {
        return asBool(o, false);
    }

    private Boolean asBool(Object o, boolean dflt) {
        return o == null ? dflt : (Boolean) o;
    }
}
