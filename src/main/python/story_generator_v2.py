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
            
            # Enhanced memory system for better context
            self.character_memory = {}
            self.key_events = []
            self.story_summary = ""
            self.last_chunk = ""
            
            # Signal that Java expects
            print("✅ READY - StoryGenerator initialized!", file=sys.stderr)
            
        except Exception as e:
            print(f"❌ Critical error: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)
        
    def initialize_model(self):
        """Set up the AI model with optimal story generation settings"""
        try:
            print("⏳ Loading Gemma 2B model...", file=sys.stderr)
            
            start_time = time.time()
            
            # Configuration optimized for story generation
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=16384,        # Large context window for stories
                n_gpu_layers=99,  
                n_batch=512,       
                n_threads=8,       
                verbose=False,
                seed=42,
                use_mmap=True,      # Enable memory mapping for large models
                use_mlock=False     # Disable memory locking for flexibility
            )
            
            load_time = time.time() - start_time
            print(f"✅ Model loaded in {load_time:.1f} seconds", file=sys.stderr)
            
            # Quick test to verify model works
            test_response = self.llm(
                "Once upon a time", 
                max_tokens=5, 
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
    
    def generate_text(self, prompt, max_tokens=400, temperature=0.8):
        """Generate text using the model with story-optimized settings"""
        try:
            print(f"📝 Generating story text with {max_tokens} tokens...", file=sys.stderr)
            
            response = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                top_k=40,           # Add top_k sampling for better diversity
                repeat_penalty=1.2,
                stop=["<end_of_turn>", "<eos>", "###", "\n\n\n", "END_OF_STORY", "The end"],
                echo=False
            )
            
            result = response["choices"][0]["text"].strip()
            print(f"✅ Story segment generated ({len(result)} chars)", file=sys.stderr)
            return result
            
        except Exception as e:
            error_msg = f"❌ Generation error: {str(e)}"
            print(error_msg, file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return error_msg
    
    def create_story_prompt(self, config, user_input, is_continuation=False):
        """Create the prompt for generation with enhanced context"""
        try:
            if not is_continuation:
                return f"""<start_of_turn>system
You are a skilled storyteller. Write the FIRST CHAPTER of a {config.get('genre', 'fantasy')} story.

INITIAL SITUATION: {config.get('situation', 'an exciting adventure begins')}

MAIN CHARACTERS:
- {config.get('char1', 'Character 1')}
- {config.get('char2', 'Character 2')}

WRITING STYLE:
- Use {config.get('perspective', 'third person')} perspective
- Write in a style fitting for {config.get('genre', 'fantasy')}
- Introduce an engaging conflict or mystery
- Create vivid descriptions and natural dialogue
- Length: approximately 400-500 words

Respond only with the story text, no commentary or metadata.<end_of_turn>

<start_of_turn>user
Begin the story now<end_of_turn>
<start_of_turn>model
"""
            else:
                # Enhanced context for continuations
                memory_context = self.get_memory_context()
                recent_story = config.get('current_story', '')[:1200]  # Keep more context
                
                return f"""<start_of_turn>system
You are continuing a {config.get('genre', 'fantasy')} story. Maintain perfect consistency.

CHARACTERS:
- {config.get('char1', 'Character 1')}
- {config.get('char2', 'Character 2')}

PERSPECTIVE: {config.get('perspective', 'third person')}

{memory_context}

STORY SO FAR (last part): {recent_story}...

INSTRUCTIONS:
- Continue naturally based on: {user_input}
- Maintain perfect consistency with established characters, events, and tone
- Develop the plot forward in a compelling way
- Include descriptive elements and natural dialogue
- Length: 400-500 words
- Respond only with the next narrative segment

<end_of_turn>

<start_of_turn>user
{user_input}<end_of_turn>
<start_of_turn>model
"""
        except Exception as e:
            print(f"❌ Prompt error: {str(e)}", file=sys.stderr)
            return f"Error: {str(e)}"
    
    def update_story_memory(self, new_text):
        """Update character and event memory with enhanced tracking"""
        try:
            # Extract character names with better pattern matching
            characters = self.extract_characters(new_text)
            for char in characters:
                if char not in self.character_memory:
                    self.character_memory[char] = {
                        "mentions": 1, 
                        "last_seen": new_text[:250],
                        "traits": self.extract_character_traits(new_text, char),
                        "cup_size": None,  # Track cup size
                        "emotional_state": None  # Track emotional state
                    }
                else:
                    self.character_memory[char]["mentions"] += 1
                    # Update traits if new ones are discovered
                    new_traits = self.extract_character_traits(new_text, char)
                    if new_traits:
                        self.character_memory[char]["traits"].extend(
                            t for t in new_traits if t not in self.character_memory[char]["traits"]
                        )
                    # Update cup size and emotional state if mentioned
                    cup_size_match = re.search(r'\b([A-D]+\s*cup)\b', new_text, re.IGNORECASE)
                    if cup_size_match:
                        self.character_memory[char]["cup_size"] = cup_size_match.group(1)
                        emotional_state_match = re.search(r'\b(aroused|excited|embarrassed|terrified|calm|nervous|desperate)\b', new_text, re.IGNORECASE)
                    if emotional_state_match:
                        self.character_memory[char]["emotional_state"] = emotional_state_match.group(1)
            
            # Extract important plot points
            sentences = re.split(r'[.!?]+', new_text)
            important_events = [
                s.strip() for s in sentences 
                if len(s.split()) > 6 and 
                any(keyword in s.lower() for keyword in [
                    'decided', 'began', 'found', 'discovered', 'realized', 
                    'promised', 'agreed', 'refused', 'encountered', 'met',
                    'fought', 'traveled', 'learned', 'changed', 'revealed',
                    'grew', 'shrunk', 'aroused', 'calmed'
                ])
            ]
            
            for event in important_events[:3]:  # Keep more key events
                if event and event not in self.key_events:
                    self.key_events.append(event)
            
            # Update story summary
            self.update_story_summary(new_text)
                    
            print(f"🧠 Memory updated: {len(self.character_memory)} chars, {len(self.key_events)} events", file=sys.stderr)
            
        except Exception as e:
            print(f"❌ Memory error: {str(e)}", file=sys.stderr)
    
    def extract_characters(self, text):
        """Extract character names with better filtering"""
        try:
            # Look for proper nouns that might be characters
            words = re.findall(r'\b[A-Z][a-z]{2,}\b', text)
            common_words = {
                'The', 'And', 'But', 'For', 'With', 'This', 'That', 
                'There', 'Then', 'You', 'Your', 'They', 'She', 'He', 
                'It', 'We', 'Us', 'Our', 'Their', 'What', 'When', 'Where'
            }
            potential_names = [word for word in words if word not in common_words]
            
            # Also look for names in dialogue or descriptions
            dialogue_pattern = r'\"([A-Z][a-z]+ [A-Z][a-z]+|[A-Z][a-z]+)\"'
            dialogue_names = re.findall(dialogue_pattern, text)
            
            all_names = list(set(potential_names + dialogue_names))
            return all_names[:5]  # Reasonable number of characters to track
            
        except:
            return []
    
    def extract_character_traits(self, text, character_name):
        """Extract character traits from text"""
        traits = []
        try:
            # Look for descriptions involving the character
            pattern = rf"{character_name} (was|is|had|has|seemed|looked|appeared) ([^.!?]+)[.!?]"
            matches = re.findall(pattern, text, re.IGNORECASE)
            
            for match in matches:
                description = match[1].strip()
                if len(description.split()) > 2:  # Meaningful description
                    traits.append(description)
                    
        except:
            pass
            
        return traits
    
    def update_story_summary(self, new_text):
        """Update the overall story summary"""
        try:
            # Keep a concise summary of the story so far
            if len(self.story_summary) < 500:  # Keep summary manageable
                key_points = " ".join(self.key_events[-3:]) if self.key_events else ""
                self.story_summary = f"{self.story_summary} {key_points}".strip()[:500]
                
        except Exception as e:
            print(f"❌ Summary update error: {str(e)}", file=sys.stderr)
    
    def get_memory_context(self):
        """Generate comprehensive memory context for the prompt"""
        try:
            if not self.character_memory:
                return "CONTEXT: Beginning a new story."
            
            memory_text = "CHARACTER CONTEXT:\n"
            for char, info in list(self.character_memory.items())[:4]:  # Main characters
                memory_text += f"- {char}: mentioned {info['mentions']} times"
                if info['traits']:
                    memory_text += f", traits: {', '.join(info['traits'][:2])}"
                memory_text += "\n"
                if info['cup_size']:
                    memory_text += f", cup size: {info['cup_size']}"
                if info['emotional_state']:
                    memory_text += f", emotional state: {info['emotional_state']}"
                memory_text += "\n"
            
            if self.key_events:
                memory_text += "\nRECENT PLOT DEVELOPMENTS:\n"
                for event in self.key_events[-3:]:  # Recent key events
                    memory_text += f"- {event}\n"
            
            if self.story_summary:
                memory_text += f"\nSTORY SUMMARY: {self.story_summary}\n"
            
            return memory_text
            
        except Exception as e:
            print(f"❌ Memory context error: {str(e)}", file=sys.stderr)
            return ""
    
    def clear_memory(self):
        """Clear memory while keeping model loaded"""
        self.character_memory = {}
        self.key_events = []
        self.story_summary = ""
        self.last_chunk = ""
        print("🧹 Memory cleared for new story", file=sys.stderr)
    
    def process_command(self, command_type, data, config_json=None):
        """Process commands from Spring Boot"""
        try:
            print(f"📨 Processing: {command_type}", file=sys.stderr)
            
            config = {}
            if config_json:
                try:
                    config = json.loads(config_json)
                    print(f"⚙️  Config received: {list(config.keys())}", file=sys.stderr)
                except json.JSONDecodeError as e:
                    print(f"❌ JSON error: {str(e)}", file=sys.stderr)
                    return f"JSON error: {str(e)}"
            
            if command_type == "GENERATE":
                # New story - clear memory first
                self.clear_memory()
                prompt = self.create_story_prompt(config, data, False)
                print(f"📋 Generation prompt created ({len(prompt)} chars)", file=sys.stderr)
                response = self.generate_text(prompt, max_tokens=500)
                # Update memory with the new story
                self.update_story_memory(response)
                return response
            
            elif command_type == "CONTINUE":
                prompt = self.create_story_prompt(config, data, True)
                print(f"📋 Continuation prompt created ({len(prompt)} chars)", file=sys.stderr)
                response = self.generate_text(prompt, max_tokens=450)
                # Update memory with continuation
                self.update_story_memory(response)
                return response
            
            elif command_type == "CLEAR_MEMORY":
                self.clear_memory()
                return "Memory cleared successfully"
            
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
        print("🚀 STARTING STORY GENERATOR", file=sys.stderr)
        print("=" * 50, file=sys.stderr)
        
        print(f"📌 Python version: {sys.version}", file=sys.stderr)
        print(f"📌 Working directory: {os.getcwd()}", file=sys.stderr)
        
        generator = StoryGenerator()
        
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
        print("👋 Shutting down Story Generator", file=sys.stderr)
        sys.stderr.flush()

if __name__ == "__main__":
    main()