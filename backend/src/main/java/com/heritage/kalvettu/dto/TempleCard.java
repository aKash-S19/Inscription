package com.heritage.kalvettu.dto;

public record TempleCard(
        Long id, String slug, String nameEn, String nameTa, String town,
        String districtSlug, String dynastySlug, String deity, String periodNote,
        Integer consecrationYear, Double lat, Double lng, String summary,
        Boolean unescoWorldHeritage, Boolean asiMonument, String heroImageUrl) {
}
