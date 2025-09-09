package com.example.API_AI.service;

import org.springframework.stereotype.Service;
import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;
import java.io.*;
import java.util.concurrent.TimeUnit;

@Service
public class AIStoryService {

    private Process pythonProcess;
    private BufferedReader reader;
    private BufferedWriter writer;

    @PostConstruct
    public void initialize() {
        try {
            // Obtener el directorio actual del proyecto
            String projectDir = System.getProperty("user.dir");
            String pythonScriptPath = projectDir + "/src/main/python/story_generator.py";
            
            System.out.println("📍 Inicializando proceso Python...");
            System.out.println("📍 Ruta del script: " + pythonScriptPath);
            
            ProcessBuilder pb = new ProcessBuilder("python", pythonScriptPath);
            pb.redirectErrorStream(true);
            pb.directory(new File(projectDir));
            pythonProcess = pb.start();
            
            reader = new BufferedReader(new InputStreamReader(pythonProcess.getInputStream()));
            writer = new BufferedWriter(new OutputStreamWriter(pythonProcess.getOutputStream()));
            
            // Esperar a que el proceso se inicialice
            TimeUnit.SECONDS.sleep(3);
            
            // Leer salida inicial
            StringBuilder initOutput = new StringBuilder();
            while (reader.ready()) {
                initOutput.append(reader.readLine()).append("\n");
            }
            System.out.println("Salida inicial Python: " + initOutput.toString());
            
        } catch (Exception e) {
            System.err.println("❌ Error inicializando proceso Python: " + e.getMessage());
            throw new RuntimeException("Error inicializando proceso Python", e);
        }
    }

    public String generateStory(String configJson) {
        return sendCommand("GENERATE", "Iniciar historia", configJson);
    }

    public String continueStory(String userInput, String configJson) {
        return sendCommand("CONTINUE", userInput, configJson);
    }

    public String clearMemory() {
        return sendCommand("CLEAR_MEMORY", "", "{}");
    }

    private String sendCommand(String commandType, String data, String configJson) {
        try {
            if (pythonProcess == null) {
                initialize();
            }
            
            String command = String.format("%s|%s|%s\n", commandType, data, configJson);
            writer.write(command);
            writer.flush();
            
            StringBuilder response = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.equals("END_RESPONSE")) {
                    break;
                }
                response.append(line).append("\n");
            }
            
            return response.toString().trim();
            
        } catch (Exception e) {
            throw new RuntimeException("Error enviando comando a Python: " + e.getMessage(), e);
        }
    }

    @PreDestroy
    public void shutdown() {
        try {
            if (pythonProcess != null) {
                pythonProcess.destroy();
                System.out.println("✅ Proceso Python terminado");
            }
        } catch (Exception e) {
            System.err.println("❌ Error terminando proceso Python: " + e.getMessage());
        }
    }
}