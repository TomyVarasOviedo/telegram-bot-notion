# Especificaciones para Agentes

## Deployment

### Railway

- **Build**: Automático (detecta Python desde Dockerfile)
- **Puerto**: 8080 (configurable via variable `PORT`)
- **Start command**: `python main.py`

### Docker

```bash
docker build -t telegram-bot-notion .
docker run -d --env-file .env -p 8080:8080 telegram-bot-notion
```

### Variables de Entorno Requeridas

| Variable | Descripción |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram |
| `TELEGRAM_USER_ID` | ID del usuario autorizado |
| `NOTION_API` | Token de integración de Notion |
| `NOTION_DATABASE_ID` | ID de la base de datos de tareas |
| `NOTION_USER_ID` | ID de usuario de Notion |
| `GEMINI_API_KEY` | API Key de Google Gemini |
| `AI_MODEL` | Modelo de Gemini a usar |
| `PORT` | Puerto del health check (default: 8080) |

---

## Estructura de Componentes

| Archivo | Función | Problema |
|---------|---------|----------|
| `main.py` | Entry point del bot + health check `/health` | - |
| `controllers/handlers.py` | ConversationHandler de Telegram | Manejo de estados |
| `controllers/conversationController.py` | Lógica del flujo de conversación | Flujo de pasos |
| `utils/config.py` | Carga de variables de entorno | Configuración |
| `utils/notionutils.py` | Creación de tareas en Notion | **Problemas con Notion** |
| `utils/aiutils.py` | Procesamiento de archivos con Gemini | **Problemas de IA** |

---

## Test

### Comando

```bash
pytest
```

### Tests

- **Ubicación**: `tests/test_ai_file.py`
- **Framework**: pytest con pytest-asyncio
- **Tests disponibles**:
  - `test_generate_task_from_pdf()` - Procesa PDF con IA
  - `test_generate_task_from_docx()` - Procesa DOCX con IA (comentado)

### Archivos requeridos para tests

Los tests requieren archivos locales en la raíz del proyecto:
- `TP 2.docx`
- `Enunciado TPn°7.pdf`

---

## Health Check

- **Endpoint**: `GET /health` o `GET /`
- **Puerto**: 8080 (o el configurado en `PORT`)
- **Respuesta**: `OK`

---

## Exclusiones

Carpetas y archivos a excluir:
- `env/` - Entorno virtual
- `session/` - Sesiones de Opencode
- `tests/` - Tests
- `__pycache__/` - Cache de Python
- `.pytest_cache/` - Cache de pytest

---

## Reglas de Contribución

- **Cambios grandes**: Si resolver un error requiere cambiar más de 5 líneas de código consecutivas en un bloque, primero se debe reportar al usuario antes de llevar a cabo dicho cambio. Esperar confirmación antes de proceder.
- **Seguridad**: Cada vez que el agente agregue una contribución debe indicar los posibles riesgos de seguridad que puede tener dicha implementación.

---

## Stack Tecnológico

- **Python**: 3.10+
- **python-telegram-bot**: 22.7
- **Notion API**: notion-client, notion-markdown
- **Google Gemini**: google-genai
- **Docker**: python:3.12-slim