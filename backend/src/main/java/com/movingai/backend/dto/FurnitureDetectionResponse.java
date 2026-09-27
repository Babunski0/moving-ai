package com.movingai.backend.dto;

import java.util.List;
import java.util.Map;

public record FurnitureDetectionResponse(
        int framesProcessed,
        double confidenceThreshold,
        List<DetectedFurnitureItem> items,
        List<FrameDetection> frames
) {

    public record DetectedFurnitureItem(
            String name,
            int quantity
    ) {
    }

    public record FrameDetection(
            String frame,
            Map<String, Integer> detections
    ) {
    }
}