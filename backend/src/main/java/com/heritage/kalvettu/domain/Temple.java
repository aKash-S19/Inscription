package com.heritage.kalvettu.domain;

import jakarta.persistence.*;

/**
 * A documented Tamil temple. Every field is sourced; fields that cannot be
 * verified are left null rather than invented.
 */
@Entity
@Table(name = "temples")
public class Temple {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String slug;

    @Column(name = "name_en", nullable = false)
    private String nameEn;

    @Column(name = "name_ta")
    private String nameTa;

    @Column(name = "alternate_names", columnDefinition = "TEXT")
    private String alternateNames;

    @Column(name = "district_slug")
    private String districtSlug;

    @Column(name = "town")
    private String town;

    @Column(name = "deity")
    private String deity;

    @Column(name = "dynasty_slug")
    private String dynastySlug;

    @Column(name = "patron")
    private String patron;

    @Column(name = "period_note", columnDefinition = "TEXT")
    private String periodNote;

    @Column(name = "consecration_year")
    private Integer consecrationYear;

    @Column(name = "lat")
    private Double lat;

    @Column(name = "lng")
    private Double lng;

    @Column(name = "unesco_world_heritage")
    private Boolean unescoWorldHeritage = false;

    @Column(name = "unesco_url", columnDefinition = "TEXT")
    private String unescoUrl;

    @Column(name = "asi_monument")
    private Boolean asiMonument = false;

    @Column(name = "asi_url", columnDefinition = "TEXT")
    private String asiUrl;

    @Column(name = "managed_by")
    private String managedBy;

    @Column(name = "history", columnDefinition = "TEXT")
    private String history;

    @Column(name = "architecture", columnDefinition = "TEXT")
    private String architecture;

    @Column(name = "summary", columnDefinition = "TEXT")
    private String summary;

    @Column(name = "verified")
    private Boolean verified = true;

    @Column(name = "source_note", columnDefinition = "TEXT")
    private String sourceNote;

    public Temple() {
    }

    // getters & setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getSlug() { return slug; }
    public void setSlug(String slug) { this.slug = slug; }
    public String getNameEn() { return nameEn; }
    public void setNameEn(String nameEn) { this.nameEn = nameEn; }
    public String getNameTa() { return nameTa; }
    public void setNameTa(String nameTa) { this.nameTa = nameTa; }
    public String getAlternateNames() { return alternateNames; }
    public void setAlternateNames(String alternateNames) { this.alternateNames = alternateNames; }
    public String getDistrictSlug() { return districtSlug; }
    public void setDistrictSlug(String districtSlug) { this.districtSlug = districtSlug; }
    public String getTown() { return town; }
    public void setTown(String town) { this.town = town; }
    public String getDeity() { return deity; }
    public void setDeity(String deity) { this.deity = deity; }
    public String getDynastySlug() { return dynastySlug; }
    public void setDynastySlug(String dynastySlug) { this.dynastySlug = dynastySlug; }
    public String getPatron() { return patron; }
    public void setPatron(String patron) { this.patron = patron; }
    public String getPeriodNote() { return periodNote; }
    public void setPeriodNote(String periodNote) { this.periodNote = periodNote; }
    public Integer getConsecrationYear() { return consecrationYear; }
    public void setConsecrationYear(Integer consecrationYear) { this.consecrationYear = consecrationYear; }
    public Double getLat() { return lat; }
    public void setLat(Double lat) { this.lat = lat; }
    public Double getLng() { return lng; }
    public void setLng(Double lng) { this.lng = lng; }
    public Boolean getUnescoWorldHeritage() { return unescoWorldHeritage; }
    public void setUnescoWorldHeritage(Boolean unescoWorldHeritage) { this.unescoWorldHeritage = unescoWorldHeritage; }
    public String getUnescoUrl() { return unescoUrl; }
    public void setUnescoUrl(String unescoUrl) { this.unescoUrl = unescoUrl; }
    public Boolean getAsiMonument() { return asiMonument; }
    public void setAsiMonument(Boolean asiMonument) { this.asiMonument = asiMonument; }
    public String getAsiUrl() { return asiUrl; }
    public void setAsiUrl(String asiUrl) { this.asiUrl = asiUrl; }
    public String getManagedBy() { return managedBy; }
    public void setManagedBy(String managedBy) { this.managedBy = managedBy; }
    public String getHistory() { return history; }
    public void setHistory(String history) { this.history = history; }
    public String getArchitecture() { return architecture; }
    public void setArchitecture(String architecture) { this.architecture = architecture; }
    public String getSummary() { return summary; }
    public void setSummary(String summary) { this.summary = summary; }
    public Boolean getVerified() { return verified; }
    public void setVerified(Boolean verified) { this.verified = verified; }
    public String getSourceNote() { return sourceNote; }
    public void setSourceNote(String sourceNote) { this.sourceNote = sourceNote; }
}
