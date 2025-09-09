package com.example.API_AI.controller;

import com.example.API_AI.service.AIStoryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/ai")
public class AIChatController {

    @Autowired
    private AIStoryService aiStoryService;

    private Map<String, String> userSessions = new HashMap<>();

    @PostMapping("/start-story")
    public Map<String, String> startStory(@RequestBody Map<String, String> request) {
        String sessionId = request.getOrDefault("sessionId", "default");
        String configJson = request.get("config");
        
        String story = aiStoryService.generateStory("Iniciar historia", configJson);
        
        userSessions.put(sessionId, story);
        
        return Map.of(
            "response", story,
            "sessionId", sessionId,
            "status", "success"
        );
    }

    @PostMapping("/continue-story")
    public Map<String, String> continueStory(@RequestBody Map<String, String> request) {
        String sessionId = request.get("sessionId");
        String userInput = request.get("message");
        
        String currentStory = userSessions.getOrDefault(sessionId, "");
        String continuedStory = aiStoryService.continueStory(userInput, currentStory);
        
        // Actualizar la historia con la nueva continuación
        String updatedStory = currentStory + "\n\n" + continuedStory;
        userSessions.put(sessionId, updatedStory);
        
        return Map.of(
            "response", continuedStory,
            "sessionId", sessionId,
            "fullStory", updatedStory,
            "status", "success"
        );
    }

    @GetMapping("/story/{sessionId}")
    public Map<String, String> getStory(@PathVariable String sessionId) {
        String story = userSessions.getOrDefault(sessionId, "No hay historia para esta sesión");
        return Map.of("story", story);
    }

    @DeleteMapping("/story/{sessionId}")
    public Map<String, String> clearStory(@PathVariable String sessionId) {
        userSessions.remove(sessionId);
        return Map.of("status", "success", "message", "Historia limpiada");
    }
}