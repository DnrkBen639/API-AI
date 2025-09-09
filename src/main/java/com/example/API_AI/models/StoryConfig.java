package com.example.API_AI.models;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.time.LocalDateTime;

@Entity
@Table(name = "story_config")
public class StoryConfig {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @NotBlank(message = "First character is required")
    @Column(name = "first_character", nullable = false, columnDefinition = "TEXT")
    private String firstCharacter;
    
    @NotBlank(message = "Second character is required")
    @Column(name = "second_character", nullable = false, columnDefinition = "TEXT")
    private String secondCharacter;
    
    @NotBlank(message = "Background is required")
    @Column(name = "background", nullable = false, columnDefinition = "TEXT")
    private String background;
    
    @NotNull(message = "Genre is required")
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "id_genre", nullable = false, foreignKey = @ForeignKey(name = "fk_story_config_genre"))
    private Genre genre;
    
    @NotNull(message = "Perspective is required")
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "id_perspective", nullable = false, foreignKey = @ForeignKey(name = "fk_story_config_perspective"))
    private Perspective perspective;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    // Constructores
    public StoryConfig() {
        this.createdAt = LocalDateTime.now();
    }
    
    public StoryConfig(String firstCharacter, String secondCharacter, String background, 
                      Genre genre, Perspective perspective) {
        this();
        this.firstCharacter = firstCharacter;
        this.secondCharacter = secondCharacter;
        this.background = background;
        this.genre = genre;
        this.perspective = perspective;
    }
    
    // Getters y Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    
    public String getFirstCharacter() { return firstCharacter; }
    public void setFirstCharacter(String firstCharacter) { this.firstCharacter = firstCharacter; }
    
    public String getSecondCharacter() { return secondCharacter; }
    public void setSecondCharacter(String secondCharacter) { this.secondCharacter = secondCharacter; }
    
    public String getBackground() { return background; }
    public void setBackground(String background) { this.background = background; }
    
    public Genre getGenre() { return genre; }
    public void setGenre(Genre genre) { this.genre = genre; }
    
    public Perspective getPerspective() { return perspective; }
    public void setPerspective(Perspective perspective) { this.perspective = perspective; }
    
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
    
    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }
    
    @PreUpdate
    public void preUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
}