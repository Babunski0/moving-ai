package com.movingai.backend.dto;

import java.util.List;

public record VideoProcessingResponse(
        String analysisId,
        String originalFileName,
        long frameCount,
        List<FurnitureItemResponse> furniture,
        String status
) {
}