package com.heritage.kalvettu.dto;

public record RulerDto(
        Long id, String slug, String nameEn, String nameTa, String dynastySlug,
        Integer reignStart, Integer reignEnd, String capital, String note, String sourceNote) {
}
