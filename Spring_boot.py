#!/usr/bin/env python3
import sys
import json
import re
import os
from llama_cpp import Llama
import time

class StoryGenerator:
    def __init__(self):
        # CONFIGURACIÓN DE RUTAS - AJUSTA ESTA RUTA!
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Diferentes posibles ubicaciones del modelo
        possible_paths = [
            # Ruta relativa desde el script
            os.path.join(current_dir, "models", "gemma-2-2b-it-abliterated-Q4_K_M.gguf"),
            # Ruta absoluta (ajusta según tu sistema)
            "C:/Users/Ben/AppData/Local/Programs/Microsoft VS Code/downloaded_models/models--bartowski--gemma-2-2b-it-abliterated-GGUF/snapshots/11124c8787de96de70c3d5cb8d5d49c420ebcdf8/gemma-2-2b-it-abliterated-Q4_K_M.gguf",
            # Otra posible ruta
            os.path.join(current_dir, "..", "..", "models", "gemma-2-2b-it-abliterated-Q4_K_M.gguf")
        ]
        
        # Encontrar la ruta correcta
        self.model_path = None
        for path in possible_paths:
            if os.path.exists(path):
                self.model_path = path
                break
        
        if not self.model_path:
            print("❌ ERROR: No se encontró el modelo en ninguna de las rutas probadas", file=sys.stderr)
            print("📍 Rutas probadas:", file=sys.stderr)
            for path in possible_paths:
                print(f"   - {path} → Existe: {os.path.exists(path)}", file=sys.stderr)
            sys.exit(1)
        
        print(f"✅ Modelo encontrado en: {self.model_path}", file=sys.stderr)
        
        self.llm = None
        self.initialize_model()
        
        # Sistema de memoria
        self.character_memory = {}
        self.plot_points = []
        self.last_summary = ""
        
    def initialize_model(self):
        """Inicializa el modelo de IA"""
        try:
            print("⏳ Inicializando modelo Gemma 2B...", file=sys.stderr)
            
            start_time = time.time()
            
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=8192,
                n_gpu_layers=99,
                n_batch=512,
                n_threads=6,
                verbose=False
            )
            
            load_time = time.time() - start_time
            print(f"✅ Modelo cargado en {load_time:.1f} segundos", file=sys.stderr)
            
        except Exception as e:
            print(f"❌ Error inicializando modelo: {e}", file=sys.stderr)
            sys.exit(1)
    
    def generate_text(self, prompt, max_tokens=350, temperature=0.8):
        """Genera texto usando el modelo"""
        try:
            response = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                repeat_penalty=1.2,
                stop=["<end_of_turn>", "<eos>", "###", "\n\n\n"]
            )
            return response["choices"][0]["text"].strip()
        except Exception as e:
            return f"Error en generación: {str(e)}"
    
    def create_story_prompt(self, config, user_input, is_continuation=False):
        """Crea el prompt para la generación"""
        if not is_continuation:
            return f"""<start_of_turn>system
Escribe el PRIMER CAPÍTULO de una historia de {config.get('genre', '')} con:

SITUACIÓN INICIAL: {config.get('situation', '')}

PERSONAJES PRINCIPALES:
1. {config.get('char1', '')}
2. {config.get('char2', '')}

REGLAS:
- Usar perspectiva: {config.get('perspective', '')}
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

Género: {config.get('genre', '')}
Personajes: {config.get('char1', '')} y {config.get('char2', '')}
Perspectiva: {config.get('perspective', '')}

{memory_context}

Contexto previo: {config.get('current_story', '')[:1000]}...

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
    
    def update_story_memory(self, new_text):
        """Actualiza la memoria de personajes y eventos"""
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
    
    def extract_characters(self, text):
        """Extrae nombres propios potenciales de personajes"""
        words = re.findall(r'\b[A-Z][a-z]{2,}\b', text)
        common_words = {'The', 'And', 'But', 'For', 'With', 'This', 'That', 'There', 'Then'}
        potential_names = [word for word in words if word not in common_words]
        return list(set(potential_names))[:4]
    
    def get_memory_context(self):
        """Genera contexto de memoria para el prompt"""
        if not self.character_memory:
            return ""
        
        memory_text = "MEMORIA DE PERSONAJES:\n"
        for char, info in list(self.character_memory.items())[:3]:
            memory_text += f"- {char}: mencionado {info['mentions']} veces\n"
        
        memory_text += "\nEVENTOS RECIENTES:\n"
        for event in self.plot_points[-3:]:
            memory_text += f"- {event}\n"
        
        return memory_text
    
    def clear_memory(self):
        """Limpia la memoria"""
        self.character_memory = {}
        self.plot_points = []
        self.last_summary = ""
    
    def process_command(self, command_type, data, config_json=None):
        """Procesa comandos desde Spring Boot"""
        try:
            config = json.loads(config_json) if config_json else {}
            
            if command_type == "GENERATE":
                # Nueva historia - limpiar memoria primero
                self.clear_memory()
                prompt = self.create_story_prompt(config, data, False)
                response = self.generate_text(prompt)
                # Actualizar memoria con la nueva historia
                self.update_story_memory(response)
                return response
            
            elif command_type == "CONTINUE":
                prompt = self.create_story_prompt(config, data, True)
                response = self.generate_text(prompt)
                # Actualizar memoria con la continuación
                self.update_story_memory(response)
                return response
            
            elif command_type == "CLEAR_MEMORY":
                self.clear_memory()
                return "Memoria limpiada"
            
            else:
                return "Comando no reconocido"
                
        except Exception as e:
            return f"Error procesando comando: {str(e)}"

def main():
    generator = StoryGenerator()
    print("🚀 Story Generator ready - Waiting for commands...", file=sys.stderr)
    
    try:
        while True:
            line = sys.stdin.readline().strip()
            if not line:
                break
                
            parts = line.split('|', 2)
            if len(parts) < 2:
                print("ERROR: Formato de comando inválido")
                continue
                
            command_type = parts[0]
            data = parts[1] if len(parts) > 1 else ""
            config_json = parts[2] if len(parts) > 2 else "{}"
            
            result = generator.process_command(command_type, data, config_json)
            
            # Enviar respuesta
            print(result)
            print("END_RESPONSE")
            sys.stdout.flush()
            
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
    finally:
        print("👋 Cerrando Story Generator", file=sys.stderr)

if __name__ == "__main__":
    main()