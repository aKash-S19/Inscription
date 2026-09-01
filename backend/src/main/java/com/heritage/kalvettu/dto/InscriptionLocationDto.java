package com.heritage.kalvettu.dto;

public record InscriptionLocationDto(
        Long id, String inscriptionSlug, String templeSlug, String label,
        String description, String area, Double mapX, Double mapY,
        String coordinateSystem, Double lat, Double lng) {
}
