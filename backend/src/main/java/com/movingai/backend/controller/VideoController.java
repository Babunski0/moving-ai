package com.movingai.backend.controller;

import com.movingai.backend.dto.VideoProcessingResponse;
import com.movingai.backend.service.VideoService;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/videos")
public class VideoController {

    private final VideoService videoService;

    public VideoController(VideoService videoService) {
        this.videoService = videoService;
    }

    @PostMapping(
            value = "/analyze",
            consumes = MediaType.MULTIPART_FORM_DATA_VALUE
    )
    public ResponseEntity<VideoProcessingResponse> analyzeVideo(
            @RequestParam("video") MultipartFile video
    ) {

        VideoProcessingResponse response =
                videoService.processVideo(video);

        return ResponseEntity.ok(response);
    }
}