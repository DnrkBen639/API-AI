#!/usr/bin/env python3
import sys
import os

print("🔍 Diagnóstico del entorno Python:")
print(f"Python version: {sys.version}")
print(f"Current dir: {os.getcwd()}")

# Verificar que las dependencias estén instaladas
try:
    from llama_cpp import Llama
    print("✅ llama-cpp-python instalado")
except ImportError as e:
    print(f"❌ Error importando llama_cpp: {e}")

# Verificar rutas de modelo
possible_paths = [
    "C:/Users/Ben/AppData/Local/Programs/Microsoft VS Code/downloaded_models/models--bartowski--gemma-2-2b-it-abliterated-GGUF/snapshots/11124c8787de96de70c3d5cb8d5d49c420ebcdf8/gemma-2-2b-it-abliterated-Q4_K_M.gguf",
    # ... otras rutas
]

print("📁 Verificando rutas de modelo:")
for path in possible_paths:
    exists = os.path.exists(path)
    print(f"   {path} → {'✅' if exists else '❌'}")