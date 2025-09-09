package com.example.API_AI.service;

import org.springframework.stereotype.Service;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import java.io.*;
import java.util.concurrent.TimeUnit;

@Service
public class AIStoryService {

    private Process pythonProcess;
    private BufferedReader reader;
    private BufferedWriter writer;
    private boolean initialized = false;

    @PostConstruct
    public void initialize() {
        try {
            // Obtener el directorio actual del proyecto
            String projectDir = System.getProperty("user.dir");
            String pythonScriptPath = projectDir + "/src/main/python/story_generator.py";
            
            System.out.println("📍 Inicializando proceso Python...");
            System.out.println("📍 Ruta del script: " + pythonScriptPath);
            
            // Verificar que el script existe
            File scriptFile = new File(pythonScriptPath);
            if (!scriptFile.exists()) {
                throw new RuntimeException("El script Python no existe en: " + pythonScriptPath);
            }
            
            ProcessBuilder pb = new ProcessBuilder("python", pythonScriptPath);
            pb.redirectErrorStream(true);
            pb.directory(new File(projectDir));
            pythonProcess = pb.start();
            
            reader = new BufferedReader(new InputStreamReader(pythonProcess.getInputStream()));
            writer = new BufferedWriter(new OutputStreamWriter(pythonProcess.getOutputStream()));
            
            // Esperar a que el proceso se inicialice
            TimeUnit.SECONDS.sleep(3);
            
            // Leer salida inicial para verificar que funciona
            StringBuilder initOutput = new StringBuilder();
            long startTime = System.currentTimeMillis();
            while (System.currentTimeMillis() - startTime < 5000) { // timeout de 5 segundos
                if (reader.ready()) {
                    String line = reader.readLine();
                    if (line != null) {
                        initOutput.append(line).append("\n");
                        if (line.contains("ready") || line.contains("Ready")) {
                            break;
                        }
                    }
                }
                TimeUnit.MILLISECONDS.sleep(100);
            }
            
            System.out.println("Salida inicial Python: " + initOutput.toString());
            initialized = true;
            System.out.println("✅ Proceso Python inicializado correctamente");
            
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
            if (!initialized || pythonProcess == null) {
                initialize();
            }
            
            if (!pythonProcess.isAlive()) {
                throw new RuntimeException("El proceso Python no está activo");
            }
            
            String command = String.format("%s|%s|%s\n", commandType, data, configJson);
            System.out.println("Enviando comando: " + command.replace("\n", "\\n"));
            
            writer.write(command);
            writer.flush();
            
            StringBuilder response = new StringBuilder();
            String line;
            long startTime = System.currentTimeMillis();
            boolean responseStarted = false;
            
            // Leer respuesta con timeout
            while (System.currentTimeMillis() - startTime < 30000) { // 30 segundos timeout
                if (reader.ready()) {
                    line = reader.readLine();
                    if (line != null) {
                        if (line.equals("END_RESPONSE")) {
                            break;
                        }
                        response.append(line).append("\n");
                        responseStarted = true;
                    }
                } else if (responseStarted) {
                    // Pequeña pausa para evitar CPU alto
                    TimeUnit.MILLISECONDS.sleep(100);
                }
            }
            
            String result = response.toString().trim();
            if (result.isEmpty()) {
                throw new RuntimeException("Timeout o respuesta vacía del proceso Python");
            }
            
            return result;
            
        } catch (Exception e) {
            throw new RuntimeException("Error enviando comando a Python: " + e.getMessage(), e);
        }
    }

    @PreDestroy
    public void shutdown() {
        try {
            if (pythonProcess != null && pythonProcess.isAlive()) {
                // Enviar comando de salida limpia
                try {
                    writer.write("EXIT\n");
                    writer.flush();
                    TimeUnit.SECONDS.sleep(1);
                } catch (Exception e) {
                    // Ignorar errores en shutdown
                }
                
                pythonProcess.destroy();
                if (pythonProcess.isAlive()) {
                    pythonProcess.destroyForcibly();
                }
                System.out.println("✅ Proceso Python terminado");
            }
        } catch (Exception e) {
            System.err.println("❌ Error terminando proceso Python: " + e.getMessage());
        }
    }
    
    public boolean isInitialized() {
        return initialized && pythonProcess != null && pythonProcess.isAlive();
    }
}