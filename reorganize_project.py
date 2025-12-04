# reorganize_project.py
"""
Script para reorganizar la estructura del proyecto
Ejecutar desde: C:\Proyecto IAAI\cv-analyzer
"""
import os
import shutil
import sys

def create_directory(path):
    """Crea un directorio si no existe"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f" Creado: {path}")
    else:
        print(f"  Ya existe: {path}")

def move_directory(src, dst):
    """Mueve un directorio si existe"""
    if os.path.exists(src) and not os.path.exists(dst):
        shutil.move(src, dst)
        print(f" Movido: {src} → {dst}")
    elif os.path.exists(dst):
        print(f"  Destino ya existe: {dst}")
    else:
        print(f"  Origen no existe: {src}")

def move_file(src, dst):
    """Mueve un archivo si existe"""
    if os.path.exists(src):
        # Crear directorio destino si no existe
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)
        print(f" Movido: {src} → {dst}")
    else:
        print(f"  Archivo no existe: {src}")

def create_file(path, content=""):
    """Crea un archivo con contenido"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f" Creado: {path}")

def reorganize():
    """Reorganiza el proyecto"""
    
    print("\n" + "="*70)
    print(" REORGANIZANDO ESTRUCTURA DEL PROYECTO")
    print("="*70 + "\n")
    
    base_path = os.getcwd()
    print(f" Ruta base: {base_path}\n")
    
    # Crear directorio backend si no existe
    print(" Creando estructura backend...\n")
    create_directory("backend")
    
    # Mover carpetas a backend
    print(" Moviendo carpetas a backend...\n")
    folders_to_move = [
        "agents",
        "models", 
        "services",
        "utils",
        "tests"
    ]
    
    for folder in folders_to_move:
        src = os.path.join(base_path, folder)
        dst = os.path.join(base_path, "backend", folder)
        move_directory(src, dst)
    
    # Mover archivos de configuración a backend
    print("\n Moviendo archivos de configuración...\n")
    files_to_move = [
        ("config.py", "backend/config.py"),
        ("requirements.txt", "backend/requirements.txt"),
        (".env", "backend/.env"),
    ]
    
    for src_file, dst_file in files_to_move:
        src = os.path.join(base_path, src_file)
        dst = os.path.join(base_path, dst_file)
        if os.path.exists(src):
            move_file(src, dst)
    
    # Mover venv a backend
    print("\n Moviendo entorno virtual...\n")
    venv_src = os.path.join(base_path, "venv")
    venv_dst = os.path.join(base_path, "backend", "venv")
    if os.path.exists(venv_src) and not os.path.exists(venv_dst):
        print("  Moviendo venv... esto puede tomar un momento...")
        move_directory(venv_src, venv_dst)
        print(" venv movido. Necesitarás reactivarlo desde backend/venv")
    
    # Crear archivos __init__.py
    print("\n Creando archivos __init__.py...\n")
    init_files = [
        "backend/__init__.py",
        "backend/agents/__init__.py",
        "backend/services/__init__.py",
        "backend/models/__init__.py",
        "backend/utils/__init__.py",
        "backend/tests/__init__.py",
    ]
    
    for init_file in init_files:
        path = os.path.join(base_path, init_file)
        if not os.path.exists(path):
            create_file(path, '"""Package initialization"""\n')
    
    # Crear carpeta api
    print("\n Creando estructura API...\n")
    create_directory("backend/api")
    create_directory("backend/api/routes")
    create_directory("backend/api/middlewares")
    create_file("backend/api/__init__.py", '"""API package"""\n')
    create_file("backend/api/routes/__init__.py", '"""API routes"""\n')
    
    # Crear .env.example si no existe
    if not os.path.exists("backend/.env.example"):
        env_example = """# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-key-here
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Azure Document Intelligence Configuration
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your-key-here

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
"""
        create_file("backend/.env.example", env_example)
    
    # Crear README si no existe
    if not os.path.exists("README.md"):
        readme = """# CV Analyzer - Sistema Multi-Agente

Sistema inteligente para automatizar aplicaciones a trabajos.

##  Setup Rápido

```bash
cd backend
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
```

## Configuración

1. Copiar `backend/.env.example` a `backend/.env`
2. Completar con credenciales de Azure
3. Ejecutar tests: `python test_job_analyzer.py`

##  Estructura

```
cv-analyzer/
├── backend/          # Código backend
│   ├── agents/       # Agentes IA
│   ├── services/     # Servicios Azure
│   ├── models/       # Modelos de datos
│   └── utils/        # Utilidades
├── data/             # Datos de prueba
└── frontend/         # UI (futuro)
```
"""
        create_file("README.md", readme)
    
    # Actualizar .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# Environment variables
.env

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
data/outputs/*
!data/outputs/.gitkeep
*.log
test_*.json
example_*.json

# Distribution
dist/
build/
*.egg-info/
"""
    create_file(".gitignore", gitignore_content)
    
    # Limpiar __pycache__ de la raíz
    pycache = os.path.join(base_path, "__pycache__")
    if os.path.exists(pycache):
        shutil.rmtree(pycache)
        print("🧹 Limpiado: __pycache__")
    
    print("\n" + "="*70)
    print(" REORGANIZACIÓN COMPLETADA")
    print("="*70 + "\n")
    
    print(" ESTRUCTURA FINAL:\n")
    print("cv-analyzer/")
    print("├── backend/")
    print("│   ├── agents/")
    print("│   ├── services/")
    print("│   ├── models/")
    print("│   ├── utils/")
    print("│   ├── api/")
    print("│   ├── tests/")
    print("│   ├── venv/")
    print("│   ├── .env")
    print("│   ├── .env.example")
    print("│   ├── config.py")
    print("│   └── requirements.txt")
    print("├── data/")
    print("├── frontend/")
    print("├── .gitignore")
    print("└── README.md")
    print()
    
    print("  IMPORTANTE:")
    print("1. El entorno virtual se movió a backend/venv")
    print("2. Debes reactivarlo:")
    print("   cd backend")
    print("   venv\\Scripts\\activate")
    print("3. Verifica que tu .env esté en backend/.env")
    print()

if __name__ == "__main__":
    try:
        # Confirmar antes de ejecutar
        print("\n  Este script reorganizará tu proyecto.")
        print("Se moverán carpetas y archivos a la estructura correcta.")
        response = input("\n¿Continuar? (s/n): ")
        
        if response.lower() in ['s', 'si', 'y', 'yes']:
            reorganize()
        else:
            print(" Operación cancelada")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)