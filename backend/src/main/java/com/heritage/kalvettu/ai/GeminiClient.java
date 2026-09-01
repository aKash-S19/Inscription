package com.heritage.kalvettu.ai;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.heritage.kalvettu.config.AiProperties;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.Map;

/**
 * Thin, dependency-light client for the Google Gemini REST API.
 *
 * Only the "generateContent" endpoint is used; it supports both plain text
 * prompts and multimodal (text + inline image) prompts, which covers the
 * chat, translation and image-based ingestion features.
 */
@Component
public class GeminiClient {

    private static final Logger log = LoggerFactory.getLogger(GeminiClient.class);

    private final RestClient restClient;
    private final AiProperties props;
    private final ObjectMapper mapper = new ObjectMapper();

    public GeminiClient(RestClient geminiRestClient, AiProperties props) {
        this.restClient = geminiRestClient;
        this.props = props;
    }

    /** Simple text in -> text out. */
    public String complete(String prompt) {
        return generate(prompt, null);
    }

    /** Text + inline image (base64, no data-URI prefix) -> text out. */
    public String completeWithImage(String prompt, String base64Image, String mimeType) {
        return generate(prompt, new InlineImage(base64Image, mimeType));
    }

    private record InlineImage(String data, String mimeType) {
    }

    private String generate(String prompt, InlineImage image) {
        String key = props.getGeminiKey();
        if (!props.isEnabled() || key == null || key.isBlank()) {
            throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE,
                    "AI is not configured. Set KALVETTU_AI_GEMINI_KEY and restart.");
        }

        ObjectNode request = mapper.createObjectNode();

        // Gemini system instruction (grounding behaviour/accuracy policy).
        if (props.getSystemPrompt() != null && !props.getSystemPrompt().isBlank()) {
            ObjectNode si = mapper.createObjectNode();
            ObjectNode siText = mapper.createObjectNode();
            siText.put("text", props.getSystemPrompt());
            si.set("parts", mapper.createArrayNode().add(siText));
            si.put("role", "system_instruction");
            request.set("systemInstruction", si);
        }

        // Build the single user turn with optional inline image.
        ArrayNode contents = mapper.createArrayNode();
        ObjectNode content = mapper.createObjectNode();
        ArrayNode parts = mapper.createArrayNode();

        ObjectNode textPart = mapper.createObjectNode();
        textPart.put("text", prompt);
        parts.add(textPart);

        if (image != null) {
            ObjectNode imagePart = mapper.createObjectNode();
            ObjectNode inlineData = mapper.createObjectNode();
            inlineData.put("mimeType", image.mimeType());
            inlineData.put("data", image.data());
            imagePart.set("inlineData", inlineData);
            parts.add(imagePart);
        }

        content.put("role", "user");
        content.set("parts", parts);
        contents.add(content);
        request.set("contents", contents);

        // Disable moderately creative sampling for factual grounding.
        ObjectNode generationConfig = mapper.createObjectNode();
        generationConfig.put("temperature", 0.2);
        generationConfig.put("maxOutputTokens", 4096);
        request.set("generationConfig", generationConfig);

        try {
            String url = props.getGeminiUrl().replace("{model}", props.getGeminiModel());
            JsonNode body = restClient.post()
                    .uri(url)
                    .header("x-goog-api-key", key)
                    .body(request)
                    .retrieve()
                    .body(JsonNode.class);

            if (body == null) {
                throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "Empty response from Gemini.");
            }

            // Extract the first text part from candidates[0].content.parts[].
            JsonNode candidates = body.path("candidates");
            if (candidates.isArray() && candidates.size() > 0) {
                JsonNode partsNode = candidates.get(0).path("content").path("parts");
                if (partsNode.isArray()) {
                    StringBuilder sb = new StringBuilder();
                    for (JsonNode part : partsNode) {
                        if (part.hasNonNull("text")) {
                            sb.append(part.get("text").asText());
                        }
                    }
                    if (sb.length() > 0) {
                        return sb.toString().trim();
                    }
                }
            }

            // Surface a meaningful Gemini error if present.
            JsonNode err = body.path("error");
            if (err.isObject()) {
                throw new ResponseStatusException(HttpStatus.BAD_GATEWAY,
                        "Gemini error: " + err.path("message").asText(err.path("status").asText("unknown")));
            }
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "Gemini returned no text content.");
        } catch (ResponseStatusException e) {
            throw e;
        } catch (Exception e) {
            log.error("Gemini call failed", e);
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "Gemini call failed: " + e.getMessage());
        }
    }
}
