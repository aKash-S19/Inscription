package com.heritage.kalvettu.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/**
 * Configuration for the Google Gemini AI integration.
 *
 * All values are externalised via environment variables / properties so the
 * API key never lives in source control:
 *   KALVETTU_AI_GEMINI_KEY    (required to enable AI features)
 *   KALVETTU_AI_GEMINI_MODEL  (defaults to gemini-2.0-flash)
 *   KALVETTU_AI_ENABLED        (defaults to true; set false to disable)
 */
@Component
@ConfigurationProperties(prefix = "kalvettu.ai")
public class AiProperties {

    /** Master switch for all AI endpoints. */
    private boolean enabled = true;

    /** Google Gemini API key. Leave blank/absent to keep AI disabled. */
    private String geminiKey = "";

    /** Gemini model id used for text + vision calls. */
    private String geminiModel = "gemini-3.6-flash";

    /** Base URL of the Gemini generateContent endpoint (key placeholder). */
    private String geminiUrl = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent";

    /** Optional system/grounding instructions prepended to AI prompts. */
    private String systemPrompt = "";

    public boolean isEnabled() {
        return enabled;
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public String getGeminiKey() {
        return geminiKey;
    }

    public void setGeminiKey(String geminiKey) {
        this.geminiKey = geminiKey;
    }

    public String getGeminiModel() {
        return geminiModel;
    }

    public void setGeminiModel(String geminiModel) {
        this.geminiModel = geminiModel;
    }

    public String getGeminiUrl() {
        return geminiUrl;
    }

    public void setGeminiUrl(String geminiUrl) {
        this.geminiUrl = geminiUrl;
    }

    public String getSystemPrompt() {
        return systemPrompt;
    }

    public void setSystemPrompt(String systemPrompt) {
        this.systemPrompt = systemPrompt;
    }
}
