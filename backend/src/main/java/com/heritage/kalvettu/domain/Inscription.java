package com.heritage.kalvettu.domain;

import jakarta.persistence.*;

/**
 * A single documented temple inscription (Kalvettu).
 *
 * Integrity rule: nothing here is invented. Fields that cannot be verified
 * from a primary/authoritative source are left null and the UI renders them
 * as "Not recorded in a citable source".
 */
@Entity
@Table(name = "inscriptions")
public class Inscription {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String slug;

    @Column(name = "temple_slug", nullable = false)
    private String templeSlug;

    @Column(name = "title", nullable = false)
    private String title;

    @Column(name = "title_ta")
    private String titleTa;

    /** Stable reference used in the source publication, e.g. "SII Vol. II, No. 91". */
    @Column(name = "reference_id")
    private String referenceId;

    @Column(name = "are_number")
    private String areNumber;

    @Column(name = "sii_reference")
    private String siiReference;

    @Column(name = "epigraphia_indica")
    private String epigraphiaIndica;

    @Column(name = "ruler_slug")
    private String rulerSlug;

    @Column(name = "dynasty_slug")
    private String dynastySlug;

    @Column(name = "regnal_year")
    private String regnalYear;

    @Column(name = "date_note", columnDefinition = "TEXT")
    private String dateNote;

    @Column(name = "language")
    private String language;

    @Column(name = "script")
    private String script;

    /** Physical location of the inscription inside the temple (verified only). */
    @Column(name = "physical_location", columnDefinition = "TEXT")
    private String physicalLocation;

    /** Original inscription text in Tamil / Grantha script (only when from a source). */
    @Column(name = "original_text", columnDefinition = "TEXT")
    private String originalText;

    @Column(name = "original_text_source", columnDefinition = "TEXT")
    private String originalTextSource;

    @Column(name = "transliteration", columnDefinition = "TEXT")
    private String transliteration;

    @Column(name = "translation", columnDefinition = "TEXT")
    private String translation;

    @Column(name = "translation_source", columnDefinition = "TEXT")
    private String translationSource;

    @Column(name = "simple_explanation", columnDefinition = "TEXT")
    private String simpleExplanation;

    @Column(name = "historical_significance", columnDefinition = "TEXT")
    private String historicalSignificance;

    @Column(name = "source_citation", columnDefinition = "TEXT", nullable = false)
    private String sourceCitation;

    @Column(name = "source_url", columnDefinition = "TEXT")
    private String sourceUrl;

    @Column(name = "verified")
    private Boolean verified = true;

    public Inscription() {
    }

    // getters & setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getSlug() { return slug; }
    public void setSlug(String slug) { this.slug = slug; }
    public String getTempleSlug() { return templeSlug; }
    public void setTempleSlug(String templeSlug) { this.templeSlug = templeSlug; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getTitleTa() { return titleTa; }
    public void setTitleTa(String titleTa) { this.titleTa = titleTa; }
    public String getReferenceId() { return referenceId; }
    public void setReferenceId(String referenceId) { this.referenceId = referenceId; }
    public String getAreNumber() { return areNumber; }
    public void setAreNumber(String areNumber) { this.areNumber = areNumber; }
    public String getSiiReference() { return siiReference; }
    public void setSiiReference(String siiReference) { this.siiReference = siiReference; }
    public String getEpigraphiaIndica() { return epigraphiaIndica; }
    public void setEpigraphiaIndica(String epigraphiaIndica) { this.epigraphiaIndica = epigraphiaIndica; }
    public String getRulerSlug() { return rulerSlug; }
    public void setRulerSlug(String rulerSlug) { this.rulerSlug = rulerSlug; }
    public String getDynastySlug() { return dynastySlug; }
    public void setDynastySlug(String dynastySlug) { this.dynastySlug = dynastySlug; }
    public String getRegnalYear() { return regnalYear; }
    public void setRegnalYear(String regnalYear) { this.regnalYear = regnalYear; }
    public String getDateNote() { return dateNote; }
    public void setDateNote(String dateNote) { this.dateNote = dateNote; }
    public String getLanguage() { return language; }
    public void setLanguage(String language) { this.language = language; }
    public String getScript() { return script; }
    public void setScript(String script) { this.script = script; }
    public String getPhysicalLocation() { return physicalLocation; }
    public void setPhysicalLocation(String physicalLocation) { this.physicalLocation = physicalLocation; }
    public String getOriginalText() { return originalText; }
    public void setOriginalText(String originalText) { this.originalText = originalText; }
    public String getOriginalTextSource() { return originalTextSource; }
    public void setOriginalTextSource(String originalTextSource) { this.originalTextSource = originalTextSource; }
    public String getTransliteration() { return transliteration; }
    public void setTransliteration(String transliteration) { this.transliteration = transliteration; }
    public String getTranslation() { return translation; }
    public void setTranslation(String translation) { this.translation = translation; }
    public String getTranslationSource() { return translationSource; }
    public void setTranslationSource(String translationSource) { this.translationSource = translationSource; }
    public String getSimpleExplanation() { return simpleExplanation; }
    public void setSimpleExplanation(String simpleExplanation) { this.simpleExplanation = simpleExplanation; }
    public String getHistoricalSignificance() { return historicalSignificance; }
    public void setHistoricalSignificance(String historicalSignificance) { this.historicalSignificance = historicalSignificance; }
    public String getSourceCitation() { return sourceCitation; }
    public void setSourceCitation(String sourceCitation) { this.sourceCitation = sourceCitation; }
    public String getSourceUrl() { return sourceUrl; }
    public void setSourceUrl(String sourceUrl) { this.sourceUrl = sourceUrl; }
    public Boolean getVerified() { return verified; }
    public void setVerified(Boolean verified) { this.verified = verified; }
}
