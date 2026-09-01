package com.heritage.kalvettu.domain;

import jakarta.persistence.*;

/**
 * A historical ruler (king/queen) appearing in Tamil temple inscriptions.
 */
@Entity
@Table(name = "rulers")
public class Ruler {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String slug;

    @Column(name = "name_en", nullable = false)
    private String nameEn;

    @Column(name = "name_ta")
    private String nameTa;

    @Column(name = "dynasty_slug")
    private String dynastySlug;

    @Column(name = "reign_start")
    private Integer reignStart;

    @Column(name = "reign_end")
    private Integer reignEnd;

    @Column(name = "capital")
    private String capital;

    @Column(name = "note", columnDefinition = "TEXT")
    private String note;

    @Column(name = "source_note", columnDefinition = "TEXT")
    private String sourceNote;

    public Ruler() {
    }

    public Ruler(String slug, String nameEn, String nameTa, String dynastySlug,
                 Integer reignStart, Integer reignEnd, String capital, String note,
                 String sourceNote) {
        this.slug = slug;
        this.nameEn = nameEn;
        this.nameTa = nameTa;
        this.dynastySlug = dynastySlug;
        this.reignStart = reignStart;
        this.reignEnd = reignEnd;
        this.capital = capital;
        this.note = note;
        this.sourceNote = sourceNote;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getSlug() { return slug; }
    public void setSlug(String slug) { this.slug = slug; }
    public String getNameEn() { return nameEn; }
    public void setNameEn(String nameEn) { this.nameEn = nameEn; }
    public String getNameTa() { return nameTa; }
    public void setNameTa(String nameTa) { this.nameTa = nameTa; }
    public String getDynastySlug() { return dynastySlug; }
    public void setDynastySlug(String dynastySlug) { this.dynastySlug = dynastySlug; }
    public Integer getReignStart() { return reignStart; }
    public void setReignStart(Integer reignStart) { this.reignStart = reignStart; }
    public Integer getReignEnd() { return reignEnd; }
    public void setReignEnd(Integer reignEnd) { this.reignEnd = reignEnd; }
    public String getCapital() { return capital; }
    public void setCapital(String capital) { this.capital = capital; }
    public String getNote() { return note; }
    public void setNote(String note) { this.note = note; }
    public String getSourceNote() { return sourceNote; }
    public void setSourceNote(String sourceNote) { this.sourceNote = sourceNote; }
}
