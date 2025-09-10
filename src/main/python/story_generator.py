#!/usr/bin/env python3
import sys
import json
import re
import os
import traceback
from llama_cpp import Llama
import time

class StoryGenerator:
    def __init__(self):
        try:
            # CONFIGURACIÓN DE RUTAS
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Ruta exacta donde está el modelo (usa la que ya tienes configurada)
            self.model_path = "C:/Users/Ben/AppData/Local/Programs/Microsoft VS Code/downloaded_models/models--bartowski--gemma-2-2b-it-abliterated-GGUF/snapshots/11124c8787de96de70c3d5cb8d5d49c420ebcdf8/gemma-2-2b-it-abliterated-Q4_K_M.gguf"
            
            print(f"📍 Ruta del modelo: {self.model_path}", file=sys.stderr)
            print(f"📁 Existe: {os.path.exists(self.model_path)}", file=sys.stderr)
            
            if not os.path.exists(self.model_path):
                print("❌ ERROR: El modelo no existe en la ruta especificada", file=sys.stderr)
                sys.exit(1)
                
            print(f"✅ Modelo verificado: {os.path.getsize(self.model_path) / (1024*1024*1024):.2f} GB", file=sys.stderr)
            
            self.llm = None
            self.initialize_model()
            
            # Sistema de memoria
            self.character_memory = {}
            self.plot_points = []
            self.last_summary = ""
            
            # MENSAJE CLAVE QUE JAVA ESPERA - debe contener "ready"
            print("✅ READY - StoryGenerator initialized successfully!", file=sys.stderr)
            
        except Exception as e:
            print(f"❌ Error crítico en __init__: {str(e)}", file=sys.stderr)
            print(f"📋 Traceback completo:\n{traceback.format_exc()}", file=sys.stderr)
            sys.exit(1)
        
    def initialize_model(self):
        """Inicializa el modelo de IA"""
        try:
            print("⏳ Inicializando modelo Gemma 2B...", file=sys.stderr)
            
            start_time = time.time()
            
            # CONFIGURACIÓN MÁS CONSERVADORA
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=2048,      # REDUCIDO - mucho más seguro
                n_gpu_layers=10,  # REDUCIDO - empieza con pocas capas en GPU
                n_batch=128,      # REDUCIDO
                n_threads=2,      # REDUCIDO
                verbose=False,    # Desactivado para menos output
                seed=42           # Para reproducibilidad
            )
            
            load_time = time.time() - start_time
            print(f"✅ Modelo cargado en {load_time:.1f} segundos", file=sys.stderr)
            
            # Test MUY simple para verificar funcionamiento
            print("🧪 Realizando test básico...", file=sys.stderr)
            test_response = self.llm(
                "Hola", 
                max_tokens=5, 
                temperature=0.1,
                stop=["\n"]
            )
            
            test_text = test_response['choices'][0]['text'].strip()
            print(f"✅ Test exitoso: '{test_text}'", file=sys.stderr)
            
        except Exception as e:
            print(f"❌ Error inicializando modelo: {str(e)}", file=sys.stderr)
            print(f"📋 Traceback:\n{traceback.format_exc()}", file=sys.stderr)
            
            # Sugerencias específicas basadas en el error
            if "CUDA" in str(e) or "GPU" in str(e):
                print("💡 SUGERENCIA: Intenta con n_gpu_layers=0 para usar solo CPU", file=sys.stderr)
            elif "memory" in str(e).lower():
                print("💡 SUGERENCIA: Reduce n_ctx o n_gpu_layers", file=sys.stderr)
                
            sys.exit(1)
    
    def generate_text(self, prompt, max_tokens=350, temperature=0.8):
        """Genera texto usando el modelo"""
        try:
            print(f"📝 Generando texto con {max_tokens} tokens...", file=sys.stderr)
            
            response = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                repeat_penalty=1.2,
                stop=["<end_of_turn>", "<eos>", "###", "\n\n\n", "END_OF_STORY"]
            )
            
            result = response["choices"][0]["text"].strip()
            print(f"✅ Texto generado ({len(result)} caracteres)", file=sys.stderr)
            return result
            
        except Exception as e:
            error_msg = f"❌ Error en generación: {str(e)}"
            print(error_msg, file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            return error_msg
    
    def create_story_prompt(self, config, user_input, is_continuation=False):
        """Crea el prompt para la generación"""
        try:
            if not is_continuation:
                return f"""<start_of_turn>system
Escribe el PRIMER CAPÍTULO de una historia de {config.get('genre', 'fantasía')} con:

SITUACIÓN INICIAL: {config.get('situation', 'una aventura emocionante')}

PERSONAJES PRINCIPALES:
1. {config.get('char1', 'Personaje 1')}
2. {config.get('char2', 'Personaje 2')}

REGLAS:
- Usar perspectiva: {config.get('perspective', 'tercera persona')}
- Estilo narrativo apropiado para el género
- Introducir conflicto o misterio inicial
- Longitud: aproximadamente 300-400 palabras

Responde solo con el texto de la historia, sin comentarios.<end_of_turn>

<start_of_turn>user
Comienza la historia<end_of_turn>
<start_of_turn>model
"""
            else:
                # Usar memoria para mejor coherencia
                memory_context = self.get_memory_context()
                
                return f"""<start_of_turn>system
Continúa la historia manteniendo coherencia con:

Género: {config.get('genre', 'fantasía')}
Personajes: {config.get('char1', 'Personaje 1')} y {config.get('char2', 'Personaje 2')}
Perspectiva: {config.get('perspective', 'tercera persona')}

{memory_context}

Contexto previo: {config.get('current_story', '')[:800]}...

INSTRUCCIONES:
- Desarrolla la historia naturalmente basado en: {user_input}
- Mantén coherencia con personajes y eventos establecidos
- Longitud: 150-250 palabras
- Responde solo con el siguiente segmento narrativo

Responde únicamente con texto narrativo, sin metadatos.<end_of_turn>

<start_of_turn>user
{user_input}<end_of_turn>
<start_of_turn>model
"""
        except Exception as e:
            print(f"❌ Error creando prompt: {str(e)}", file=sys.stderr)
            return f"Error creando prompt: {str(e)}"
    
    def update_story_memory(self, new_text):
        """Actualiza la memoria de personajes y eventos"""
        try:
            # Extraer nombres de personajes
            characters = self.extract_characters(new_text)
            for char in characters:
                if char not in self.character_memory:
                    self.character_memory[char] = {"mentions": 1, "last_seen": new_text[:200]}
                else:
                    self.character_memory[char]["mentions"] += 1
            
            # Extraer eventos importantes
            sentences = re.split(r'[.!?]+', new_text)
            significant_events = [s.strip() for s in sentences if len(s.split()) > 5 and any(word in s.lower() for word in ['decidió', 'empezó', 'encontró', 'descubrió', 'sintió', 'pensó'])]
            
            for event in significant_events[:2]:
                if event and event not in self.plot_points:
                    self.plot_points.append(event)
                    
            print(f"🧠 Memoria actualizada: {len(self.character_memory)} personajes, {len(self.plot_points)} eventos", file=sys.stderr)
            
        except Exception as e:
            print(f"❌ Error actualizando memoria: {str(e)}", file=sys.stderr)
    
    def extract_characters(self, text):
        """Extrae nombres propios potenciales de personajes"""
        try:
            words = re.findall(r'\b[A-Z][a-z]{2,}\b', text)
            common_words = {'The', 'And', 'But', 'For', 'With', 'This', 'That', 'There', 'Then', 'You', 'Your', 'They'}
            potential_names = [word for word in words if word not in common_words]
            return list(set(potential_names))[:4]
        except:
            return []
    
    def get_memory_context(self):
        """Genera contexto de memoria para el prompt"""
        try:
            if not self.character_memory:
                return "MEMORIA: Primera generación de la historia."
            
            memory_text = "MEMORIA DE PERSONAJES:\n"
            for char, info in list(self.character_memory.items())[:3]:
                memory_text += f"- {char}: mencionado {info['mentions']} veces\n"
            
            if self.plot_points:
                memory_text += "\nEVENTOS RECIENTES:\n"
                for event in self.plot_points[-3:]:
                    memory_text += f"- {event}\n"
            
            return memory_text
            
        except Exception as e:
            print(f"❌ Error obteniendo contexto de memoria: {str(e)}", file=sys.stderr)
            return ""
    
    def clear_memory(self):
        """Limpia la memoria"""
        self.character_memory = {}
        self.plot_points = []
        self.last_summary = ""
        print("🧹 Memoria limpiada", file=sys.stderr)
    
    def process_command(self, command_type, data, config_json=None):
        """Procesa comandos desde Spring Boot"""
        try:
            print(f"📨 Procesando comando: {command_type}", file=sys.stderr)
            
            config = {}
            if config_json:
                try:
                    config = json.loads(config_json)
                    print(f"⚙️  Configuración recibida: {list(config.keys())}", file=sys.stderr)
                except json.JSONDecodeError as e:
                    print(f"❌ Error decodificando JSON: {str(e)}", file=sys.stderr)
                    return f"Error en formato JSON: {str(e)}"
            
            if command_type == "GENERATE":
                # Nueva historia - limpiar memoria primero
                self.clear_memory()
                prompt = self.create_story_prompt(config, data, False)
                print(f"📋 Prompt de generación creado ({len(prompt)} caracteres)", file=sys.stderr)
                response = self.generate_text(prompt, max_tokens=450)
                # Actualizar memoria con la nueva historia
                self.update_story_memory(response)
                return response
            
            elif command_type == "CONTINUE":
                prompt = self.create_story_prompt(config, data, True)
                print(f"📋 Prompt de continuación creado ({len(prompt)} caracteres)", file=sys.stderr)
                response = self.generate_text(prompt, max_tokens=300)
                # Actualizar memoria con la continuación
                self.update_story_memory(response)
                return response
            
            elif command_type == "CLEAR_MEMORY":
                self.clear_memory()
                return "Memoria limpiada correctamente"
            
            else:
                error_msg = f"Comando no reconocido: {command_type}"
                print(error_msg, file=sys.stderr)
                return error_msg
                
        except Exception as e:
            error_msg = f"❌ Error procesando comando {command_type}: {str(e)}"
            print(error_msg, file=sys.stderr)
            print(f"📋 Traceback:\n{traceback.format_exc()}", file=sys.stderr)
            return error_msg

def main():
    try:
        print("=" * 50, file=sys.stderr)
        print("🚀 INICIANDO STORY GENERATOR", file=sys.stderr)
        print("=" * 50, file=sys.stderr)
        
        print(f"📌 Python version: {sys.version}", file=sys.stderr)
        print(f"📌 Working directory: {os.getcwd()}", file=sys.stderr)
        
        generator = StoryGenerator()
        
        # MENSAJE CLAVE QUE JAVA ESPERA - debe contener "ready"
        print("✅ READY - Waiting for commands...", file=sys.stderr)
        
        # Flush crítico para que Spring Boot vea los mensajes
        sys.stderr.flush()
        sys.stdout.flush()
        
        # Bucle principal
        while True:
            try:
                line = sys.stdin.readline().strip()
                if not line:
                    print("📭 No input received (possible shutdown)", file=sys.stderr)
                    break
                    
                print(f"📥 Received command: {line[:50]}...", file=sys.stderr)
                
                parts = line.split('|', 2)
                if len(parts) < 2:
                    error_msg = "ERROR: Invalid command format. Expected: COMMAND|DATA|CONFIG"
                    print(error_msg, file=sys.stderr)
                    print(error_msg)
                    print("END_RESPONSE")
                    sys.stdout.flush()
                    continue
                    
                command_type = parts[0]
                data = parts[1] if len(parts) > 1 else ""
                config_json = parts[2] if len(parts) > 2 else "{}"
                
                result = generator.process_command(command_type, data, config_json)
                
                # Enviar respuesta
                print(result)
                print("END_RESPONSE")
                sys.stdout.flush()
                
                print(f"✅ Response sent ({len(result)} characters)", file=sys.stderr)
                
            except Exception as e:
                error_msg = f"❌ Error in main loop: {str(e)}"
                print(error_msg, file=sys.stderr)
                print(traceback.format_exc(), file=sys.stderr)
                print(error_msg)
                print("END_RESPONSE")
                sys.stdout.flush()
            
    except Exception as e:
        print(f"❌ Critical error in main: {str(e)}", file=sys.stderr)
        print(f"📋 Full traceback:\n{traceback.format_exc()}", file=sys.stderr)
    finally:
        print("👋 Shutting down Story Generator", file=sys.stderr)
        sys.stderr.flush()

if __name__ == "__main__":
    main()