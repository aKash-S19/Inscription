package com.heritage.kalvettu.repository;

import com.heritage.kalvettu.domain.Temple;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

public interface TempleRepository extends JpaRepository<Temple, Long>, JpaSpecificationExecutor<Temple> {

    Optional<Temple> findBySlug(String slug);

    List<Temple> findByDistrictSlug(String districtSlug);

    List<Temple> findByDynastySlug(String dynastySlug);

    @Query("SELECT t FROM Temple t WHERE " +
            "(:q IS NULL OR LOWER(t.nameEn) LIKE LOWER(CONCAT('%',:q,'%')) " +
            "OR LOWER(COALESCE(t.nameTa,'')) LIKE LOWER(CONCAT('%',:q,'%')) " +
            "OR LOWER(COALESCE(t.deity,'')) LIKE LOWER(CONCAT('%',:q,'%')) " +
            "OR LOWER(COALESCE(t.town,'')) LIKE LOWER(CONCAT('%',:q,'%')) " +
            "OR LOWER(COALESCE(t.alternateNames,'')) LIKE LOWER(CONCAT('%',:q,'%')))")
    List<Temple> search(@Param("q") String q);
}
