package com.movingai.backend.repository;

import com.movingai.backend.model.VideoAnalysis;
import org.springframework.data.jpa.repository.JpaRepository;

public interface VideoAnalysisRepository
        extends JpaRepository<VideoAnalysis, String> {
}