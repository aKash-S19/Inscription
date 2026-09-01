package com.heritage.kalvettu.domain;

import jakarta.persistence.*;

/**
 * A South Indian dynasty represented in Tamil temple epigraphy
 * (Pallava, Chola, Pandya, Vijayanagara, Nayak, ...).
 */
@Entity
@Table(name = "dynasties")
public class Dynasty {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String slug;

    @Column(name = "name_en", nullable = false)
    private String nameEn;

    @Column(name = "name_ta")
    private String nameTa;

    @Column(name = "start_year")
    private Integer startYear;

    @Column(name = "end_year")
    private Integer endYear;

    @Column(name = "capital")
    private String capital;

    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    @Column(name = "source_note", columnDefinition = "TEXT")
    private String sourceNote;

    public Dynasty() {
    }

    public Dynasty(String slug, String nameEn, String nameTa, Integer startYear,
                   Integer endYear, String capital, String description, String sourceNote) {
        this.slug = slug;
        this.nameEn = nameEn;
        this.nameTa = nameTa;
        this.startYear = startYear;
        this.endYear = endYear;
        this.capital = capital;
        this.description = description;
        this.sourceNote = sourceNote;
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
    public Integer getStartYear() { return startYear; }
    public void setStartYear(Integer startYear) { this.startYear = startYear; }
    public Integer getEndYear() { return endYear; }
    public void setEndYear(Integer endYear) { this.endYear = endYear; }
    public String getCapital() { return capital; }
    public void setCapital(String capital) { this.capital = capital; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public String getSourceNote() { return sourceNote; }
    public void setSourceNote(String sourceNote) { this.sourceNote = sourceNote; }
}
