package com.example.API_AI.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {
    
    @GetMapping("/hello")
    public String hello() {
        return "¡Hola desde Spring Boot! 🚀";
    }
    
    @GetMapping("/")
    public String home() {
        return "La aplicación está funcionando correctamente ✅";
    }
}
