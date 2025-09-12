package com.example.API_AI.service;

import org.springframework.stereotype.Service;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import java.io.*;
import java.util.concurrent.TimeUnit;

@Service
public class RoleplayAIService {

    private Process pythonProcess;
    private BufferedReader reader;
    private BufferedWriter writer;
    private boolean initialized = false;
    private boolean reinitializationAttempted = false;

    @PostConstruct
    public void initialize() {
        try {
            // Obtener el directorio actual del proyecto
            String projectDir = System.getProperty("user.dir");
            String pythonScriptPath = projectDir + "/src/main/python/roleplay_generator.py";
            
            System.out.println("📍 Inicializando proceso Python para Roleplay...");
            System.out.println("📍 Ruta del script: " + pythonScriptPath);
            
            // Verificar que el script existe
            File scriptFile = new File(pythonScriptPath);
            if (!scriptFile.exists()) {
                System.err.println("❌ El script Python no existe en: " + pythonScriptPath);
                throw new RuntimeException("El script Python no existe en: " + pythonScriptPath);
            }
            
            ProcessBuilder pb = new ProcessBuilder("py", pythonScriptPath);
            pb.redirectErrorStream(true);
            pb.directory(new File(projectDir));
            pythonProcess = pb.start();
            
            reader = new BufferedReader(new InputStreamReader(pythonProcess.getInputStream()));
            writer = new BufferedWriter(new OutputStreamWriter(pythonProcess.getOutputStream()));
            
            // DEBUG: Leer toda la salida inicial
            System.out.println("📍 Esperando inicialización Python para Roleplay...");
            StringBuilder initOutput = new StringBuilder();
            long startTime = System.currentTimeMillis();
            boolean ready = false;
            boolean modelLoaded = false;
            
            while (System.currentTimeMillis() - startTime < 180000) { // 3 minutos para cargar modelo
                if (reader.ready()) {
                    String line = reader.readLine();
                    if (line != null) {
                        System.out.println("PYTHON ROLEPLAY OUTPUT: " + line);
                        initOutput.append(line).append("\n");
                        
                        if (line.contains("READY") || line.contains("✅ READY") || 
                            line.contains("✅") && line.contains("RoleplayGenerator initialized")) {
                            ready = true;
                            System.out.println("✅ Detected ready signal: " + line);
                        }

                        if (line.contains("Model loaded") || line.contains("Model loaded in") || 
                            line.contains("Test passed") || line.contains("✅ Model verified")) {
                            modelLoaded = true;
                            System.out.println("✅ Detected model loaded signal: " + line);
                        }
                        
                        if (line.contains("✅ READY - Waiting for commands...")) {
                            ready = true;
                            modelLoaded = true;
                            System.out.println("✅ Full initialization complete: " + line);
                        }
                        
                        if (line.contains("ERROR") || line.contains("Error") || line.contains("❌")) {
                            System.err.println("❌ Python reportó error: " + line);
                            break;
                        }
                        
                        // Considerar listo si tanto el modelo está cargado como el proceso está ready
                        if (ready && modelLoaded) {
                            break;
                        }
                    }
                }
                TimeUnit.MILLISECONDS.sleep(100);
                
                // Verificar si el proceso sigue vivo
                if (!pythonProcess.isAlive()) {
                    System.err.println("❌ Proceso Python murió durante inicialización");
                    break;
                }
            }
            
            if (!pythonProcess.isAlive()) {
                int exitCode = pythonProcess.exitValue();
                System.err.println("❌ Proceso Python terminó con código: " + exitCode);
                throw new RuntimeException("Proceso Python terminó durante inicialización. Código: " + exitCode);
            }
            
            if (!ready || !modelLoaded) {
                System.err.println("❌ Timeout en inicialización Python. Output completo:");
                System.err.println(initOutput.toString());
                throw new RuntimeException("Timeout inicializando proceso Python. ¿Modelo cargado correctamente?");
            }
            
            initialized = true;
            reinitializationAttempted = false;
            System.out.println("✅ Proceso Python para Roleplay inicializado correctamente");
            
        } catch (Exception e) {
            System.err.println("❌ Error inicializando proceso Python para Roleplay: " + e.getMessage());
            initialized = false;
            // No relanzar la excepción para permitir reintentos posteriores
        }
    }

    public String generateRoleplay(String configJson, String userInput) {
        return sendCommand("GENERATE", userInput, configJson);
    }

    public String continueRoleplay(String userInput, String configJson) {
        return sendCommand("CONTINUE", userInput, configJson);
    }

    public String clearMemory() {
        return sendCommand("CLEAR_MEMORY", "", "{}");
    }

    private String sendCommand(String commandType, String data, String configJson) {
        try {
            if (!initialized || pythonProcess == null || !pythonProcess.isAlive()) {
                System.out.println("⚠️  Proceso Python no activo, intentando reinicializar...");
                // Solo intentar reinicializar una vez por comando
                if (!reinitializationAttempted) {
                    reinitializationAttempted = true;
                    initialize();
                } else {
                    throw new RuntimeException("Reinicialización ya intentada previamente");
                }
            }
            
            if (!pythonProcess.isAlive()) {
                String lastOutput = getLastPythonOutput();
                throw new RuntimeException("El proceso Python no está activo. Output previo: " + lastOutput);
            }
            
            String command = String.format("%s|%s|%s\n", commandType, data, configJson);
            System.out.println("📤 Enviando comando Roleplay: " + command.replace("\n", "\\n"));
            
            writer.write(command);
            writer.flush();
            
            StringBuilder response = new StringBuilder();
            String line;
            long startTime = System.currentTimeMillis();
            boolean responseStarted = false;
            boolean endResponseFound = false;
            
            // Leer respuesta con timeout
            while (System.currentTimeMillis() - startTime < 120000) { // 2 minutos timeout
                if (reader.ready()) {
                    line = reader.readLine();
                    if (line != null) {
                        System.out.println("📥 Python roleplay response: " + line);
                        if (line.equals("END_RESPONSE")) {
                            endResponseFound = true;
                            break;
                        }
                        if (responseStarted || !line.trim().isEmpty()) {
                            response.append(line).append("\n");
                            responseStarted = true;
                        }
                    }
                } else if (responseStarted) {
                    // Pequeña pausa para evitar CPU alto
                    TimeUnit.MILLISECONDS.sleep(50);
                }
                
                // Verificar si el proceso murió durante la respuesta
                if (!pythonProcess.isAlive()) {
                    System.err.println("❌ Proceso Python murió durante la respuesta");
                    break;
                }
            }
            
            if (!endResponseFound) {
                System.err.println("⚠️  Timeout o END_RESPONSE no recibido");
            }
            
            String result = response.toString().trim();
            if (result.isEmpty()) {
                throw new RuntimeException("Timeout o respuesta vacía del proceso Python");
            }
            
            return result;
            
        } catch (Exception e) {
            // Marcar como no inicializado para reintentos futuros
            initialized = false;
            reinitializationAttempted = false;
            throw new RuntimeException("Error enviando comando a Python: " + e.getMessage(), e);
        }
    }

    @PreDestroy
    public void shutdown() {
        try {
            if (pythonProcess != null) {
                // Enviar comando de salida limpia si está vivo
                if (pythonProcess.isAlive()) {
                    try {
                        if (writer != null) {
                            writer.write("EXIT\n");
                            writer.flush();
                            System.out.println("📤 Enviando comando EXIT al proceso Python de Roleplay");
                            TimeUnit.SECONDS.sleep(2); // Dar tiempo para shutdown limpio
                        }
                    } catch (Exception e) {
                        System.err.println("⚠️  Error enviando comando EXIT: " + e.getMessage());
                    }
                }
                
                // Destruir el proceso
                if (pythonProcess.isAlive()) {
                    pythonProcess.destroy();
                    TimeUnit.SECONDS.sleep(1);
                    
                    if (pythonProcess.isAlive()) {
                        pythonProcess.destroyForcibly();
                        System.out.println("⚠️  Proceso Python de Roleplay forzado a terminar");
                    }
                }
                
                System.out.println("✅ Proceso Python de Roleplay terminado");
            }
        } catch (Exception e) {
            System.err.println("❌ Error terminando proceso Python: " + e.getMessage());
        } finally {
            // Cerrar recursos
            try {
                if (reader != null) reader.close();
                if (writer != null) writer.close();
            } catch (IOException e) {
                System.err.println("⚠️  Error cerrando streams: " + e.getMessage());
            }
        }
    }
    
    private String getLastPythonOutput() {
        try {
            StringBuilder output = new StringBuilder();
            // Leer todo lo que haya disponible
            while (reader != null && reader.ready()) {
                String line = reader.readLine();
                if (line != null) {
                    output.append(line).append("\n");
                }
            }
            return output.toString().isEmpty() ? "No hay output disponible" : output.toString();
        } catch (Exception e) {
            return "Error leyendo output: " + e.getMessage();
        }
    }
    
    public boolean isInitialized() {
        return initialized && pythonProcess != null && pythonProcess.isAlive();
    }
    
    public String getPythonStatus() {
        if (pythonProcess == null) {
            return "No inicializado";
        }
        if (pythonProcess.isAlive()) {
            return "Activo";
        } else {
            try {
                return "Inactivo (exit code: " + pythonProcess.exitValue() + ")";
            } catch (IllegalThreadStateException e) {
                return "Inactivo (exit code no disponible)";
            }
        }
    }
    
    // Métodos adicionales específicos para roleplay
    public String getClothingStatus(String characterName) {
        // Este método podría usarse para consultar el estado de la vestimenta
        // Requeriría modificar el script Python para soportar este comando
        return "Clothing tracking functionality available";
    }
    
    public String getCharacterMemory(String characterName) {
        // Método para consultar la memoria del personaje
        return "Character memory tracking available";
    }
}