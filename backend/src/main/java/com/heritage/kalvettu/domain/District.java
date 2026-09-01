package com.heritage.kalvettu.domain;

import jakarta.persistence.*;

/**
 * Present-day Tamil Nadu district used to group temples and inscriptions.
 */
@Entity
@Table(name = "districts")
public class District {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String slug;

    @Column(name = "name_en", nullable = false)
    private String nameEn;

    @Column(name = "headquarters")
    private String headquarters;

    @Column(name = "lat")
    private Double lat;

    @Column(name = "lng")
    private Double lng;

    @Column(name = "note", columnDefinition = "TEXT")
    private String note;

    public District() {
    }

    public District(String slug, String nameEn, String headquarters, Double lat, Double lng, String note) {
        this.slug = slug;
        this.nameEn = nameEn;
        this.headquarters = headquarters;
        this.lat = lat;
        this.lng = lng;
        this.note = note;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getSlug() { return slug; }
    public void setSlug(String slug) { this.slug = slug; }
    public String getNameEn() { return nameEn; }
    public void setNameEn(String nameEn) { this.nameEn = nameEn; }
    public String getHeadquarters() { return headquarters; }
    public void setHeadquarters(String headquarters) { this.headquarters = headquarters; }
    public Double getLat() { return lat; }
    public void setLat(Double lat) { this.lat = lat; }
    public Double getLng() { return lng; }
    public void setLng(Double lng) { this.lng = lng; }
    public String getNote() { return note; }
    public void setNote(String note) { this.note = note; }
}
