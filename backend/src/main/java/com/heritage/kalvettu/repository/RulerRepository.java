package com.heritage.kalvettu.repository;

import com.heritage.kalvettu.domain.Ruler;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface RulerRepository extends JpaRepository<Ruler, Long> {
    Optional<Ruler> findBySlug(String slug);
    List<Ruler> findByDynastySlug(String dynastySlug);
}
