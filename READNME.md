# CV Analyzer - Sistema Multi-Agente

Sistema inteligente para automatizar aplicaciones a trabajos usando IA.

## Setup
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

## Configuración

1. El archivo `.env` ya está configurado en `backend/.env`
2. Ejecutar tests: `python test_job_analyzer.py`

## Estructura
```
cv-analyzer/
├── backend/          # Código backend
│   ├── agents/       # Agentes IA
│   ├── services/     # Servicios Azure
│   └── models/       # Modelos de datos
└── data/             # Datos de prueba
```