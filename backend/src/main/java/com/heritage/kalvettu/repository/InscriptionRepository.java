package com.heritage.kalvettu.repository;

import com.heritage.kalvettu.domain.Inscription;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

public interface InscriptionRepository extends JpaRepository<Inscription, Long>, JpaSpecificationExecutor<Inscription> {

    Optional<Inscription> findBySlug(String slug);

    List<Inscription> findByTempleSlug(String templeSlug);

    List<Inscription> findByDynastySlug(String dynastySlug);

    List<Inscription> findByRulerSlug(String rulerSlug);

    @Query("SELECT i FROM Inscription i WHERE " +
            "(:q IS NULL OR LOWER(i.title) LIKE LOWER(CONCAT('%',:q,'%')) " +
            "OR LOWER(COALESCE(i.translation,'')) LIKE LOWER(CONCAT('%',:q,'%')) " +
            "OR LOWER(COALESCE(i.simpleExplanation,'')) LIKE LOWER(CONCAT('%',:q,'%')) " +
            "OR LOWER(COALESCE(i.siiReference,'')) LIKE LOWER(CONCAT('%',:q,'%')) " +
            "OR LOWER(COALESCE(i.areNumber,'')) LIKE LOWER(CONCAT('%',:q,'%')) " +
            "OR LOWER(COALESCE(i.physicalLocation,'')) LIKE LOWER(CONCAT('%',:q,'%')))")
    List<Inscription> search(@Param("q") String q);
}
