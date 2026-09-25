package com.movingai.backend.model;

import jakarta.persistence.*;

@Entity
@Table(name = "furniture_items")
public class FurnitureItem {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    private Integer quantity;

    private String room;

    private Boolean excluded;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "video_analysis_id", nullable = false)
    private VideoAnalysis videoAnalysis;

    public FurnitureItem() {
    }

    public Long getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Integer getQuantity() {
        return quantity;
    }

    public void setQuantity(Integer quantity) {
        this.quantity = quantity;
    }

    public String getRoom() {
        return room;
    }

    public void setRoom(String room) {
        this.room = room;
    }

    public Boolean getExcluded() {
        return excluded;
    }

    public void setExcluded(Boolean excluded) {
        this.excluded = excluded;
    }

    public VideoAnalysis getVideoAnalysis() {
        return videoAnalysis;
    }

    public void setVideoAnalysis(VideoAnalysis videoAnalysis) {
        this.videoAnalysis = videoAnalysis;
    }
}