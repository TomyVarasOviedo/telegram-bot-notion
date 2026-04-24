from datetime import date
import re
import requests
import json

from notion_client import AsyncClient
from notion_markdown import to_notion

from utils.config import NOTION_USER_ID, NOTION_PROPS, NOTION_API, NOTION_DATABASE_ID

headers: dict = {
    "Authorization":f"Bearer {NOTION_API}",
    "Notion-Version": "2022-06-28"
}
def convert_materias(response:list) -> list[list[str]]:
    materias: list[list[str]] = []
    for _ in response:
        if len(response) > 2:
            materias.append(
                [
                    response.pop()["name"],
                    response.pop()["name"],
                    response.pop()["name"]
                ]
            )
        elif len(response) == 2:
            materias.append(
                [
                    response.pop()["name"],
                    response.pop()["name"]
                ]
            )
        else:
            materias.append(
                [
                    response.pop()["name"]
                ]
            )
    return materias


class NotionTask:
    def __init__(
        self,
        titulo: str,
        plazo: date,
        materia: str,
        tipo: str,
        prioridad: str,
        contenido: str,
    ) -> None:
        self.titulo = titulo
        self.plazo = plazo
        self.materia = materia
        self.tipo = tipo
        self.prioridad = prioridad
        self.contenido = contenido

    def __str__(self) -> str:
        return f"Titulo: {self.titulo}\nPlazo: {self.plazo}\nMateria: {self.materia}\nTipo: {self.tipo}\nPrioridad: {self.prioridad}"


class NotionController:
    def __init__(self, api_key: str, id_database: str) -> None:
        self.api_key = api_key
        self.id_database = id_database
        self.client = AsyncClient(auth=self.api_key)
        self.database = None
        response = requests.get(f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}", headers=headers).json()
        self.materias = convert_materias(response["properties"]["Materia"]["select"]["options"])

    def _parse_checklist_to_blocks(self, description: str) -> list[dict]:
        blocks = []
        lines = description.strip().splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue

            match = re.match(r"^-\s+\[([ xX])\]\s+(.+)$", line)
            if match:
                checked = match.group(1).lower() == "x"
                content = match.group(2)
                blocks.append(
                    {
                        "object": "block",
                        "type": "to_do",
                        "to_do": {
                            "rich_text": [
                                {"type": "text", "text": {"content": content}}
                            ],
                            "checked": checked,
                        },
                    }
                )
            else:
                blocks.append(
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": line}}],
                        },
                    }
                )
        return (
            blocks
            if blocks
            else [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": description}}
                        ],
                    },
                }
            ]
        )

    async def create_task(self, task: NotionTask):
        page = await self.client.pages.create(
            parent={"database_id": self.id_database},
            icon={
                "type": "icon",
                "icon": {"name": "checkmark", "color": "green"},
            },
            properties={
                NOTION_PROPS["title"]: {
                    "title": [{"type": "text", "text": {"content": task.titulo}}]
                },
                NOTION_PROPS["due_date"]: {"date": {"start": task.plazo.isoformat()}},
                NOTION_PROPS["subject"]: {"select": {"name": task.materia}},
                NOTION_PROPS["task_type"]: {"multi_select": [{"name": task.tipo}]},
                NOTION_PROPS["priority"]: {"select": {"name": task.prioridad}},
                NOTION_PROPS["status"]: {"status": {"name": "Empezar"}},
                "Responsable": {
                    "people": [
                        {
                            "object": "user",
                            "id": str(NOTION_USER_ID),
                        },
                    ]
                },
            },
            children=to_notion(task.contenido),
        )
        return page.get("url", "https://www.notion.so/")

    async def get_materias(self):
        return self.materias

    def get_tipos(self):
        # Aquí puedes agregar la lógica para obtener los tipos de tareas desde Notion utilizando su API
        pass


""" async def main():
    notion = NotionController(
        api_key=str(NOTION_API), id_database=str(NOTION_DATABASE_ID)
    )
    task = NotionTask(
        "Tarea de prueba",
        date(2026, 4, 24),
        "Sistemas distribuidos",
        "Trabajo practico",
        "Medio",
        "# Hacer algo para tal\n## Hacer algo mas chico\n- [ ] Subir el trabajo a la plataforma\n- [x] Revisar el material de estudio",
    )
    print(NOTION_DATABASE_ID)
    url = await notion.create_task(task)
    print(f"Tarea creada en Notion: {url}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main()) """
