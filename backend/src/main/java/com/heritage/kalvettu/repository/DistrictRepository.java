package com.heritage.kalvettu.repository;

import com.heritage.kalvettu.domain.District;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface DistrictRepository extends JpaRepository<District, Long> {
    Optional<District> findBySlug(String slug);
}
