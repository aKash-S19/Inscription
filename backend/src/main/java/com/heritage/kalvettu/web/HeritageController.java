package com.heritage.kalvettu.web;

import com.heritage.kalvettu.dto.*;
import com.heritage.kalvettu.service.HeritageService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*")
public class HeritageController {

    private final HeritageService service;

    public HeritageController(HeritageService service) {
        this.service = service;
    }

    @GetMapping("/temples")
    public List<TempleCard> temples(@RequestParam(required = false) String q,
                                    @RequestParam(required = false) String district,
                                    @RequestParam(required = false) String dynasty) {
        return service.listTemples(q, district, dynasty);
    }

    @GetMapping("/temples/{slug}")
    public TempleDetail temple(@PathVariable String slug) {
        return service.getTemple(slug).orElseThrow(() -> new NotFoundException("Temple not found: " + slug));
    }

    @GetMapping("/inscriptions")
    public List<InscriptionCard> inscriptions(@RequestParam(required = false) String q,
                                              @RequestParam(required = false) String temple,
                                              @RequestParam(required = false) String dynasty,
                                              @RequestParam(required = false) String ruler,
                                              @RequestParam(required = false) String district) {
        return service.listInscriptions(q, temple, dynasty, ruler, district);
    }

    @GetMapping("/inscriptions/{slug}")
    public InscriptionDetail inscription(@PathVariable String slug) {
        return service.getInscription(slug).orElseThrow(() -> new NotFoundException("Inscription not found: " + slug));
    }

    @GetMapping("/dynasties")
    public List<DynastyDto> dynasties() {
        return service.listDynasties();
    }

    @GetMapping("/rulers")
    public List<RulerDto> rulers(@RequestParam(required = false) String dynasty) {
        return service.listRulers(dynasty);
    }

    @GetMapping("/districts")
    public List<DistrictDto> districts() {
        return service.listDistricts();
    }

    @GetMapping("/temples/{slug}/locations")
    public List<InscriptionLocationDto> locations(@PathVariable String slug) {
        return service.locationsForTemple(slug);
    }

    @GetMapping("/timeline")
    public List<TimelineEvent> timeline() {
        return service.timeline();
    }

    @GetMapping("/search")
    public SearchResult search(@RequestParam String q) {
        return new SearchResult(service.listTemples(q, null, null), service.listInscriptions(q, null, null, null, null));
    }

    public record SearchResult(List<TempleCard> temples, List<InscriptionCard> inscriptions) {
    }
}
