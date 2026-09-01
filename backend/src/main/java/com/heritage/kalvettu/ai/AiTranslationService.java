package com.heritage.kalvettu.ai;

import org.springframework.stereotype.Service;

/**
 * Handles translation of Kalvettu (temple inscription) text into any target
 * language, together with a plain-language explanation of its meaning.
 *
 * The endpoint intentionally does NOT rely on an inscription slug existing in
 * the archive: any Tamil / Grantha kalvettu text (or image, via the ingestion
 * path) can be translated on demand.
 */
@Service
public class AiTranslationService {

    private final GeminiClient gemini;

    public AiTranslationService(GeminiClient gemini) {
        this.gemini = gemini;
    }

    public AiDtos.TranslateResponse translate(AiDtos.TranslateRequest request) {
        String text = (request.text() == null ? "" : request.text()).trim();
        if (text.isEmpty()) {
            throw new IllegalArgumentException("text must not be blank");
        }
        String target = (request.targetLanguage() == null || request.targetLanguage().isBlank())
                ? "English" : request.targetLanguage();

        String prompt = """
                You are an expert epigrapher for ancient Tamil temple inscriptions (Kalvettu).

                ORIGINAL INSCRIPTION TEXT:
                ---
                %s
                ---

                TASK:
                1. TRANSLATION: Translate the inscription faithfully into %s.
                2. EXPLANATION: Provide a plain-language explanation of what the inscription
                   records (who, what, when, why) for a general reader.
                - Be faithful; where a passage is unclear, note it rather than guessing.
                - Only translate/explain the provided text; do not add facts from outside.

                Respond in exactly this format:
                TRANSLATION:
                <translation>

                EXPLANATION:
                <plain-language explanation>
                """.formatted(text, target);

        String raw = gemini.complete(prompt);
        String translation = extractSection(raw, "TRANSLATION");
        String explanation = extractSection(raw, "EXPLANATION");

        return new AiDtos.TranslateResponse(translation, explanation, target);
    }

    private String extractSection(String raw, String header) {
        if (raw == null) {
            return "";
        }
        String marker = header + ":";
        int idx = raw.indexOf(marker);
        int start = idx >= 0 ? idx + marker.length() : 0;

        // Cut at the next section header if present.
        int next = raw.indexOf("EXPLANATION:", start);
        int nf = raw.indexOf("TRANSLATION:", start);
        int min = raw.length();
        for (int pos : new int[]{next, nf}) {
            if (pos > start && pos < min) {
                min = pos;
            }
        }
        String section = raw.substring(start, min).trim();
        return section.isEmpty() ? raw.trim() : section;
    }
}
