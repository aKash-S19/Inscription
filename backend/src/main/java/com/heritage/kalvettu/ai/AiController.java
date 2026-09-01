package com.heritage.kalvettu.ai;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * REST entry points for the AI features:
 *   POST /api/ai/chat        — grounded Q&A over the verified archive
 *   POST /api/ai/translate   — translate + explain a Kalvettu into any language
 *   POST /api/ai/ingest      — extract a structured record from an image/text
 *
 * All endpoints require KALVETTU_AI_GEMINI_KEY to be set; otherwise the Gemini
 * client returns 503.
 */
@RestController
@RequestMapping("/api/ai")
@CrossOrigin(origins = "*")
public class AiController {

    private final AiAssistantService assistant;
    private final AiTranslationService translation;
    private final AiIngestionService ingestion;

    public AiController(AiAssistantService assistant,
                        AiTranslationService translation,
                        AiIngestionService ingestion) {
        this.assistant = assistant;
        this.translation = translation;
        this.ingestion = ingestion;
    }

    @PostMapping("/chat")
    public AiDtos.ChatResponse chat(@RequestBody AiDtos.ChatRequest request) {
        return assistant.chat(request);
    }

    @PostMapping("/translate")
    public AiDtos.TranslateResponse translate(@RequestBody AiDtos.TranslateRequest request) {
        return translation.translate(request);
    }

    @PostMapping("/ingest")
    public AiDtos.IngestResponse ingest(@RequestBody AiDtos.IngestRequest request) {
        return ingestion.ingest(request);
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<String> handleBadRequest(IllegalArgumentException ex) {
        return ResponseEntity.badRequest().body(ex.getMessage());
    }
}