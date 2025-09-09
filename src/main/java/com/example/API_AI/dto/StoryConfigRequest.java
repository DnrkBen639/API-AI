package com.example.API_AI.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public class StoryConfigRequest {
    
    @NotBlank(message = "El primer personaje es requerido")
    private String firstCharacter;
    
    @NotBlank(message = "El segundo personaje es requerido")
    private String secondCharacter;
    
    @NotBlank(message = "El fondo es requerido")
    private String background;
    
    @NotNull(message = "El género es requerido")
    private Long genreId;
    
    @NotNull(message = "La perspectiva es requerida")
    private Long perspectiveId;

    // Getters y Setters
    public String getFirstCharacter() { return firstCharacter; }
    public void setFirstCharacter(String firstCharacter) { this.firstCharacter = firstCharacter; }
    
    public String getSecondCharacter() { return secondCharacter; }
    public void setSecondCharacter(String secondCharacter) { this.secondCharacter = secondCharacter; }
    
    public String getBackground() { return background; }
    public void setBackground(String background) { this.background = background; }
    
    public Long getGenreId() { return genreId; }
    public void setGenreId(Long genreId) { this.genreId = genreId; }
    
    public Long getPerspectiveId() { return perspectiveId; }
    public void setPerspectiveId(Long perspectiveId) { this.perspectiveId = perspectiveId; }
}