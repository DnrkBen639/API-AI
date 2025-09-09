package com.example.API_AI.service;

import com.example.API_AI.models.Perspective;
import com.example.API_AI.repository.PerspectiveRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class PerspectiveService {
    
    @Autowired
    private PerspectiveRepository perspectiveRepository;
    
    public List<Perspective> getAll() {
        return perspectiveRepository.findAll();
    }
    
    public Optional<Perspective> getById(Long id) {
        return perspectiveRepository.findById(id);
    }
    
    public Perspective create(Perspective perspective) {
        // Verificar si ya existe una perspectiva con la misma descripción
        if (perspectiveRepository.existsByDescription(perspective.getDescription())) {
            throw new RuntimeException("Ya existe una perspectiva con la descripción: " + perspective.getDescription());
        }
        return perspectiveRepository.save(perspective);
    }
    
    public Optional<Perspective> update(Long id, Perspective perspectiveDetails) {
        return perspectiveRepository.findById(id)
                .map(perspective -> {
                    // Verificar si la nueva descripción ya existe (excluyendo el actual)
                    if (!perspective.getDescription().equals(perspectiveDetails.getDescription()) && 
                        perspectiveRepository.existsByDescription(perspectiveDetails.getDescription())) {
                        throw new RuntimeException("Ya existe una perspectiva con la descripción: " + perspectiveDetails.getDescription());
                    }
                    
                    perspective.setDescription(perspectiveDetails.getDescription());
                    return perspectiveRepository.save(perspective);
                });
    }
    
    public boolean delete(Long id) {
        if (perspectiveRepository.existsById(id)) {
            perspectiveRepository.deleteById(id);
            return true;
        }
        return false;
    }
    
    public Optional<Perspective> getByDescription(String description) {
        return perspectiveRepository.findByDescription(description);
    }
    
    public boolean existsById(Long id) {
        return perspectiveRepository.existsById(id);
    }
    
    // Método para inicializar datos de prueba
    public void initializeSampleData() {
        if (perspectiveRepository.count() == 0) {
            String[] samplePerspectives = {
                "Primera Persona", "Tercera Persona", "Omnisciente", 
                "Múltiple", "Segunda Persona", "Objetiva"
            };
            
            for (String perspectiveDesc : samplePerspectives) {
                Perspective perspective = new Perspective();
                perspective.setDescription(perspectiveDesc);
                perspectiveRepository.save(perspective);
            }
        }
    }
}