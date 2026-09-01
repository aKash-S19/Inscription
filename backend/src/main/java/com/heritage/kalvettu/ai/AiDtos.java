package com.heritage.kalvettu.ai;

import java.util.List;

/**
 * Request/response records shared by the AI endpoints.
 * Kept as lightweight records so the frontend has simple, typed JSON.
 */
public final class AiDtos {

    private AiDtos() {
    }

    /** A single chat turn. */
    public record ChatMessage(String role, String content) {
    }

    /** Chat request: conversation history + a target output language (optional). */
    public record ChatRequest(List<ChatMessage> messages, String language) {
    }

    /** Chat / assistant response. */
    public record ChatResponse(String answer, String language) {
    }

    /** Translation request: the inscription text + optional target language. */
    public record TranslateRequest(String text, String targetLanguage) {
    }

    /** Translation + plain-language explanation response. */
    public record TranslateResponse(String translation, String explanation, String targetLanguage) {
    }

    /** Ingestion request: optional image (base64) and/or text of a kalvettu. */
    public record IngestRequest(String imageBase64, String mimeType, String text, String templeName) {
    }

    /** Structured record extracted from a submitted kalvettu image/text. */
    public record IngestResponse(
            String title,
            String language,
            String script,
            String translation,
            String simpleExplanation,
            String historicalSignificance,
            String ruler,
            String notes) {
    }
}
