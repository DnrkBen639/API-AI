package com.example.API_AI.models;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

@Entity
@Table(name = "perspectives")
public class Perspective {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @NotBlank(message = "La descripción es requerida")
    @Size(max = 45, message = "La descripción no puede exceder 45 caracteres")
    @Column(name = "description", nullable = false, length = 45)
    private String description;
    
    // Constructores
    public Perspective() {}
    
    public Perspective(String description) {
        this.description = description;
    }
    
    // Getters y Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    
    // Para compatibilidad con tu código existente
    public String getName() { return description; }
    public void setName(String name) { this.description = name; }
}