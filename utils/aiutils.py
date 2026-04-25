import time

from google import genai
from google.genai import types
from utils.config import GEMINI_API_KEY, AI_MODEL
import tempfile
import os

TIPO_PERMITIDOS_ARCHIVOS = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/heic",
}

class IAController:
    def __init__(self, api_key:str, ai_model:str):
        self.api_key = api_key
        self.ai_model = ai_model
        self.client = genai.Client(api_key=self.api_key)
    
    def generate_prompt(self, task:dict) -> str:
        return (
            "Eres un asistente academico, encargado de ayudar con la identificacion de tareas "
            f"para la materia \"{task.get('subject', 'Desconocida')}\" "
            f"(Es una tarea del tipo \"{task.get('task_type', 'Desconocida')}\"). \n\n"
            "Genera una lista de verificacion con todos los puntos, requisitos y entregables que el alumno debe completar."
            "Usa EXACTAMENTE este formato para cada item:\n"
            "- # Para titulos o secciones"
            "- [ ] Descripcion del punto a completar \n\n"
            "Reglas: \n"
            "- Se conciso y claro\n"
            "- Maximo 12 items\n"
            "- Solo devuelve la lista junto con las secciones para la mejor compresion y discriminacion de las tareas por secciones, sin encabezados ni texto adicional\n"
            "- Si el documento no tiene requisitos claros, infiere los pasos logicos"
            "- TODAS las respuestas debe ser en formato Markdown, SIEMPRE"
        )
    async def extract_text_from_docx(self, file_bytes:str) -> str:
        try:
            import docx
            import io
            doc = docx.Document(io.BytesIO(file_bytes))
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except ImportError:
            raise RuntimeError ("python-docx no esta instalado")
    async def generate_prompt_test(self):
        try:
            response = self.client.models.generate_content(
                contents=["Estas vivo y bien? Dame una sola palabra nada"],
                model=self.ai_model
            )
            respuesta = response.text.strip()
            print(respuesta)
            return respuesta
        except Exception as e:
            return f"[Error] -> {e}"
        
    async def generate_task_from_file(self, file_bytes:bytes, filename:str, mime_type:str, task:dict) -> str:
        if mime_type not in TIPO_PERMITIDOS_ARCHIVOS:
            if "word" in mime_type or filename.endswith((".docx", ".doc")):
                try:
                    text_content = await self.extract_text_from_docx(file_bytes)
                    prompt = self.generate_prompt(task) + f"\n\nCONTENIDO DEL ARCHIVO:\n{text_content}"
                    response = self.client.models.generate_content(
                        model=self.ai_model,
                        contents=[prompt]
                    )
                    return "# Descripcion de la tarea\n"+response.text.strip()
                except Exception as e:
                    return "❌ No se pudo procesar el archivo Word. Intentá con PDF o imagen."
            else:
                return (
                    f"⚠️ Formato '{mime_type}' no soportado. "
                    "Enviá el archivo como PDF o imagen (JPG/PNG)."
                )
        name_parts = filename.rsplit(".", 1)
        safe_filename = "".join(c if c.isalnum() or c in "-_" else "_" for c in name_parts[0])
        if len(name_parts) > 1:
            safe_filename += "." + name_parts[1]
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=f"_{safe_filename}",
            mode="wb"
        ) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        try:
            upload_file = self.client.files.upload(file=tmp_path)
            while upload_file.state == "PROCESSING":
                # Verificar subida de archivo
                time.sleep(2)
                upload_file = self.client.files.get(name=upload_file.name)
            if upload_file.state == "FAILED":
                return "❌ Error al procesar el archivo PDF"
            
            response = self.client.models.generate_content(
                contents=[upload_file, self.generate_prompt(task)], 
                model=self.ai_model
                )
            return "# Descripcion de la tarea\n"+response.text.strip()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
async def main():
    gemini = IAController(GEMINI_API_KEY, AI_MODEL)
    respuesta = await gemini.generate_prompt_test()
    print(respuesta)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
    
