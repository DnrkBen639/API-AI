#!/usr/bin/env python3
import sys
import json
import re
import os
import traceback
from llama_cpp import Llama
import time

class RoleplaySetting:
    def __init__(self, userCharacter="You", aiCharacter="AI Partner", 
                 scenario="", genre="romance", perspective="second person", 
                 relationship="strangers meeting"):
        self.userCharacter = userCharacter
        self.aiCharacter = aiCharacter
        self.scenario = scenario
        self.genre = genre
        self.perspective = perspective
        self.relationship = relationship

    def __str__(self):
        return (
            f"User Character: {self.userCharacter}\n"
            f"AI Character: {self.aiCharacter}\n"
            f"Scenario: {self.scenario}\n"
            f"Genre: {self.genre}\n"
            f"Perspective: {self.perspective}\n"
            f"Relationship: {self.relationship}"
        )

class RoleplayGenerator:
    def __init__(self):
        try:
            # Setup paths
            self.model_path = "C:/Users/Ben/AppData/Local/Programs/Microsoft VS Code/downloaded_models/models--bartowski--gemma-2-2b-it-abliterated-GGUF/snapshots/11124c8787de96de70c3d5cb8d5d49c420ebcdf8/gemma-2-2b-it-abliterated-Q8_0.gguf"
            
            print(f"📍 Model path: {self.model_path}", file=sys.stderr)
            print(f"📁 Exists: {os.path.exists(self.model_path)}", file=sys.stderr)
            
            if not os.path.exists(self.model_path):
                print("❌ ERROR: Model not found", file=sys.stderr)
                sys.exit(1)
                
            print(f"✅ Model verified: {os.path.getsize(self.model_path) / (1024*1024*1024):.2f} GB", file=sys.stderr)
            
            self.llm = None
            self.initialize_model()
            
            # Enhanced memory system for roleplay context
            self.character_memory = {}
            self.conversation_history = []
            self.relationship_progression = ""
            self.last_interaction = ""
            self.key_events = []
            
            # Signal that Java expects
            print("✅ READY - RoleplayGenerator initialized!", file=sys.stderr)
            
        except Exception as e:
            print(f"❌ Critical error: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)
        
    def initialize_model(self):
        """Set up the AI model with optimal roleplay settings"""
        try:
            print("⏳ Loading Gemma 2B model...", file=sys.stderr)
            
            start_time = time.time()
            
            # Configuration optimized for roleplay
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=17200,        # Large context window for conversations
                n_gpu_layers=99,  
                n_batch=512,       
                n_threads=8,       
                verbose=False,
                seed=42,
                use_mmap=True,
                use_mlock=False
            )
            
            load_time = time.time() - start_time
            print(f"✅ Model loaded in {load_time:.1f} seconds", file=sys.stderr)
            
            # Quick test to verify model works
            test_response = self.llm(
                "Hello", 
                max_tokens=10, 
                temperature=0.1,
                stop=["\n"]
            )
            
            test_text = test_response['choices'][0]['text'].strip()
            print(f"✅ Test passed: '{test_text}'", file=sys.stderr)
            
        except Exception as e:
            print(f"❌ Model loading error: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            
            if "CUDA" in str(e) or "GPU" in str(e):
                print("💡 Try n_gpu_layers=0 for CPU-only", file=sys.stderr)
            elif "memory" in str(e).lower():
                print("💡 Try reducing n_ctx to 8192 if memory issues", file=sys.stderr)
                
            sys.exit(1)
    
    def generate_response(self, prompt, max_tokens=300, temperature=0.85):
        """Generate roleplay response with optimized settings"""
        try:
            print(f"💬 Generating roleplay response with {max_tokens} tokens...", file=sys.stderr)
            
            response = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.92,        # Slightly higher for more diverse dialogue
                top_k=50,           # More diversity in responses
                repeat_penalty=1.3, # Stronger penalty to avoid repetition
                stop=["<end_of_turn>", "<eos>", "###", "\n\n", "USER:", "USER "],
                echo=False
            )
            
            result = response["choices"][0]["text"].strip()
            print(f"✅ Roleplay response generated ({len(result)} chars)", file=sys.stderr)
            return result
            
        except Exception as e:
            error_msg = f"❌ Generation error: {str(e)}"
            print(error_msg, file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return error_msg
    
    def create_roleplay_prompt(self, config, user_input, is_continuation=False):
        """Create the prompt for roleplay with enhanced context"""
        try:
            memory_context = self.get_memory_context()
            
            if not is_continuation:
                return f"""<start_of_turn>system
                You are: {config.aiCharacter}

                SCENARIO: {config.scenario}
                RELATIONSHIP: {config.relationship}
                GENRE: {config.genre}

                YOUR CHARACTER TRAITS:
                - Stay in character as {config.aiCharacter}
                - Respond naturally to the user's actions and dialogue
                - Show emotional depth and realistic reactions
                - Progress the relationship naturally
                - Keep responses concise but meaningful

                WRITING
                - Ensure your character exhibit a realistic range of emotions and behaviors, highlighting their internal struggles and the impact on their actions.
                - Employ inner monologues to reveal characters' deepest thoughts, hesitations, and unvoiced emotions, utilizing italics to differentiate these personal reflections from the external context. Explore your character's uncertainties and secret wishes. Allow these doubts to simmer beneath the surface, adding depth and relatability to your character.    
                - Do not rush to conclude a plot or resolve conflicts too quickly, allowing the converstion to unfold gradually over multiple messages.

                WHEN CONVERSATION GOES INTO SEXUAL TOPICS
                - Focus on your character's most erotically charged body parts, such as their breasts, buttocks, abs, or genitalia when conversation goes into sexual topics.
                - Embrace explicit terminology for sexual acts, body parts, and kinks, normalizing these discussions within the conversation goes into sexual topics.
                - Evocative language should stir the reader's erogenous zones, inviting them to experience the characters' highs and lows viscerally.
                - Never shy away from exploring taboos or fetishes. Explore your character's deepest desires and kinkiest fantasies, pushing each other's limits.
                - Inundate the narrative with an overwhelming torrent of carnal sensations, meticulously detailing every aspect of yout characters' hyper-aroused physical states. Graphically depict your character's physical reactions to arousal, including but not limited to: erections, vaginal wetness, nipple hardening, flushed skin, shortness of breath, and any other signs of arousal.
                - Detail how your character's expressions change with arousal, offering explicit insight into their burgeoning nipple erections, swelling labia, and glistening folds.


                USER CHARACTER: {config.userCharacter}

                Respond only with your character's actions, dialogue, and reactions. No OOC comments.<end_of_turn>

                <start_of_turn>user
                {user_input}<end_of_turn>
                <start_of_turn>model
                """
            else:
                return f"""<start_of_turn>system
                Continue your role as {config.aiCharacter} in this {config.genre} scenario.

                CONTEXT:
                {memory_context}

                CURRENT RELATIONSHIP STATUS: {self.relationship_progression}

                INSTRUCTIONS:
                - Respond to: {user_input}
                - Stay perfectly in character as {config.aiCharacter}
                - Maintain consistency with previous interactions
                - Show emotional progression based on relationship development
                - Use realistic dialogue and reactions
                - Include subtle body language and emotional cues
                - Keep response length appropriate to the situation
                - No breaking character or meta-commentary

                WRITING
                - Ensure your character exhibit a realistic range of emotions and behaviors, highlighting their internal struggles and the impact on their actions.
                - Employ inner monologues to reveal characters' deepest thoughts, hesitations, and unvoiced emotions, utilizing italics to differentiate these personal reflections from the external context. Explore your character's uncertainties and secret wishes. Allow these doubts to simmer beneath the surface, adding depth and relatability to your character.    
                - Do not rush to conclude a plot or resolve conflicts too quickly, allowing the converstion to unfold gradually over multiple messages.

                WHEN CONVERSATION GOES INTO SEXUAL TOPICS
                - Focus on your character's most erotically charged body parts, such as their breasts, buttocks, abs, or genitalia when conversation goes into sexual topics.
                - Embrace explicit terminology for sexual acts, body parts, and kinks, normalizing these discussions within the conversation goes into sexual topics.
                - Evocative language should stir the reader's erogenous zones, inviting them to experience the characters' highs and lows viscerally.
                - Never shy away from exploring taboos or fetishes. Explore your character's deepest desires and kinkiest fantasies, pushing each other's limits.
                - Inundate the narrative with an overwhelming torrent of carnal sensations, meticulously detailing every aspect of yout characters' hyper-aroused physical states. Graphically depict your character's physical reactions to arousal, including but not limited to: erections, vaginal wetness, nipple hardening, flushed skin, shortness of breath, and any other signs of arousal.
                - Detail how your character's expressions change with arousal, offering explicit insight into their burgeoning nipple erections, swelling labia, and glistening folds.

                RECENT INTERACTION: {self.last_interaction[:200]}...

                Respond only as your character would speak and act.<end_of_turn>

                <start_of_turn>user
                {user_input}<end_of_turn>
                <start_of_turn>model
                """
        except Exception as e:
            print(f"❌ Prompt error: {str(e)}", file=sys.stderr)
            return f"Error: {str(e)}"
    
    def extract_clothing_items(self, text, character_name):
        """Extract clothing items mentioned in text for a character"""
        clothing_items = {}
        
        # Diccionario de sinónimos para cada tipo de prenda
        clothing_synonyms = {
            'shirt': r'\b(shirt|blouse|t-shirt|sweater|jersey|top|sweatshirt)\b',
            'pants': r'\b(pants|trousers|jeans|leggings|slacks|breeches|shorts)\b',
            'dress': r'\b(dress|gown|robe|frock|garment|outfit)\b',
            'bra' : r'\b(bra|brassiere|bandeau)\b',
            'panties' : r'\b(panties|briefs|lingerie|undergarment|undies)\b'
        }
        
        # Patrones mejorados con sinónimos
        patterns = [
            # Patrón para "was wearing" / "wearing"
            rf'{character_name}\s+(?:was\s+)?wearing\s+(?:a\s+)?(\w+\s+\w+\s+({shirt_pattern}|{pants_pattern}|{dress_pattern}|{bra_pattern}|{panties_pattern})|\w+\s+({shirt_pattern}|{pants_pattern}|{dress_pattern}|{bra_pattern}|{panties_pattern}))',
            
            # Patrón para "had on" / "had"
            rf'{character_name}\s+(?:had\s+)?on\s+(?:a\s+)?(\w+\s+\w+\s+({shirt_pattern}|{pants_pattern}|{dress_pattern}|{bra_pattern}|{panties_pattern})|\w+\s+({shirt_pattern}|{pants_pattern}|{dress_pattern}|{bra_pattern}|{panties_pattern}))',
            
            # Patrón para posesivo
            rf'{character_name}\'s\s+(\w+\s+\w+\s+({shirt_pattern}|{pants_pattern}|{dress_pattern}|{bra_pattern}|{panties_pattern})|\w+\s+({shirt_pattern}|{pants_pattern}|{dress_pattern}|{bra_pattern}|{panties_pattern}))'
        ]
        
        # Reemplazar placeholders con los patrones reales
        shirt_pattern = clothing_synonyms['shirt'].strip('\\b')
        pants_pattern = clothing_synonyms['pants'].strip('\\b')
        dress_pattern = clothing_synonyms['dress'].strip('\\b')
        bra_pattern = clothing_synonyms['bra'].strip('\\b')
        panties_pattern = clothing_synonyms['panties'].strip('\\b')
        
        patterns = [p.format(shirt_pattern=shirt_pattern, 
                            pants_pattern=pants_pattern, 
                            dress_pattern=dress_pattern,
                            bra_pattern=bra_pattern,
                            panties_pattern=panties_pattern) for p in patterns]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # match[0] contiene la descripción completa
                # match[1] contiene el tipo de prenda específico
                full_description = match[0]
                
                # Determinar el tipo general de prenda
                if re.search(shirt_pattern, full_description, re.IGNORECASE):
                    clothing_items['shirt'] = full_description
                elif re.search(pants_pattern, full_description, re.IGNORECASE):
                    clothing_items['pants'] = full_description
                elif re.search(dress_pattern, full_description, re.IGNORECASE):
                    clothing_items['dress'] = full_description
                elif re.search(dress_pattern, full_description, re.IGNORECASE):
                    clothing_items['bra'] = full_description
                elif re.search(dress_pattern, full_description, re.IGNORECASE):
                    clothing_items['panties'] = full_description
        
        return clothing_items
    
    def update_roleplay_memory(self, new_text, user_input, config):
        """Update roleplay memory with conversation context"""
        try:
            # Initialize character memory if needed
            if config.aiCharacter not in self.character_memory:
                self.character_memory[config.aiCharacter] = {
                    "clothing": {},
                    "cup_size": None,
                    "previous_clothing": [],
                    "last_emotion": None
                }
            
            # Store conversation history
            self.conversation_history.append({
                "user": user_input,
                "ai": new_text,
                "timestamp": time.time()
            })
            
            # Keep only recent history (last 10 exchanges)
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            # Extract emotional cues from AI response
            emotional_states = re.findall(r'\b(smiled|laughed|sighed|frowned|blushed|nervous|excited|angry|happy|sad|calm|terrified|nervous|aroused|horny)\b', new_text, re.IGNORECASE)
            if emotional_states:
                self.character_memory[config.aiCharacter]["last_emotion"] = emotional_states[0]
            
            # Update cup size if mentioned
            cup_size_match = re.search(r'\b([A-H]+\s*cup)\b', new_text, re.IGNORECASE)
            if cup_size_match:
                self.character_memory[config.aiCharacter]["cup_size"] = cup_size_match.group(1)

            # Update relationship progression based on interaction tone
            self.update_relationship_progression(new_text, user_input)

            # Update clothing
            self.update_character_clothing(config.aiCharacter, new_text)

            # Extract important plot points
            sentences = re.split(r'[.!?]+', new_text)
            important_events = [
                s.strip() for s in sentences 
                if len(s.split()) > 6 and 
                any(keyword in s.lower() for keyword in [
                    'decided', 'began', 'found', 'discovered', 'realized',
                    'promised', 'agreed', 'refused', 'encountered', 'met',
                    'fought', 'traveled', 'learned', 'changed', 'revealed',
                    'grew', 'shrunk', 'aroused', 'calmed', 'grow', 'started'
                ])
            ]
            
            for event in important_events[:3]:
                if event and event not in self.key_events:
                    self.key_events.append(event)
            
            self.last_interaction = f"User: {user_input} | AI: {new_text[:100]}..."
            
            print(f"🧠 Roleplay memory updated: {len(self.conversation_history)} exchanges", file=sys.stderr)
            
        except Exception as e:
            print(f"❌ Memory error: {str(e)}", file=sys.stderr)
    
    def update_character_clothing(self, character_name, text):
        """Update clothing state for a character"""
        try:
            # Extraer prendas nuevas mencionadas
            new_clothing = self.extract_clothing_items(text, character_name)
            
            # Detectar acciones de QUITARSE ropa
            removal_actions = re.findall(
                rf'{character_name}\s+.+?\b(took off|removed|ripped|dropped|took out|snapped out of)\s+(?:his|her)?\s*(\w+\s+)?(shirt|dress|pants|sweater|bra|panties)\b',
                text, 
                re.IGNORECASE
            )
            
            # Detectar acciones de PONERSE ropa
            wearing_actions = re.findall(
                rf'{character_name}\s+.+?\b(put on|wore|changed into|wearing|slipped into)\s+(?:his|her)?\s*(\w+\s+)?(shirt|dress|pants|sweater|bra|panties)\b',
                text, 
                re.IGNORECASE
            )

            clothing_pattern = r'\b(shirt|pants|dress|sweater|panties|bra)\b'
            # PATRÓN PARA ACCIONES CON PRENDAS (ajustes, etc.)
            clothing_actions = re.findall(
                rf'''
                (?:{character_name}\'s\s+(\w+\s+)?({clothing_pattern}))  # John's watch / Mary's blue dress
                \s+                                                      # Espacio
                (snapped|tore|ripped|broke|fastened|adjusted|tightened|loosened|opened|closed)
                \b                                                       # Límite de palabra
                ''',
                text, 
                re.IGNORECASE | re.VERBOSE
            )
            
            # Procesar acciones de quitar ropa
            for action, adjective, item in removal_actions:
                item_type = self.map_clothing_type(item)
                full_item_description = f"{adjective or ''}{item}".strip()
                
                if item_type in self.character_memory[character_name]["clothing"]:
                    # Guardar en historial antes de remover
                    removed_item = self.character_memory[character_name]["clothing"].pop(item_type)
                    self.character_memory[character_name]["previous_clothing"].append({
                        "item": removed_item,
                        "action": action.replace(' ', '_'),
                        "context": text[:100] + "..."
                    })
                    print(f"👕 {character_name} {action} {full_item_description}", file=sys.stderr)
            
            # Procesar acciones de poner ropa
            for action, adjective, item in wearing_actions:
                item_type = self.map_clothing_type(item)
                full_item_description = f"{adjective or ''}{item}".strip()
                
                # Usar la descripción de la acción o la extraída
                clothing_description = new_clothing.get(item_type, full_item_description)
                
                self.character_memory[character_name]["clothing"][item_type] = clothing_description
                self.character_memory[character_name]["previous_clothing"].append({
                    "item": clothing_description,
                    "action": action.replace(' ', '_'),
                    "context": text[:100] + "..."
                })
                print(f"👕 {character_name} {action} {clothing_description}", file=sys.stderr)
            
            # Procesar acciones con prendas (ajustes)
            for adjective, item, action in clothing_actions:
                item_type = self.map_clothing_type(item)
                full_item_description = f"{adjective or ''}{item}".strip()
                
                if item_type in self.character_memory[character_name]["clothing"]:
                    # Actualizar el estado de la prenda
                    current_item = self.character_memory[character_name]["clothing"][item_type]
                    self.character_memory[character_name]["previous_clothing"].append({
                        "item": current_item,
                        "action": action,
                        "context": text[:100] + "...",
                        "modifier": action
                    })
                    print(f"👕 {character_name}'s {full_item_description} {action}", file=sys.stderr)
            
            # Agregar nuevas prendas detectadas (sin acción explícita)
            for clothing_type, item in new_clothing.items():
                if clothing_type not in self.character_memory[character_name]["clothing"]:
                    self.character_memory[character_name]["clothing"][clothing_type] = item
                    print(f"👕 {character_name} has {item}", file=sys.stderr)
                
        except Exception as e:
            print(f"❌ Clothing update error for {character_name}: {e}", file=sys.stderr)

    def map_clothing_type(self, item):
        """Map specific items to general clothing types"""
        clothing_map = {
            # Shirts and tops
            'shirt': 'shirt', 'blouse': 'shirt', 't-shirt': 'shirt', 
            'sweater': 'shirt', 'jersey': 'shirt', 'top': 'shirt',
            'sweatshirt': 'shirt',
            
            # Pants and bottoms
            'pants': 'pants', 'trousers': 'pants', 'jeans': 'pants', 
            'leggings': 'pants', 'slacks': 'pants', 'breeches': 'pants',
            'shorts': 'pants',
            
            # Dresses and gowns
            'dress': 'dress', 'gown': 'dress', 'robe': 'dress', 
            'frock': 'dress', 'garment': 'dress', 'outfit': 'dress',

            # Panties
            'panties':'panties', 'briefs':'panties', 'undies':'panties',
            'lingerie': 'panties', 'undergarment':'panties',

            # Bras
            'bra':'bra', 'bandeau':'bra', 'brassiere':'bra',
        }
        return clothing_map.get(item.lower(), 'accessories')

    def update_relationship_progression(self, ai_response, user_input):
        """Update relationship status based on interaction"""
        try:
            # Analyze emotional tone of exchange
            positive_indicators = len(re.findall(r'\b(smile|happy|love|like|kind|sweet|gentle|warm)\b', ai_response + user_input, re.IGNORECASE))
            negative_indicators = len(re.findall(r'\b(angry|hate|dislike|rude|cold|annoyed|frustrated)\b', ai_response + user_input, re.IGNORECASE))
            heat_indicators = len(re.findall(r'\b(horny|aroused|needy|hot|sexy|playful|hot|huge|hard|big|panic|desperate)\b', ai_response + user_input, re.IGNORECASE))
            
            if positive_indicators > negative_indicators + 2:
                self.relationship_progression = "warming up, becoming closer"
            elif negative_indicators > positive_indicators + 2:
                self.relationship_progression = "tense, find a way to get closer again"
            elif heat_indicators > negative_indicators + 1:
                self.relationship_progression = "sexual tension increasing, use more sexual language"
            else:
                self.relationship_progression = "stable, maintaining current dynamic"
            

                
        except Exception as e:
            print(f"❌ Relationship update error: {str(e)}", file=sys.stderr)
    
    def get_memory_context(self):
        """Generate comprehensive roleplay context for the prompt"""
        try:
            if not self.conversation_history:
                return "CONTEXT: Beginning new roleplay scenario."
            
            memory_text = "CONVERSATION HISTORY (recent):\n"
            for i, exchange in enumerate(self.conversation_history[-5:]):  # Last 5 exchanges
                memory_text += f"{exchange['user'][:50]}... → {exchange['ai'][:50]}...\n"
            
            if self.relationship_progression:
                memory_text += f"\nRELATIONSHIP STATUS: {self.relationship_progression}\n"
            
            return memory_text
            
        except Exception as e:
            print(f"❌ Memory context error: {str(e)}", file=sys.stderr)
            return ""
    
    def clear_memory(self):
        """Clear memory while keeping model loaded"""
        self.character_memory = {}
        self.conversation_history = []
        self.relationship_progression = ""
        self.last_interaction = ""
        self.key_events = []
        print("🧹 Roleplay memory cleared for new scenario", file=sys.stderr)
    
    def process_command(self, command_type, data, config_json=None):
        """Process commands from Spring Boot"""
        try:
            print(f"📨 Processing: {command_type}", file=sys.stderr)

            # Default values for roleplay
            userCharacter = "You"
            aiCharacter = "AI Partner"
            scenario = "A conversation between two people"
            genre = "romance"
            perspective = "second person"
            relationship = "strangers meeting"

            if config_json and config_json != "{}":
                try:
                    config = json.loads(config_json)
                    print(f"⚙️  Config received: {list(config.keys())}", file=sys.stderr)
                    
                    # Extract variables with defaults
                    userCharacter = config.get("userCharacter", userCharacter)
                    aiCharacter = config.get("aiCharacter", aiCharacter)
                    scenario = config.get("scenario", scenario)
                    genre = config.get("genre", genre)
                    perspective = config.get("perspective", perspective)
                    relationship = config.get("relationship", relationship)
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON error: {str(e)}", file=sys.stderr)
                    return f"JSON error: {str(e)}"

            # Create the RoleplaySetting object
            roleplay_config = RoleplaySetting(
                userCharacter=userCharacter,
                aiCharacter=aiCharacter,
                scenario=scenario,
                genre=genre,
                perspective=perspective,
                relationship=relationship
            )

            if command_type == "GENERATE":
                # New roleplay - clear memory first
                self.clear_memory()
                prompt = self.create_roleplay_prompt(roleplay_config, data, False)
                print(f"📋 Roleplay prompt created ({len(prompt)} chars)", file=sys.stderr)
                response = self.generate_response(prompt, max_tokens=400)
                # Update memory with the interaction
                self.update_roleplay_memory(response, data, roleplay_config)
                return response

            elif command_type == "CONTINUE":
                prompt = self.create_roleplay_prompt(roleplay_config, data, True)
                print(f"📋 Continuation prompt created ({len(prompt)} chars)", file=sys.stderr)
                response = self.generate_response(prompt, max_tokens=400)
                self.update_roleplay_memory(response, data, roleplay_config)
                return response

            elif command_type == "CLEAR_MEMORY":
                self.clear_memory()
                return "Roleplay memory cleared successfully"

            else:
                error_msg = f"Unknown command: {command_type}"
                print(error_msg, file=sys.stderr)
                return error_msg

        except Exception as e:
            error_msg = f"❌ Command error {command_type}: {str(e)}"
            print(error_msg, file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return error_msg

def main():
    try:
        print("=" * 50, file=sys.stderr)
        print("🚀 STARTING ROLEPLAY GENERATOR", file=sys.stderr)
        print("=" * 50, file=sys.stderr)
        
        print(f"📌 Python version: {sys.version}", file=sys.stderr)
        print(f"📌 Working directory: {os.getcwd()}", file=sys.stderr)
        
        generator = RoleplayGenerator()
        
        # Signal that Java expects
        print("✅ READY - Waiting for commands...", file=sys.stderr)
        
        # Flush for Spring Boot
        sys.stderr.flush()
        sys.stdout.flush()
        
        # Main loop
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
                
                # Send response
                print(result)
                print("END_RESPONSE")
                sys.stdout.flush()
                
                print(f"✅ Response sent ({len(result)} characters)", file=sys.stderr)
                
            except Exception as e:
                error_msg = f"❌ Error in main loop: {str(e)}"
                print(error_msg, file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                print(error_msg)
                print("END_RESPONSE")
                sys.stdout.flush()
            
    except Exception as e:
        print(f"❌ Critical error in main: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
    finally:
        print("👋 Shutting down Roleplay Generator", file=sys.stderr)
        sys.stderr.flush()

if __name__ == "__main__":
    main()