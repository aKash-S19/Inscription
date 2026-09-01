package com.heritage.kalvettu.dto;

public record ImageDto(
        Long id, String entityType, String entitySlug, String category,
        String imageUrl, String thumbUrl, Integer width, Integer height,
        String author, String license, String licenseUrl, String commonsUrl, String caption) {
}
