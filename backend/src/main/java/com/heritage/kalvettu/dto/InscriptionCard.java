package com.heritage.kalvettu.dto;

public record InscriptionCard(
        Long id, String slug, String templeSlug, String title, String titleTa,
        String referenceId, String areNumber, String siiReference, String rulerSlug,
        String dynastySlug, String regnalYear, String language, String script,
        String physicalLocation, String thumbImageUrl, Boolean verified) {
}
