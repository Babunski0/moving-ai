package com.movingai.backend.dto;

public record VideoProcessingResponse(
        String analysisId,
        String originalFileName,
        String savedVideo,
        String audioFile,
        String framesDirectory,
        long frameCount,
        String status
) {
}