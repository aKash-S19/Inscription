package com.heritage.kalvettu.dto;

import java.util.List;

public record InscriptionDetail(
        Long id, String slug, String templeSlug, String title, String titleTa,
        String referenceId, String areNumber, String siiReference, String epigraphiaIndica,
        String rulerSlug, String dynastySlug, String regnalYear, String dateNote,
        String language, String script, String physicalLocation,
        String originalText, String originalTextSource, String transliteration,
        String translation, String translationSource, String simpleExplanation,
        String historicalSignificance, String sourceCitation, String sourceUrl,
        Boolean verified, List<ImageDto> images, TempleCard temple) {
}
