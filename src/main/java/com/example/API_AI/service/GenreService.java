package com.example.API_AI.service;

import com.example.API_AI.models.Genre;
import com.example.API_AI.repository.GenreRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class GenreService {
    
    @Autowired
    private GenreRepository genreRepository;
    
    public List<Genre> getAll() {
        return genreRepository.findAll();
    }
    
    public Optional<Genre> getById(Long id) {
        return genreRepository.findById(id);
    }
    
    public Genre create(Genre genre) {
        // Verificar si ya existe un género con la misma descripción
        if (genreRepository.existsByDescription(genre.getDescription())) {
            throw new RuntimeException("Ya existe un género con la descripción: " + genre.getDescription());
        }
        return genreRepository.save(genre);
    }
    
    public Optional<Genre> update(Long id, Genre genreDetails) {
        return genreRepository.findById(id)
                .map(genre -> {
                    // Verificar si la nueva descripción ya existe (excluyendo el actual)
                    if (!genre.getDescription().equals(genreDetails.getDescription()) && 
                        genreRepository.existsByDescription(genreDetails.getDescription())) {
                        throw new RuntimeException("Ya existe un género con la descripción: " + genreDetails.getDescription());
                    }
                    
                    genre.setDescription(genreDetails.getDescription());
                    return genreRepository.save(genre);
                });
    }
    
    public boolean delete(Long id) {
        if (genreRepository.existsById(id)) {
            genreRepository.deleteById(id);
            return true;
        }
        return false;
    }
    
    public Optional<Genre> getByDescription(String description) {
        return genreRepository.findByDescription(description);
    }
    
    public boolean existsById(Long id) {
        return genreRepository.existsById(id);
    }
    
    // Método para inicializar datos de prueba
    public void initializeSampleData() {
        if (genreRepository.count() == 0) {
            String[] sampleGenres = {
                "Fantasía", "Ciencia Ficción", "Romance", "Terror", 
                "Aventura", "Misterio", "Histórico", "Comedia"
            };
            
            for (String genreDesc : sampleGenres) {
                Genre genre = new Genre();
                genre.setDescription(genreDesc);
                genreRepository.save(genre);
            }
        }
    }
}