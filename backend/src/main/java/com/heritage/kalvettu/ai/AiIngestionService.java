package com.heritage.kalvettu.ai;

import org.springframework.stereotype.Service;

/**
 * AI-assisted data ingestion: converts a photo / scan of a Kalvettu (temple
 * inscription) — and/or raw pasted text — into a structured, verifiable record
 * that can then be reviewed and added to the archive dataset.
 *
 * Gemini reads the image with vision; the output is an ordered, parseable block
 * that mirrors the fields of the archive's inscription records.
 */
@Service
public class AiIngestionService {

    private final GeminiClient gemini;

    public AiIngestionService(GeminiClient gemini) {
        this.gemini = gemini;
    }

    public AiDtos.IngestResponse ingest(AiDtos.IngestRequest request) {
        boolean hasImage = request.imageBase64() != null && !request.imageBase64().isBlank();
        boolean hasText = request.text() != null && !request.text().isBlank();
        if (!hasImage && !hasText) {
            throw new IllegalArgumentException("Provide an inscription image and/or text.");
        }
        if (hasImage) {
            long approxBytes = (long) request.imageBase64().length() * 3L / 4L;
            if (approxBytes > 15L * 1024L * 1024L) {
                throw new IllegalArgumentException(
                        "Image is too large (approx " + (approxBytes / (1024L * 1024L))
                                + " MB). Please upload a smaller photo (under ~12 MB) "
                                + "or a cropped scan of the inscription.");
            }
        }

        String prompt = buildPrompt(request);
        String raw;

        if (hasImage) {
            String mime = (request.mimeType() == null || request.mimeType().isBlank())
                    ? "image/jpeg" : request.mimeType();
            raw = gemini.completeWithImage(prompt, request.imageBase64(), mime);
        } else {
            raw = gemini.complete(prompt);
        }

        return parse(raw);
    }

    private String buildPrompt(AiDtos.IngestRequest request) {
        StringBuilder sb = new StringBuilder();
        sb.append("""
                You are an expert epigrapher. Examine the provided temple inscription (Kalvettu)
                and extract the following structured fields. Be faithful to what is actually
                readable; where a field cannot be determined, write "Not determined".
                Do not invent rulers, dates, or references that are not visible.

                """);
        if (request.templeName() != null && !request.templeName().isBlank()) {
            sb.append("Known temple: ").append(request.templeName()).append("\n");
        }
        if (request.text() != null && !request.text().isBlank()) {
            sb.append("Transcribed text provided along with the image (use it to aid reading):\n---")
                    .append(request.text()).append("\n---\n");
        }

        sb.append("""

                Output ONLY in this exact labelled format:
                TITLE: <short descriptive title>
                LANGUAGE: <language, e.g. Tamil / Sanskrit>
                SCRIPT: <script, e.g. Grantha / Tamil medieval>
                TRANSLATION: <faithful translation into English>
                SIMPLE_EXPLANATION: <plain-language meaning>
                HISTORICAL_SIGNIFICANCE: <why it matters / what it records>
                RULER: <ruler if identifiable, else Not determined>
                NOTES: <any caveats about readability or missing parts>
                """);
        return sb.toString();
    }

    private AiDtos.IngestResponse parse(String raw) {
        return new AiDtos.IngestResponse(
                field(raw, "TITLE"),
                field(raw, "LANGUAGE"),
                field(raw, "SCRIPT"),
                field(raw, "TRANSLATION"),
                field(raw, "SIMPLE_EXPLANATION"),
                field(raw, "HISTORICAL_SIGNIFICANCE"),
                field(raw, "RULER"),
                field(raw, "NOTES"));
    }

    private String field(String raw, String label) {
        if (raw == null) {
            return "";
        }
        String marker = label + ":";
        int idx = raw.indexOf(marker);
        if (idx < 0) {
            return "";
        }
        int start = idx + marker.length();
        int end = raw.length();
        for (String next : new String[]{"TITLE:", "LANGUAGE:", "SCRIPT:", "TRANSLATION:",
                "SIMPLE_EXPLANATION:", "HISTORICAL_SIGNIFICANCE:", "RULER:", "NOTES:"}) {
            if (next.equals(marker)) {
                continue;
            }
            int pos = raw.indexOf(next, start);
            if (pos > start && pos < end) {
                end = pos;
            }
        }
        return raw.substring(start, end).trim();
    }
}
