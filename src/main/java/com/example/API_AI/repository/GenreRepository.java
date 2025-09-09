package com.example.API_AI.repository;

import com.example.API_AI.models.Genre;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface GenreRepository extends JpaRepository<Genre, Long> {
    Optional<Genre> findByDescription(String description);
    boolean existsByDescription(String description);
}