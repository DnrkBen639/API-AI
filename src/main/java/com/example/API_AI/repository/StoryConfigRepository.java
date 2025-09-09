package com.example.API_AI.repository;

import com.example.API_AI.models.StoryConfig;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface StoryConfigRepository extends JpaRepository<StoryConfig, Long> {
    
    List<StoryConfig> findByGenreId(Long genreId);
    
    List<StoryConfig> findByPerspectiveId(Long perspectiveId);
    
    @Query("SELECT sc FROM StoryConfig sc WHERE sc.genre.id = :genreId AND sc.perspective.id = :perspectiveId")
    List<StoryConfig> findByGenreAndPerspective(@Param("genreId") Long genreId, 
                                               @Param("perspectiveId") Long perspectiveId);
    
    @Query("SELECT sc FROM StoryConfig sc WHERE sc.firstCharacter LIKE %:characterName% OR sc.secondCharacter LIKE %:characterName%")
    List<StoryConfig> findByCharacterName(@Param("characterName") String characterName);
}