package com.heritage.kalvettu.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.web.client.RestClient;

/**
 * Base HTTP client used by the Gemini AI client. Centralises the shared
 * JSON content type so callers do not need to repeat it.
 */
@Configuration
public class AiConfig {

    @Bean(name = "geminiRestClient")
    public RestClient geminiRestClient() {
        return RestClient.builder()
                .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                .defaultHeader(HttpHeaders.ACCEPT, MediaType.APPLICATION_JSON_VALUE)
                .build();
    }
}
