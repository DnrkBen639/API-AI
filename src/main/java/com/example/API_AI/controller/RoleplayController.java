package com.example.API_AI.controller;

import com.example.API_AI.service.RoleplayAIService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/roleplay")
public class RoleplayController {

    @Autowired
    private RoleplayAIService roleplayService;

    // Almacena sesiones de roleplay con configuración y estado de la conversación
    private Map<String, Map<String, Object>> roleplaySessions = new HashMap<>();

    @PostMapping("/start")
    public Map<String, Object> startRoleplay(@RequestBody Map<String, String> request) {
        try {
            String sessionId = request.getOrDefault("sessionId", "roleplay_" + System.currentTimeMillis());
            String configJson = request.get("config");
            String userInput = request.get("userInput");
            
            if (configJson == null || configJson.trim().isEmpty()) {
                return Map.of(
                    "response", "Error: Se requiere configuración JSON para el roleplay",
                    "status", "error"
                );
            }

            if (userInput == null || userInput.trim().isEmpty()) {
                return Map.of(
                    "response", "Error: Proporcione la situación inicial del roleplay",
                    "status", "error"
                );
            }
            
            String roleplayResponse = roleplayService.generateRoleplay(configJson, userInput);
            
            // Crear datos de sesión para roleplay
            Map<String, Object> sessionData = new HashMap<>();
            sessionData.put("conversation", roleplayResponse);
            sessionData.put("config", configJson);
            sessionData.put("fullHistory", roleplayResponse); // Historial completo
            sessionData.put("turnCount", 1);
            
            roleplaySessions.put(sessionId, sessionData);
            
            return Map.of(
                "response", roleplayResponse,
                "sessionId", sessionId,
                "turn", 1,
                "status", "success"
            );
            
        } catch (Exception e) {
            return Map.of(
                "response", "Error al iniciar roleplay: " + e.getMessage(),
                "status", "error"
            );
        }
    }

    @PostMapping("/continue")
    public Map<String, Object> continueRoleplay(@RequestBody Map<String, String> request) {
        try {
            String sessionId = request.get("sessionId");
            String userInput = request.get("message");
            
            if (sessionId == null || userInput == null) {
                return Map.of(
                    "response", "Error: sessionId y message son requeridos",
                    "status", "error"
                );
            }
            
            Map<String, Object> sessionData = roleplaySessions.get(sessionId);
            if (sessionData == null) {
                return Map.of(
                    "response", "Error: Sesión de roleplay no encontrada. Inicia una nueva sesión primero.",
                    "status", "error"
                );
            }
            
            String currentConversation = (String) sessionData.get("conversation");
            String configJson = (String) sessionData.get("config");
            String fullHistory = (String) sessionData.get("fullHistory");
            Integer turnCount = (Integer) sessionData.get("turnCount");
            
            String continuedResponse = roleplayService.continueRoleplay(userInput, configJson);
            
            // Actualizar historial de conversación
            String updatedConversation = currentConversation + "\n\n[Turno " + (turnCount + 1) + "]\n" + continuedResponse;
            String updatedFullHistory = fullHistory + "\n\nUsuario: " + userInput + "\nPersonaje: " + continuedResponse;
            
            sessionData.put("conversation", updatedConversation);
            sessionData.put("fullHistory", updatedFullHistory);
            sessionData.put("turnCount", turnCount + 1);
            
            return Map.of(
                "response", continuedResponse,
                "sessionId", sessionId,
                "currentConversation", updatedConversation,
                "turn", turnCount + 1,
                "status", "success"
            );
            
        } catch (Exception e) {
            return Map.of(
                "response", "Error al continuar roleplay: " + e.getMessage(),
                "status", "error"
            );
        }
    }

    @GetMapping("/conversation/{sessionId}")
    public Map<String, Object> getConversation(@PathVariable String sessionId) {
        Map<String, Object> sessionData = roleplaySessions.get(sessionId);
        if (sessionData == null) {
            return Map.of(
                "conversation", "No hay conversación para esta sesión",
                "status", "error"
            );
        }
        return Map.of(
            "conversation", sessionData.get("conversation"),
            "fullHistory", sessionData.get("fullHistory"),
            "turnCount", sessionData.get("turnCount"),
            "status", "success"
        );
    }

    @DeleteMapping("/session/{sessionId}")
    public Map<String, String> clearSession(@PathVariable String sessionId) {
        roleplaySessions.remove(sessionId);
        roleplayService.clearMemory();
        return Map.of(
            "status", "success", 
            "message", "Sesión de roleplay y memoria limpiadas"
        );
    }

    @PostMapping("/clear-memory")
    public Map<String, String> clearMemory() {
        try {
            roleplayService.clearMemory();
            return Map.of(
                "status", "success", 
                "message", "Memoria del roleplay limpiada"
            );
        } catch (Exception e) {
            return Map.of(
                "status", "error", 
                "message", "Error limpiando memoria: " + e.getMessage()
            );
        }
    }

    @GetMapping("/status")
    public Map<String, Object> getStatus() {
        return Map.of(
            "initialized", roleplayService.isInitialized(),
            "pythonStatus", roleplayService.getPythonStatus(),
            "activeSessions", roleplaySessions.size(),
            "status", "success"
        );
    }

    @GetMapping("/sessions")
    public Map<String, Object> getAllSessions() {
        // Método útil para debugging - muestra todas las sesiones activas de roleplay
        Map<String, Object> sessionsInfo = new HashMap<>();
        for (Map.Entry<String, Map<String, Object>> entry : roleplaySessions.entrySet()) {
            Map<String, Object> sessionInfo = new HashMap<>();
            sessionInfo.put("conversationLength", ((String) entry.getValue().get("conversation")).length());
            sessionInfo.put("turnCount", entry.getValue().get("turnCount"));
            sessionInfo.put("hasConfig", entry.getValue().containsKey("config"));
            sessionsInfo.put(entry.getKey(), sessionInfo);
        }
        
        return Map.of(
            "sessions", sessionsInfo,
            "totalSessions", roleplaySessions.size(),
            "status", "success"
        );
    }

    // Endpoint adicional para obtener información de clothing tracking
    @GetMapping("/clothing-status/{sessionId}")
    public Map<String, Object> getClothingStatus(@PathVariable String sessionId) {
        Map<String, Object> sessionData = roleplaySessions.get(sessionId);
        if (sessionData == null) {
            return Map.of(
                "status", "error",
                "message", "Sesión no encontrada"
            );
        }
        
        // Nota: Esto requeriría modificar el servicio Python para soportar consultas de estado
        return Map.of(
            "status", "info",
            "message", "Clothing tracking activo - esta funcionalidad requiere implementación adicional en el servicio Python",
            "sessionId", sessionId
        );
    }

    // Endpoint para reinicializar el servicio si hay problemas
    @PostMapping("/reinitialize")
    public Map<String, String> reinitializeService() {
        try {
            // Lógica para reinicializar podría ir aquí
            return Map.of(
                "status", "success", 
                "message", "Reinicialización solicitada - puede requerir reinicio completo"
            );
        } catch (Exception e) {
            return Map.of(
                "status", "error", 
                "message", "Error en reinicialización: " + e.getMessage()
            );
        }
    }
}
