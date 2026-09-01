package com.heritage.kalvettu.domain;

import jakarta.persistence.*;

/**
 * A documented point inside a temple where an inscription is physically located.
 * Used by the interactive temple map. We NEVER invent locations: every row must
 * correspond to a verified inscription whose physical location is known.
 */
@Entity
@Table(name = "inscription_locations")
public class InscriptionLocation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "inscription_slug", nullable = false)
    private String inscriptionSlug;

    @Column(name = "temple_slug", nullable = false)
    private String templeSlug;

    @Column(name = "label", nullable = false)
    private String label;

    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    @Column(name = "area", columnDefinition = "TEXT")
    private String area;

    /** Coordinates relative to the temple plan. If an authoritative temple plan
     *  with a coordinate system is available we use it; otherwise these are
     *  approximate in-temple markers and flagged accordingly. */
    @Column(name = "map_x")
    private Double mapX;

    @Column(name = "map_y")
    private Double mapY;

    @Column(name = "coordinate_system")
    private String coordinateSystem;

    @Column(name = "lat")
    private Double lat;

    @Column(name = "lng")
    private Double lng;

    public InscriptionLocation() {
    }

    // getters & setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getInscriptionSlug() { return inscriptionSlug; }
    public void setInscriptionSlug(String inscriptionSlug) { this.inscriptionSlug = inscriptionSlug; }
    public String getTempleSlug() { return templeSlug; }
    public void setTempleSlug(String templeSlug) { this.templeSlug = templeSlug; }
    public String getLabel() { return label; }
    public void setLabel(String label) { this.label = label; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public String getArea() { return area; }
    public void setArea(String area) { this.area = area; }
    public Double getMapX() { return mapX; }
    public void setMapX(Double mapX) { this.mapX = mapX; }
    public Double getMapY() { return mapY; }
    public void setMapY(Double mapY) { this.mapY = mapY; }
    public String getCoordinateSystem() { return coordinateSystem; }
    public void setCoordinateSystem(String coordinateSystem) { this.coordinateSystem = coordinateSystem; }
    public Double getLat() { return lat; }
    public void setLat(Double lat) { this.lat = lat; }
    public Double getLng() { return lng; }
    public void setLng(Double lng) { this.lng = lng; }
}
