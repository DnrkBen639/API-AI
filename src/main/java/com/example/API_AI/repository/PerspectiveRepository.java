package com.example.API_AI.repository;

import com.example.API_AI.models.Perspective;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface PerspectiveRepository extends JpaRepository<Perspective, Long> {
    Optional<Perspective> findByDescription(String description);
    boolean existsByDescription(String description);
}