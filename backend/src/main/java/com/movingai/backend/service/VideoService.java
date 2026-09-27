package com.movingai.backend.service;

import com.movingai.backend.dto.FurnitureDetectionResponse;
import com.movingai.backend.dto.FurnitureItemResponse;
import com.movingai.backend.dto.VideoProcessingResponse;
import com.movingai.backend.model.AnalysisStatus;
import com.movingai.backend.model.FurnitureItem;
import com.movingai.backend.model.VideoAnalysis;
import com.movingai.backend.repository.FurnitureItemRepository;
import com.movingai.backend.repository.VideoAnalysisRepository;

import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.time.Instant;
import java.util.List;
import java.util.Locale;
import java.util.UUID;
import java.util.stream.Stream;

@Service
public class VideoService {

    private final FfmpegService ffmpegService;

    private final FurnitureDetectionService
            furnitureDetectionService;

    private final VideoAnalysisRepository
            videoAnalysisRepository;

    private final FurnitureItemRepository
            furnitureItemRepository;

    public VideoService(
            FfmpegService ffmpegService,
            FurnitureDetectionService furnitureDetectionService,
            VideoAnalysisRepository videoAnalysisRepository,
            FurnitureItemRepository furnitureItemRepository
    ) {
        this.ffmpegService = ffmpegService;
        this.furnitureDetectionService =
                furnitureDetectionService;

        this.videoAnalysisRepository =
                videoAnalysisRepository;

        this.furnitureItemRepository =
                furnitureItemRepository;
    }

    public VideoProcessingResponse processVideo(
            MultipartFile video
    ) {

        validateVideo(video);

        String analysisId =
                UUID.randomUUID().toString();

        VideoAnalysis analysis =
                new VideoAnalysis();

        analysis.setId(analysisId);

        analysis.setOriginalFileName(
                video.getOriginalFilename()
        );

        analysis.setStatus(
                AnalysisStatus.PROCESSING
        );

        analysis.setCreatedAt(
                Instant.now()
        );

        analysis.setUpdatedAt(
                Instant.now()
        );

        videoAnalysisRepository.save(
                analysis
        );

        Path storageRoot =
                Path.of("storage")
                        .toAbsolutePath()
                        .normalize();

        Path uploadDirectory =
                storageRoot
                        .resolve("uploads")
                        .resolve(analysisId);

        Path processedDirectory =
                storageRoot
                        .resolve("processed")
                        .resolve(analysisId);

        Path framesDirectory =
                processedDirectory
                        .resolve("frames");

        Path savedVideo =
                uploadDirectory
                        .resolve("input.mp4");

        try {

            Files.createDirectories(
                    uploadDirectory
            );

            Files.createDirectories(
                    framesDirectory
            );

            Files.copy(
                    video.getInputStream(),
                    savedVideo,
                    StandardCopyOption.REPLACE_EXISTING
            );

            /*
             * ZA SADA:
             * nema audija
             * nema transcriptiona
             *
             * Samo video -> frames.
             */

            ffmpegService.extractFrames(
                    savedVideo,
                    framesDirectory
            );

            long frameCount;

            try (
                    Stream<Path> files =
                            Files.list(
                                    framesDirectory
                            )
            ) {

                frameCount = files
                        .filter(
                                Files::isRegularFile
                        )
                        .filter(
                                path ->
                                        path
                                                .getFileName()
                                                .toString()
                                                .toLowerCase(
                                                        Locale.ROOT
                                                )
                                                .endsWith(".jpg")
                        )
                        .count();
            }

            analysis.setSavedVideo(
                    savedVideo.toString()
            );

            analysis.setFramesDirectory(
                    framesDirectory.toString()
            );

            analysis.setFrameCount(
                    frameCount
            );

            analysis.setStatus(
                    AnalysisStatus.PROCESSED
            );

            analysis.setUpdatedAt(
                    Instant.now()
            );

            videoAnalysisRepository.save(
                    analysis
            );

            /*
             * LOCAL VISION
             */

            analysis.setStatus(
                    AnalysisStatus.AI_PROCESSING
            );

            analysis.setUpdatedAt(
                    Instant.now()
            );

            videoAnalysisRepository.save(
                    analysis
            );

            FurnitureDetectionResponse detection =
                    furnitureDetectionService.detect(
                            framesDirectory
                    );

            /*
             * Save detected furniture in PostgreSQL
             */

            List<FurnitureItem> furnitureEntities =
                    detection.items()
                            .stream()
                            .map(item -> {

                                FurnitureItem furniture =
                                        new FurnitureItem();

                                furniture.setName(
                                        item.name()
                                );

                                furniture.setQuantity(
                                        item.quantity()
                                );

                                furniture.setExcluded(
                                        false
                                );

                                furniture.setVideoAnalysis(
                                        analysis
                                );

                                return furniture;

                            })
                            .toList();

            furnitureItemRepository.saveAll(
                    furnitureEntities
            );

            analysis.setStatus(
                    AnalysisStatus.COMPLETED
            );

            analysis.setUpdatedAt(
                    Instant.now()
            );

            videoAnalysisRepository.save(
                    analysis
            );

            List<FurnitureItemResponse> furniture =
                    detection.items()
                            .stream()
                            .map(
                                    item ->
                                            new FurnitureItemResponse(
                                                    item.name(),
                                                    item.quantity()
                                            )
                            )
                            .toList();

            return new VideoProcessingResponse(
                    analysisId,
                    video.getOriginalFilename(),
                    frameCount,
                    furniture,
                    "COMPLETED"
            );

        } catch (Exception e) {

            analysis.setStatus(
                    AnalysisStatus.FAILED
            );

            analysis.setUpdatedAt(
                    Instant.now()
            );

            videoAnalysisRepository.save(
                    analysis
            );

            if (
                    e instanceof RuntimeException
                            runtimeException
            ) {

                throw runtimeException;
            }

            throw new RuntimeException(
                    "Failed to process uploaded video.",
                    e
            );
        }
    }

    private void validateVideo(
            MultipartFile video
    ) {

        if (
                video == null ||
                        video.isEmpty()
        ) {

            throw new IllegalArgumentException(
                    "Video file is required."
            );
        }

        String filename =
                video.getOriginalFilename();

        if (
                filename == null ||
                        !filename
                                .toLowerCase(
                                        Locale.ROOT
                                )
                                .endsWith(".mp4")
        ) {

            throw new IllegalArgumentException(
                    "Only MP4 videos are currently supported."
            );
        }
    }
}