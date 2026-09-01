package com.heritage.kalvettu.dto;

import java.util.List;

public record TempleDetail(
        TempleCard temple, List<ImageDto> images, List<InscriptionCard> inscriptions,
        List<InscriptionLocationDto> locations, DynastyDto dynasty, DistrictDto district) {
}
