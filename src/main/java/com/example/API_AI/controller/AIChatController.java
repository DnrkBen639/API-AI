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

    // Cambiado a Map<String, Object> para almacenar tanto la historia como la configuración
    private Map<String, Map<String, Object>> userSessions = new HashMap<>();

    @PostMapping("/start-story")
    public Map<String, Object> startStory(@RequestBody Map<String, String> request) {
        try {
            String sessionId = request.getOrDefault("sessionId", "session_" + System.currentTimeMillis());
            String configJson = request.get("config");
            String userInput = request.get("userInput");
            
            if (configJson == null || configJson.trim().isEmpty()) {
                return Map.of(
                    "response", "Error: Se requiere configuración JSON",
                    "status", "error"
                );
            }

            if (userInput == null || userInput.trim().isEmpty()) {
                return Map.of(
                    "response", "Error: Configure la situación inicial",
                    "status", "error"
                );
            }
            
            String story = aiStoryService.generateStory(configJson, userInput);
            
            // Crear mapa de sesión con ambos datos
            Map<String, Object> sessionData = new HashMap<>();
            sessionData.put("story", story);
            sessionData.put("config", configJson);
            
            // Ahora sí funciona porque userSessions es Map<String, Map<String, Object>>
            userSessions.put(sessionId, sessionData);
            
            return Map.of(
                "response", story,
                "sessionId", sessionId,
                "status", "success"
            );
            
        } catch (Exception e) {
            return Map.of(
                "response", "Error al iniciar historia: " + e.getMessage(),
                "status", "error"
            );
        }
    }

    @PostMapping("/continue-story")
    public Map<String, Object> continueStory(@RequestBody Map<String, String> request) {
        try {
            String sessionId = request.get("sessionId");
            String userInput = request.get("message");
            
            if (sessionId == null || userInput == null) {
                return Map.of(
                    "response", "Error: sessionId y message son requeridos",
                    "status", "error"
                );
            }
            
            Map<String, Object> sessionData = userSessions.get(sessionId);
            if (sessionData == null) {
                return Map.of(
                    "response", "Error: Sesión no encontrada. Inicia una nueva historia primero.",
                    "status", "error"
                );
            }
            
            String currentStory = (String) sessionData.get("story");
            String configJson = (String) sessionData.get("config");
            
            String continuedStory = aiStoryService.continueStory(userInput, configJson);
            
            String updatedStory = currentStory + "\n\n" + continuedStory;
            sessionData.put("story", updatedStory);
            
            return Map.of(
                "response", continuedStory,
                "sessionId", sessionId,
                "fullStory", updatedStory,
                "status", "success"
            );
            
        } catch (Exception e) {
            return Map.of(
                "response", "Error al continuar historia: " + e.getMessage(),
                "status", "error"
            );
        }
    }

    @GetMapping("/story/{sessionId}")
    public Map<String, Object> getStory(@PathVariable String sessionId) {
        Map<String, Object> sessionData = userSessions.get(sessionId);
        if (sessionData == null) {
            return Map.of(
                "story", "No hay historia para esta sesión",
                "status", "error"
            );
        }
        return Map.of(
            "story", sessionData.get("story"),
            "status", "success"
        );
    }

    @DeleteMapping("/story/{sessionId}")
    public Map<String, String> clearStory(@PathVariable String sessionId) {
        userSessions.remove(sessionId);
        aiStoryService.clearMemory();
        return Map.of(
            "status", "success", 
            "message", "Historia y memoria limpiadas"
        );
    }

    @GetMapping("/status")
    public Map<String, Object> getStatus() {
        return Map.of(
            "initialized", aiStoryService.isInitialized(),
            "activeSessions", userSessions.size(),
            "status", "success"
        );
    }

    @GetMapping("/sessions")
    public Map<String, Object> getAllSessions() {
        // Método útil para debugging - muestra todas las sesiones activas
        Map<String, Object> sessionsInfo = new HashMap<>();
        for (Map.Entry<String, Map<String, Object>> entry : userSessions.entrySet()) {
            Map<String, Object> sessionInfo = new HashMap<>();
            sessionInfo.put("storyLength", ((String) entry.getValue().get("story")).length());
            sessionInfo.put("hasConfig", entry.getValue().containsKey("config"));
            sessionsInfo.put(entry.getKey(), sessionInfo);
        }
        
        return Map.of(
            "sessions", sessionsInfo,
            "totalSessions", userSessions.size(),
            "status", "success"
        );
    }
}