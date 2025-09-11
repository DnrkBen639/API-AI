package com.example.API_AI.controller;

import com.example.API_AI.dto.StoryConfigRequest;
import com.example.API_AI.dto.StoryConfigResponse;
import com.example.API_AI.service.GenreService;
import com.example.API_AI.service.PerspectiveService;
import com.example.API_AI.service.StoryConfigService;

import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;


@Controller
@RequestMapping("/web")
public class WebController {

    @Autowired
    private StoryConfigService storyConfigService;

    @Autowired
    private GenreService genreService;

    @Autowired 
    private PerspectiveService perspectiveService;

    @GetMapping("/")
    public String home(Model model) {
        model.addAttribute("title", "API AI - Generador de Historias");
        model.addAttribute("genres", genreService.getAll());
        model.addAttribute("perspectives", perspectiveService.getAll());
        return "web/home";
    }

    @PostMapping("/saveConfig")
    @ResponseBody // Add this annotation
    public ResponseEntity<?> saveConfig(@RequestBody StoryConfigRequest request) { // Change to @RequestBody
        try {
            StoryConfigResponse response = storyConfigService.create(request);
            
            return ResponseEntity.ok().body(Map.of(
                "status", "success",
                "id", response.getId(),
                "message", "Configuración guardada correctamente (ID: " + response.getId() + ")"
            ));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of(
                "status", "error",
                "message", "Error al guardar: " + e.getMessage()
            ));
        }
    }

    private com.example.API_AI.dto.StoryConfigRequest convertToStoryConfigRequest(StoryConfigRequest formRequest) {
        com.example.API_AI.dto.StoryConfigRequest request = new com.example.API_AI.dto.StoryConfigRequest();
        request.setFirstCharacter(formRequest.getFirstCharacter());
        request.setSecondCharacter(formRequest.getSecondCharacter());
        request.setBackground(formRequest.getBackground());
        request.setGenreId(formRequest.getGenreId());
        request.setPerspectiveId(formRequest.getPerspectiveId());
        return request;
    }

    @PostMapping("/api/saveConfig")
    @ResponseBody
    public StoryConfigResponse saveConfigApi(@RequestBody StoryConfigRequest request) {
        return storyConfigService.create(convertToStoryConfigRequest(request));
    }

    
}