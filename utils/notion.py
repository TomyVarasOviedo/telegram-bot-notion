from datetime import date
import re

from notion_client import AsyncClient

from utils.config import NOTION_API, NOTION_DATABASE_ID, NOTION_USER_ID, NOTION_PROPS


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
            properties={
                NOTION_PROPS["title"]: {
                    "title": [{"type": "text", "text": {"content": task.titulo}}]
                },
                NOTION_PROPS["due_date"]: {"date": {"start": task.plazo.isoformat()}},
                NOTION_PROPS["subject"]: {"select": {"name": task.materia}},
                NOTION_PROPS["task_type"]: {"select": {"name": task.tipo}},
                NOTION_PROPS["priority"]: {"select": {"name": task.prioridad}},
                NOTION_PROPS["status"]: {"select": {"name": "Empezar"}},
                "Responsable": {
                    "people": [
                        {
                            "object": "user",
                            "id": str(NOTION_USER_ID),
                        },
                    ]
                },
            },
            children=self._parse_checklist_to_blocks(task.contenido),
        )
        return page.get("url", "https://www.notion.so/")

    def get_materias(self):
        # Aquí puedes agregar la lógica para obtener las materias desde Notion utilizando su API
        pass

    def get_tipos(self):
        # Aquí puedes agregar la lógica para obtener los tipos de tareas desde Notion utilizando su API
        pass


async def main():
    notion = NotionController(api_key=str(NOTION_API), id_database=str(NOTION_DATABASE_ID))
    task = NotionTask(
        "Tarea de prueba",
        date(2024, 6, 30),
        "Sistemas distribuidos",
        "Trabajo práctico",
        "Media",
        "- [ ] Subir el trabajo a la plataforma\n- [x] Revisar el material de estudio",
    )
    url = await notion.create_task(task)
    print(f"Tarea creada en Notion: {url}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
