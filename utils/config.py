import os
from dotenv import load_dotenv

load_dotenv()

# configuraciones de telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")
# configuraciones de Notion
NOTION_API = os.getenv("NOTION_API")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
NOTION_USER_ID = os.getenv("NOTION_USER_ID")
# configuraciones de Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AI_MODEL = os.getenv("AI_MODEL")

TIPOS_TAREAS: list[list[str]] = [
    ["Trabajo Practico", "Examen Parcial"],
    ["Examen Final", "Resumen"],
    ["Practica", "Presentación"],
    ["Planificacion"],
]
PRIORIDADES: list[list[str]] = [["Alta", "Medio"], ["Baja"]]

NOTION_PROPS: dict[str, str] = {
    "title": "Nombre de la tarea",
    "task_type": "Tipo de tarea",
    "status": "Estado",
    "due_date": "Plazo",
    "priority": "Prioridad",
    "subject": "Materia",
}
