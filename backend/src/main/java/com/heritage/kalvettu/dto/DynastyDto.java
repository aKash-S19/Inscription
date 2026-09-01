package com.heritage.kalvettu.dto;

public record DynastyDto(
        Long id, String slug, String nameEn, String nameTa, Integer startYear,
        Integer endYear, String capital, String description, String sourceNote) {
}
