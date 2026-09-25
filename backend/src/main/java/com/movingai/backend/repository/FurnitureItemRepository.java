package com.movingai.backend.repository;

import com.movingai.backend.model.FurnitureItem;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface FurnitureItemRepository
        extends JpaRepository<FurnitureItem, Long> {

    List<FurnitureItem> findByVideoAnalysisId(String videoAnalysisId);
}