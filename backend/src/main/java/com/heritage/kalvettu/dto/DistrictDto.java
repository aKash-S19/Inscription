package com.heritage.kalvettu.dto;

public record DistrictDto(
        Long id, String slug, String nameEn, String headquarters, Double lat, Double lng, String note) {
}
