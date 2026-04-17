from google.generativeai import GenerativeModel, upload_file as upload_file_gemini
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
        self.model = GenerativeModel(self.ai_model)
    
    def generate_prompt(task:dict) -> str:
        return (
            "Eres un asistente academico, encargado de ayudar con la identificacion de tareas "
            f"para la materia \"{task.get('subject', 'Desconocida')}\" "
            f"(Es una tarea del tipo \"{task.get('task_type', 'Desconocida')}\"). \n\n"
            "Genera una lista de verificacion con todos los puntos, requisitos y entregables que el alumno debe completar."
            "Usa EXACTAMENTE este formato para cada item:\n"
            "- [ ] Descripcion del punto a completar \n\n"
            "Reglas: \n"
            "- Se conciso y claro\n"
            "- Maximo 15 items\n"
            "- Solo devuelve la lista, sin encabezados ni texto adicional\n"
            "- Si el documento no tiene requisitos claros, infiere los pasos logicos"
        )
    def extract_text_from_docx(file_bytes:str) -> str:
        try:
            import docx
            import io
            doc = docx.Document(io.BytesIO(file_bytes))
            return "\n".join(p.tex for p in doc.paragraphs if p.text.strip())
        except ImportError:
            raise RuntimeError ("python-docx no esta instalado")
        
    async def generate_task_from_file(self, file_bytes:bytes, filename:str, mime_type:str, task:dict) -> str:
        if mime_type not in TIPO_PERMITIDOS_ARCHIVOS:
            if "word"  in mime_type or filename.endswith((".docx", ".doc")):
                try:
                    text_content = self.extract_text_from_docx(file_bytes)
                    prompt = self.generate_prompt(task) + f"\n\nCONTENIDO DEL ARCHIVO:\n{text_content}"
                    response = self.model.generate_content(prompt)
                    return response.text.strip()
                except Exception as e:
                    return "❌ No se pudo procesar el archivo Word. Intentá con PDF o imagen."
            else:
                return (
                    f"⚠️ Formato '{mime_type}' no soportado. "
                    "Enviá el archivo como PDF o imagen (JPG/PNG)."
                )
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=f"_{filename}",
            mode="wb"
        ) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        try:
            upload_file = upload_file_gemini(tmp_path, mime_type=mime_type)
            response = self.model.generate_content([upload_file, self.generate_prompt(task)])
            return response.text.strip()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

