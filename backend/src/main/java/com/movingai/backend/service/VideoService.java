package com.movingai.backend.service;

import com.movingai.backend.dto.VideoProcessingResponse;
import com.movingai.backend.model.AnalysisStatus;
import com.movingai.backend.model.VideoAnalysis;
import com.movingai.backend.repository.VideoAnalysisRepository;

import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.time.Instant;
import java.util.Locale;
import java.util.UUID;
import java.util.stream.Stream;

@Service
public class VideoService {

    private final FfmpegService ffmpegService;
    private final VideoAnalysisRepository videoAnalysisRepository;

    public VideoService(
            FfmpegService ffmpegService,
            VideoAnalysisRepository videoAnalysisRepository
    ) {
        this.ffmpegService = ffmpegService;
        this.videoAnalysisRepository = videoAnalysisRepository;
    }

    public VideoProcessingResponse processVideo(MultipartFile video) {

        validateVideo(video);

        String analysisId = UUID.randomUUID().toString();

        VideoAnalysis analysis = new VideoAnalysis();

        analysis.setId(analysisId);
        analysis.setOriginalFileName(video.getOriginalFilename());
        analysis.setStatus(AnalysisStatus.PROCESSING);
        analysis.setCreatedAt(Instant.now());
        analysis.setUpdatedAt(Instant.now());

        videoAnalysisRepository.save(analysis);

        Path storageRoot = Path.of("storage")
                .toAbsolutePath()
                .normalize();

        Path uploadDirectory = storageRoot
                .resolve("uploads")
                .resolve(analysisId);

        Path processedDirectory = storageRoot
                .resolve("processed")
                .resolve(analysisId);

        Path audioDirectory =
                processedDirectory.resolve("audio");

        Path framesDirectory =
                processedDirectory.resolve("frames");

        Path savedVideo =
                uploadDirectory.resolve("input.mp4");

        Path audioFile =
                audioDirectory.resolve("audio.wav");

        try {

            Files.createDirectories(uploadDirectory);
            Files.createDirectories(audioDirectory);
            Files.createDirectories(framesDirectory);

            Files.copy(
                    video.getInputStream(),
                    savedVideo,
                    StandardCopyOption.REPLACE_EXISTING
            );

            ffmpegService.extractAudio(
                    savedVideo,
                    audioFile
            );

            ffmpegService.extractFrames(
                    savedVideo,
                    framesDirectory
            );

            long frameCount;

            try (Stream<Path> files = Files.list(framesDirectory)) {

                frameCount = files
                        .filter(Files::isRegularFile)
                        .filter(path ->
                                path.getFileName()
                                        .toString()
                                        .toLowerCase()
                                        .endsWith(".jpg")
                        )
                        .count();
            }

            analysis.setSavedVideo(savedVideo.toString());
            analysis.setAudioFile(audioFile.toString());
            analysis.setFramesDirectory(framesDirectory.toString());
            analysis.setFrameCount(frameCount);
            analysis.setStatus(AnalysisStatus.PROCESSED);
            analysis.setUpdatedAt(Instant.now());

            videoAnalysisRepository.save(analysis);

            return new VideoProcessingResponse(
                    analysisId,
                    video.getOriginalFilename(),
                    savedVideo.toString(),
                    audioFile.toString(),
                    framesDirectory.toString(),
                    frameCount,
                    "PROCESSED"
            );

        } catch (Exception e) {

            analysis.setStatus(AnalysisStatus.FAILED);
            analysis.setUpdatedAt(Instant.now());

            videoAnalysisRepository.save(analysis);

            if (e instanceof RuntimeException runtimeException) {
                throw runtimeException;
            }

            throw new RuntimeException(
                    "Failed to process uploaded video.",
                    e
            );
        }
    }

    private void validateVideo(MultipartFile video) {

        if (video == null || video.isEmpty()) {
            throw new IllegalArgumentException(
                    "Video file is required."
            );
        }

        String filename = video.getOriginalFilename();

        if (filename == null ||
                !filename
                        .toLowerCase(Locale.ROOT)
                        .endsWith(".mp4")) {

            throw new IllegalArgumentException(
                    "Only MP4 videos are currently supported."
            );
        }
    }
}