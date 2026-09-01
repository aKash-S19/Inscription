package com.heritage.kalvettu.repository;

import com.heritage.kalvettu.domain.InscriptionLocation;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface InscriptionLocationRepository extends JpaRepository<InscriptionLocation, Long> {
    List<InscriptionLocation> findByTempleSlug(String templeSlug);
    Optional<InscriptionLocation> findByInscriptionSlug(String inscriptionSlug);
}
