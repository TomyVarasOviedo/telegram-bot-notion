# Telegram Bot for Notion Task Management

Bot de Telegram que permite crear tareas en Notion mediante una conversación guiada, con soporte para fechas límite, prioridades, materias, descripciones y archivos.

## Características

- Crear tareas en Notion via comando `/newtask`
- Flujo de conversación guiado paso a paso
- Selector de fecha con calendario interactivo
- Soporte para fotos y documentos en la descripción
- Integración con Gemini AI para procesamiento inteligente de PDFs, imágenes y DOCX
- Extracción automática de requisitos y lista de verificación de tareas académicas
- Health check endpoint (`/health`)
- Soporte para Docker

## Stack Tecnológico

- **Python 3.10+**
- [python-telegram-bot](https://python-telegram-bot.org/) - Cliente de Telegram
- [Notion API](https://www.notion.so/es-es/api) - Base de datos de tareas
- [Google Gemini](https://gemini.google.com/) - Procesamiento con IA
- [Docker](https://www.docker.com/) - Contenedorización

## Estructura del Proyecto

```
telegram-bot-notion/
├── main.py                         # Punto de entrada del bot
├── controllers/
│   ├── handlers.py                 # Handlers de conversación de Telegram
│   └── conversationController.py   # Lógica del flujo de conversación
├── utils/
│   ├── config.py                   # Configuración y variables de entorno
│   ├── notion.py                   # Cliente de Notion
│   ├── notionutils.py              # Utilidades de Notion
│   └── aiutils.py                  # Utilidades de IA (Gemini)
├── requirements.txt                # Dependencias Python
├── Dockerfile                      # Imagen Docker
└── .env.example                    # Ejemplo de variables de entorno
```

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                      Usuario de Telegram                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Telegram Bot (main.py)                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │            ConversationHandler (handlers.py)        │    │
│  │  Estado: Título → Tipo → Plazo → Materia →          │    │
│  │  Prioridad → Descripción → Confirmación             │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐       ┌─────────────────────────┐
│  NotionController       │       │    IAController         │
│  (notionutils.py)       │       │    (aiutils.py)         │
│                         │       │                         │
│  • Crear páginas        │       │  • Procesamiento de     │
│  • Propiedades          │       │    PDFs, imágenes y     │
│  • Archivos             │       │    DOCX                 │
│                         │       │  • Extracción de        │
│                         │       │    requisitos           │
│                         │       │  • Listas de            │
│                         │       │    verificación         │
└─────────────────────────┘       └─────────────────────────┘
              │                               │
              └───────────────┬───────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Notion API                             │
└─────────────────────────────────────────────────────────────┘
```

## Instalación

### Requisitos Previos

- Python 3.10 o superior
- Token de bot de Telegram
- API Key de Notion
- API Key de Google Gemini (opcional)

### Pasos

1. Clonar el repositorio:
```bash
git clone <repositorio>
cd telegram-bot-notion
```

2. Crear entorno virtual e instalar dependencias:
```bash
python -m venv env
source env/bin/activate  # Linux/Mac
# env\Scripts\activate   # Windows
pip install -r requirements.txt
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

4. Ejecutar el bot:
```bash
python main.py
```

## Variables de Entorno

| Variable | Descripción |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram |
| `TELEGRAM_USER_ID` | ID del usuario autorizado |
| `NOTION_API` | Token de integración de Notion |
| `NOTION_DATABASE_ID` | ID de la base de datos de tareas |
| `NOTION_USER_ID` | ID de usuario de Notion |
| `GEMINI_API_KEY` | API Key de Google Gemini |
| `AI_MODEL` | Modelo de Gemini a usar |

## Configuración de Notion

1. Crear una integración en [Notion Developers](https://www.notion.so/my-integrations)
2. Compartir la base de datos con la integración
3. Obtener el `NOTION_DATABASE_ID` de la URL de la base de datos
4. Configurar las siguientes propiedades en la base de datos:
   - Nombre de la tarea (title)
   - Tipo de tarea (select)
   - Estado (select)
   - Plazo (date)
   - Prioridad (select)
   - Materia (select)

## Funciones de IA

El bot utiliza Google Gemini para procesar archivos y generar descripciones inteligentes de tareas académicas:

| Función | Descripción |
|---------|------------|
| `generate_task_from_file()` | Procesa PDFs, imágenes y DOCX para extraer lista de requisitos y puntos a completar |

### Tipos de Archivos Soportados

| Tipo | Extensiones |
|------|-------------|
| PDF | `.pdf` |
| Imágenes | `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.heic` |
| Word | `.docx` |

### Ejemplo de Uso

Al enviar un PDF de enunciado de tarea, la IA analiza el documento y genera una lista de verificación con todos los requisitos, entregables y pasos a seguir.

## Uso

### Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `/newtask` | Iniciar flujo de creación de tarea |
| `/confirmar` | Confirmar y guardar la tarea |
| `/cancelar` | Cancelar el proceso actual |

### Flujo de Creación de Tarea

1. Envía `/newtask` al bot
2. Ingresa el **título** de la tarea
3. Selecciona el **tipo** de tarea (Trabajo Práctico, Examen, etc.)
4. Selecciona la **fecha límite** usando el calendario
5. Ingresa la **materia** o área
6. Selecciona la **prioridad** (Alta, Media, Baja)
7. Agrega una **descripción** (texto, foto o documento)
8. Confirma con `/confirmar` o cancela con `/cancelar`

## Docker

### Build

```bash
docker build -t telegram-bot-notion .
```

### Run

```bash
docker run -d \
  --name telegram-bot-notion \
  --env-file .env \
  telegram-bot-notion
```

### Docker Compose

```yaml
version: '3.8'

services:
  bot:
    build: .
    restart: unless-stopped
    env_file:
      - .env
    ports:
      - "8080:8080"
```

## Health Check

El bot expone un endpoint de health check en el puerto configurado (default 8080):

```bash
curl http://localhost:8080/health
```

Respuesta esperada: `OK`

## Licencia

Copyright (C) 2026

Este programa es software libre: puede redistribuirlo y/o modificarlo
bajo los términos de la Licencia Pública General GNU publicada por
la Free Software Foundation, ya sea la versión 3 de la Licencia, o
(cualquier versión posterior) a su elección.

Este programa se distribuye con la esperanza de que sea útil,
pero SIN NINGUNA GARANTÍA; sin siquiera la garantía implícita de
COMERCIABILIDAD o ADECUACIÓN PARA UN PROPÓSITO PARTICULAR. Ver la
Licencia Pública General GNU para más detalles.

Debería haber recibido una copia de la Licencia Pública General GNU
junto con este programa. Si no la ha recibido, visite <https://www.gnu.org/licenses/>.
