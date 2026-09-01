package com.heritage.kalvettu.dto;

public record TimelineEvent(
        String year, String title, String description, String type,
        String relatedSlug, String sourceNote) {
}
