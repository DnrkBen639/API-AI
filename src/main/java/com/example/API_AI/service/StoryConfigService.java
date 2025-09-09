package com.example.API_AI.service;

import com.example.API_AI.dto.StoryConfigRequest;
import com.example.API_AI.dto.StoryConfigResponse;
import com.example.API_AI.models.Genre;
import com.example.API_AI.models.Perspective;
import com.example.API_AI.models.StoryConfig;
import com.example.API_AI.repository.StoryConfigRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
@Transactional
public class StoryConfigService {
    
    @Autowired
    private StoryConfigRepository storyConfigRepository;
    
    @Autowired
    private GenreService genreService;
    
    @Autowired
    private PerspectiveService perspectiveService; 
    
    private StoryConfigResponse convertToResponse(StoryConfig storyConfig) {
        StoryConfigResponse response = new StoryConfigResponse();
        response.setId(storyConfig.getId());
        response.setFirstCharacter(storyConfig.getFirstCharacter());
        response.setSecondCharacter(storyConfig.getSecondCharacter());
        response.setBackground(storyConfig.getBackground());
        response.setGenreId(storyConfig.getGenre().getId());
        response.setGenreName(storyConfig.getGenre().getName());
        response.setPerspectiveId(storyConfig.getPerspective().getId());
        response.setPerspectiveName(storyConfig.getPerspective().getName());
        response.setCreatedAt(storyConfig.getCreatedAt());
        response.setUpdatedAt(storyConfig.getUpdatedAt());
        return response;
    }
    
    public List<StoryConfigResponse> getAll() {
        return storyConfigRepository.findAll().stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }
    
    public Optional<StoryConfigResponse> getById(Long id) {
        return storyConfigRepository.findById(id)
                .map(this::convertToResponse);
    }
    
    public StoryConfigResponse create(StoryConfigRequest request) {
        // Verificar que existan las entidades relacionadas usando los servicios
        Genre genre = genreService.getById(request.getGenreId())
                .orElseThrow(() -> new RuntimeException("Género no encontrado con id: " + request.getGenreId()));
        
        Perspective perspective = perspectiveService.getById(request.getPerspectiveId())
                .orElseThrow(() -> new RuntimeException("Perspectiva no encontrada con id: " + request.getPerspectiveId()));
        
        StoryConfig storyConfig = new StoryConfig();
        storyConfig.setFirstCharacter(request.getFirstCharacter());
        storyConfig.setSecondCharacter(request.getSecondCharacter());
        storyConfig.setBackground(request.getBackground());
        storyConfig.setGenre(genre);
        storyConfig.setPerspective(perspective);
        
        StoryConfig saved = storyConfigRepository.save(storyConfig);
        return convertToResponse(saved);
    }
    
    public Optional<StoryConfigResponse> update(Long id, StoryConfigRequest request) {
        return storyConfigRepository.findById(id)
                .map(storyConfig -> {
                    if (request.getGenreId() != null) {
                        Genre genre = genreService.getById(request.getGenreId())
                                .orElseThrow(() -> new RuntimeException("Género no encontrado"));
                        storyConfig.setGenre(genre);
                    }
                    
                    if (request.getPerspectiveId() != null) {
                        Perspective perspective = perspectiveService.getById(request.getPerspectiveId())
                                .orElseThrow(() -> new RuntimeException("Perspectiva no encontrada"));
                        storyConfig.setPerspective(perspective);
                    }
                    
                    if (request.getFirstCharacter() != null) {
                        storyConfig.setFirstCharacter(request.getFirstCharacter());
                    }
                    
                    if (request.getSecondCharacter() != null) {
                        storyConfig.setSecondCharacter(request.getSecondCharacter());
                    }
                    
                    if (request.getBackground() != null) {
                        storyConfig.setBackground(request.getBackground());
                    }
                    
                    StoryConfig updated = storyConfigRepository.save(storyConfig);
                    return convertToResponse(updated);
                });
    }
    
    public boolean delete(Long id) {
        if (storyConfigRepository.existsById(id)) {
            storyConfigRepository.deleteById(id);
            return true;
        }
        return false;
    }
    
    public List<StoryConfigResponse> getByGenre(Long genreId) {
        return storyConfigRepository.findByGenreId(genreId).stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }
    
    public List<StoryConfigResponse> getByPerspective(Long perspectiveId) {
        return storyConfigRepository.findByPerspectiveId(perspectiveId).stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }
    
    public List<StoryConfigResponse> searchByCharacter(String characterName) {
        return storyConfigRepository.findByCharacterName(characterName).stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }

    // Método adicional para crear desde entidad (útil para el controlador web)
    public StoryConfigResponse createFromEntity(StoryConfig storyConfig) {
        // Validar que los objetos relacionados existan
        if (storyConfig.getGenre() != null && storyConfig.getGenre().getId() != null) {
            Genre genre = genreService.getById(storyConfig.getGenre().getId())
                    .orElseThrow(() -> new RuntimeException("Género no encontrado"));
            storyConfig.setGenre(genre);
        }
        
        if (storyConfig.getPerspective() != null && storyConfig.getPerspective().getId() != null) {
            Perspective perspective = perspectiveService.getById(storyConfig.getPerspective().getId())
                    .orElseThrow(() -> new RuntimeException("Perspectiva no encontrada"));
            storyConfig.setPerspective(perspective);
        }
        
        StoryConfig saved = storyConfigRepository.save(storyConfig);
        return convertToResponse(saved);
    }

    // Método para obtener la entidad completa (útil para el controlador web)
    public Optional<StoryConfig> getEntityById(Long id) {
        return storyConfigRepository.findById(id);
    }

    // Método para actualizar desde entidad (útil para el controlador web)
    public Optional<StoryConfigResponse> updateFromEntity(Long id, StoryConfig storyConfigDetails) {
        return storyConfigRepository.findById(id)
                .map(storyConfig -> {
                    if (storyConfigDetails.getGenre() != null && storyConfigDetails.getGenre().getId() != null) {
                        Genre genre = genreService.getById(storyConfigDetails.getGenre().getId())
                                .orElseThrow(() -> new RuntimeException("Género no encontrado"));
                        storyConfig.setGenre(genre);
                    }
                    
                    if (storyConfigDetails.getPerspective() != null && storyConfigDetails.getPerspective().getId() != null) {
                        Perspective perspective = perspectiveService.getById(storyConfigDetails.getPerspective().getId())
                                .orElseThrow(() -> new RuntimeException("Perspectiva no encontrada"));
                        storyConfig.setPerspective(perspective);
                    }
                    
                    if (storyConfigDetails.getFirstCharacter() != null) {
                        storyConfig.setFirstCharacter(storyConfigDetails.getFirstCharacter());
                    }
                    
                    if (storyConfigDetails.getSecondCharacter() != null) {
                        storyConfig.setSecondCharacter(storyConfigDetails.getSecondCharacter());
                    }
                    
                    if (storyConfigDetails.getBackground() != null) {
                        storyConfig.setBackground(storyConfigDetails.getBackground());
                    }
                    
                    StoryConfig updated = storyConfigRepository.save(storyConfig);
                    return convertToResponse(updated);
                });
    }
}