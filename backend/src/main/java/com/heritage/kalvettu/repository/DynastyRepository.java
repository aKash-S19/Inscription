package com.heritage.kalvettu.repository;

import com.heritage.kalvettu.domain.Dynasty;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface DynastyRepository extends JpaRepository<Dynasty, Long> {
    Optional<Dynasty> findBySlug(String slug);
}
