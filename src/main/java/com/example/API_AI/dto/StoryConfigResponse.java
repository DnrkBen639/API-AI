package com.example.API_AI.dto;

import java.time.LocalDateTime;

public class StoryConfigResponse {
    
    private Long id;
    private String firstCharacter;
    private String secondCharacter;
    private String background;
    private Long genreId;
    private String genreName;
    private Long perspectiveId;
    private String perspectiveName;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    
    // Getters y Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    
    public String getFirstCharacter() { return firstCharacter; }
    public void setFirstCharacter(String firstCharacter) { this.firstCharacter = firstCharacter; }
    
    public String getSecondCharacter() { return secondCharacter; }
    public void setSecondCharacter(String secondCharacter) { this.secondCharacter = secondCharacter; }
    
    public String getBackground() { return background; }
    public void setBackground(String background) { this.background = background; }
    
    public Long getGenreId() { return genreId; }
    public void setGenreId(Long genreId) { this.genreId = genreId; }
    
    public String getGenreName() { return genreName; }
    public void setGenreName(String genreName) { this.genreName = genreName; }
    
    public Long getPerspectiveId() { return perspectiveId; }
    public void setPerspectiveId(Long perspectiveId) { this.perspectiveId = perspectiveId; }
    
    public String getPerspectiveName() { return perspectiveName; }
    public void setPerspectiveName(String perspectiveName) { this.perspectiveName = perspectiveName; }
    
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
    
    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }
}