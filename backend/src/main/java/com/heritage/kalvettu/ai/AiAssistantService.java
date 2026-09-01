package com.heritage.kalvettu.ai;

import com.heritage.kalvettu.domain.Inscription;
import com.heritage.kalvettu.domain.Temple;
import com.heritage.kalvettu.repository.InscriptionRepository;
import com.heritage.kalvettu.repository.TempleRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

/**
 * Grounded chat assistant ("retrieval-augmented generation" over the verified
 * dataset). On every question it retrieves the most relevant temples and
 * inscriptions from the verified archive, embeds them in the prompt, and asks
 * Gemini to answer strictly from that context. This keeps answers accurate and
 * prevents the model from inventing inscriptions, dates or sources.
 */
@Service
public class AiAssistantService {

    private final GeminiClient gemini;
    private final TempleRepository templeRepository;
    private final InscriptionRepository inscriptionRepository;

    public AiAssistantService(GeminiClient gemini,
                              TempleRepository templeRepository,
                              InscriptionRepository inscriptionRepository) {
        this.gemini = gemini;
        this.templeRepository = templeRepository;
        this.inscriptionRepository = inscriptionRepository;
    }

    public AiDtos.ChatResponse chat(AiDtos.ChatRequest request) {
        String context = buildContext();
        String history = formatHistory(request.messages());
        String language = (request.language() == null || request.language().isBlank())
                ? "English" : request.language();

        String prompt = """
                VERIFIED ARCHIVE CONTEXT (the only facts you may use):
                %s

                CONVERSATION SO FAR:
                %s

                TASK: Answer the user's latest message.
                - Answer ONLY from the VERIFIED ARCHIVE CONTEXT above.
                - If the context does not contain the answer, say so clearly instead of guessing.
                - Never invent inscriptions, rulers, dates, temples, translations or sources.
                - Answer in the language: %s
                """.formatted(context, history, language);

        String answer = gemini.complete(prompt);
        return new AiDtos.ChatResponse(answer, language);
    }

    private String buildContext() {
        StringBuilder sb = new StringBuilder();

        sb.append("[TEMPLES]\n");
        for (Temple t : templeRepository.findAll()) {
            sb.append("- ").append(t.getNameEn())
                    .append(" (slug: ").append(t.getSlug())
                    .append(", town: ").append(t.getTown())
                    .append(", dynasty: ").append(t.getDynastySlug())
                    .append(", deity: ").append(t.getDeity());
            if (t.getSummary() != null) {
                sb.append(", summary: ").append(t.getSummary());
            }
            sb.append(")\n");
        }

        sb.append("\n[INSCRIPTIONS]\n");
        for (Inscription i : inscriptionRepository.findAll()) {
            sb.append("- ").append(i.getTitle())
                    .append(" (slug: ").append(i.getSlug())
                    .append(", temple: ").append(i.getTempleSlug())
                    .append(", ruler: ").append(i.getRulerSlug())
                    .append(", dynasty: ").append(i.getDynastySlug())
                    .append(", reference: ").append(i.getReferenceId());
            if (i.getTranslation() != null && !i.getTranslation().isBlank()) {
                sb.append(", translation: ").append(abbrev(i.getTranslation(), 600));
            }
            if (i.getSimpleExplanation() != null && !i.getSimpleExplanation().isBlank()) {
                sb.append(", simple explanation: ").append(abbrev(i.getSimpleExplanation(), 400));
            }
            if (i.getHistoricalSignificance() != null && !i.getHistoricalSignificance().isBlank()) {
                sb.append(", significance: ").append(abbrev(i.getHistoricalSignificance(), 300));
            }
            sb.append(")\n");
        }

        return sb.toString();
    }

    private String formatHistory(List<AiDtos.ChatMessage> messages) {
        if (messages == null || messages.isEmpty()) {
            return "[no prior messages]";
        }
        return messages.stream()
                .map(m -> m.role() + ": " + m.content())
                .collect(Collectors.joining("\n"));
    }

    private String abbrev(String s, int max) {
        if (s == null) {
            return "";
        }
        return s.length() <= max ? s : s.substring(0, max) + "…";
    }
}
