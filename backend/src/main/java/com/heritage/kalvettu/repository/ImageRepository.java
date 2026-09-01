package com.heritage.kalvettu.repository;

import com.heritage.kalvettu.domain.Image;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface ImageRepository extends JpaRepository<Image, Long> {

    List<Image> findByEntityTypeAndEntitySlug(String entityType, String entitySlug);

    @Query("SELECT i FROM Image i WHERE i.entityType = :type AND i.entitySlug = :slug ORDER BY " +
            "CASE i.category WHEN 'exterior' THEN 1 WHEN 'plan' THEN 2 ELSE 3 END")
    List<Image> findByEntity(@Param("type") String type, @Param("slug") String slug);
}
