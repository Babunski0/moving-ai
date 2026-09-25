package com.movingai.backend.model;

import jakarta.persistence.*;

import java.time.Instant;

@Entity
@Table(name = "video_analyses")
public class VideoAnalysis {

    @Id
    private String id;

    @Column(nullable = false)
    private String originalFileName;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private AnalysisStatus status;

    private String savedVideo;

    private String audioFile;

    private String framesDirectory;

    private Long frameCount;

    @Column(nullable = false)
    private Instant createdAt;

    @Column(nullable = false)
    private Instant updatedAt;

    public VideoAnalysis() {
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getOriginalFileName() {
        return originalFileName;
    }

    public void setOriginalFileName(String originalFileName) {
        this.originalFileName = originalFileName;
    }

    public AnalysisStatus getStatus() {
        return status;
    }

    public void setStatus(AnalysisStatus status) {
        this.status = status;
    }

    public String getSavedVideo() {
        return savedVideo;
    }

    public void setSavedVideo(String savedVideo) {
        this.savedVideo = savedVideo;
    }

    public String getAudioFile() {
        return audioFile;
    }

    public void setAudioFile(String audioFile) {
        this.audioFile = audioFile;
    }

    public String getFramesDirectory() {
        return framesDirectory;
    }

    public void setFramesDirectory(String framesDirectory) {
        this.framesDirectory = framesDirectory;
    }

    public Long getFrameCount() {
        return frameCount;
    }

    public void setFrameCount(Long frameCount) {
        this.frameCount = frameCount;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Instant createdAt) {
        this.createdAt = createdAt;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(Instant updatedAt) {
        this.updatedAt = updatedAt;
    }
}