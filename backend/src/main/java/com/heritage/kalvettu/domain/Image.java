package com.heritage.kalvettu.domain;

import jakarta.persistence.*;

/**
 * A real, freely-licensed photograph. At present sourced from Wikimedia Commons
 * with full author + license attribution.
 */
@Entity
@Table(name = "images")
public class Image {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "entity_type", nullable = false)
    private String entityType; // TEMPLE | INSCRIPTION

    @Column(name = "entity_slug", nullable = false)
    private String entitySlug;

    @Column(name = "category")
    private String category; // exterior | detail | interior | sculpture | inscription | plan

    @Column(name = "commons_file", columnDefinition = "TEXT")
    private String commonsFile;

    @Column(name = "image_url", columnDefinition = "TEXT", nullable = false)
    private String imageUrl;

    @Column(name = "thumb_url", columnDefinition = "TEXT")
    private String thumbUrl;

    @Column(name = "width")
    private Integer width;

    @Column(name = "height")
    private Integer height;

    @Column(name = "author", columnDefinition = "TEXT")
    private String author;

    @Column(name = "license", columnDefinition = "TEXT")
    private String license;

    @Column(name = "license_url", columnDefinition = "TEXT")
    private String licenseUrl;

    @Column(name = "commons_url", columnDefinition = "TEXT")
    private String commonsUrl;

    @Column(name = "caption", columnDefinition = "TEXT")
    private String caption;

    public Image() {
    }

    // getters & setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getEntityType() { return entityType; }
    public void setEntityType(String entityType) { this.entityType = entityType; }
    public String getEntitySlug() { return entitySlug; }
    public void setEntitySlug(String entitySlug) { this.entitySlug = entitySlug; }
    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }
    public String getCommonsFile() { return commonsFile; }
    public void setCommonsFile(String commonsFile) { this.commonsFile = commonsFile; }
    public String getImageUrl() { return imageUrl; }
    public void setImageUrl(String imageUrl) { this.imageUrl = imageUrl; }
    public String getThumbUrl() { return thumbUrl; }
    public void setThumbUrl(String thumbUrl) { this.thumbUrl = thumbUrl; }
    public Integer getWidth() { return width; }
    public void setWidth(Integer width) { this.width = width; }
    public Integer getHeight() { return height; }
    public void setHeight(Integer height) { this.height = height; }
    public String getAuthor() { return author; }
    public void setAuthor(String author) { this.author = author; }
    public String getLicense() { return license; }
    public void setLicense(String license) { this.license = license; }
    public String getLicenseUrl() { return licenseUrl; }
    public void setLicenseUrl(String licenseUrl) { this.licenseUrl = licenseUrl; }
    public String getCommonsUrl() { return commonsUrl; }
    public void setCommonsUrl(String commonsUrl) { this.commonsUrl = commonsUrl; }
    public String getCaption() { return caption; }
    public void setCaption(String caption) { this.caption = caption; }
}
