from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from telegram_bot_calendar import WMonthTelegramCalendar, LSTEP
from datetime import datetime
from utils.config import TELEGRAM_USER_ID, TIPOS_TAREAS, PRIORIDADES
from utils.notionutils import NotionController, NotionTask


(
    TITULO,
    PLAZO,
    MATERIA,
    TIPO,
    PRIORIDAD,
    DESCRIPCION,
    CONFIRM,
    ERROR,
    EXITO,
) = range(9)
filter_text = filters.TEXT & ~filters.COMMAND


async def show_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra un resumen de los datos antes de confirmar la creación en Notion."""
    d = context.user_data

    texto = (
        f"📋 *Resumen de la tarea:*\n\n"
        f"📌 *Título:* {d['title']}\n"
        f"🏷 *Tipo:* {d['task_type']}\n"
        f"📅 *Entrega:* {d['due_date']}\n"
        f"📚 *Materia:* {d['subject']}\n\n"
        f"📝 *Descripción/Checklist:*\n{d['description']}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Enviá /confirmar para crear en Notion 🚀\n"
        "o /cancelar para descartar."
    )
    await update.message.reply_text(texto, parse_mode="Markdown")


class ConversationController:
    def __init__(self, notion_controller: NotionController):
        self.notion = notion_controller
        # Add iacontroller here when implemented

    async def start_new_tarea(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text(
            "¡Hola,! 📚 Creemos una nueva tarea en Notion.\n\n"
            "¿Cuál es el *título* de la tarea?",
            parse_mode="Markdown",
        )
        return TITULO

     
    async def receive_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text(
            """** CREAR TAREA DE NOTION** \n\nPor favor, ingresa el título de la tarea:"""
        )
        return TITULO

     
    async def receive_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["title"] = update.message.text.strip()
        keyboard = ReplyKeyboardMarkup(
            TIPOS_TAREAS, one_time_keyboard=True, resize_keyboard=True
        )
        await update.message.reply_text(
            "¿Que *tipo* de tarea es?", reply_markup=keyboard, parse_mode="Markdown"
        )
        return TIPO

     
    async def receive_task_type(self,
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        context.user_data["task_type"] = update.message.text.strip()

        calendar, step = WMonthTelegramCalendar(current_date=datetime.now().date()).build()

        await update.message.reply_text(
            f"📅 Selecciona {LSTEP[step]}",
            reply_markup=calendar
        )
        return PLAZO
    
    async def receive_calendar(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        result, key, step = WMonthTelegramCalendar().process(update.callback_query.data)
    
        if key:
            # El usuario sigue navegando (año/mes/día)
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(
                f"Seleccioná {LSTEP[step]}:",
                reply_markup=key,
            )
            return PLAZO
    
        if result:
            # Fecha seleccionada
            context.user_data["due_date"] = result
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(f"📅 Fecha seleccionada: {result.strftime('%d/%m/%Y')}")
        
            # Continuar al siguiente paso (materia)
            materias = await self.notion.get_materias()
            keyboard = ReplyKeyboardMarkup(materias, one_time_keyboard=True, resize_keyboard=True)
            await update.callback_query.message.reply_text(
                "¿De qué *materia* es la tarea?", reply_markup=keyboard, parse_mode="Markdown"
            )
            return MATERIA
    
        return PLAZO
     
    async def receive_subject(self, 
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        context.user_data["subject"] = update.message.text.strip()
        keyboard = ReplyKeyboardMarkup(
            PRIORIDADES, one_time_keyboard=True, resize_keyboard=True
        )
        await update.message.reply_text(
            "¿Cuál es la *prioridad* de la tarea?",
            reply_markup=keyboard,
            parse_mode="Markdown",
        )

        return PRIORIDAD

     
    async def receive_priority(self, 
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        context.user_data["priority"] = update.message.text.strip()
        await update.message.reply_text(
            "¿Quieres agregar una *descripción* a la tarea? (opcional)\nSi no deseas agregar una descripción, simplemente responde con 'No'.",
            parse_mode="Markdown",
        )
        return DESCRIPCION

     
    async def receive_description(self,
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        msg = update.message

        if msg.document or msg.photo:
            # ── Procesamiento de archivo con IA ──────────────────────────────────
            status = await msg.reply_text("⏳ Procesando archivo con IA...")

            try:
                if msg.document is not None:
                    tg_file = await msg.document.get_file()
                    filename = msg.document.file_name or "archivo"
                    mime = msg.document.mime_type or "application/octet-stream"
                else:
                    # Para fotos, toma la mayor resolución disponible
                    tg_file = await msg.photo[-1].get_file()
                    filename = "imagen.jpg"
                    mime = "image/jpeg"

                # Descarga el archivo como bytes (sin persistirlo en disco)
                file_bytes = bytes(await tg_file.download_as_bytearray())

                # checklist = await generate_checklist_from_file(
                #    file_bytes=file_bytes,
                #    filename=filename,
                #    mime_type=mime,
                #    task_data=context.user_data,
                # )
                #context.user_data["description"] = checklist
                await status.edit_text("✅ Descripción generada por IA.")

            except Exception as exc:
                # logger.error(f"Error en AI handler: {exc}", exc_info=True)
                await status.edit_text(
                    "❌ No pude procesar el archivo. Escribí la descripción manualmente."
                )
                return DESCRIPCION

        elif msg.text:
            # ── Descripción manual ────────────────────────────────────────────────
            context.user_data["description"] = msg.text.strip()

        else:
            await msg.reply_text("Por favor enviá un archivo o escribí la descripción.")
            return DESCRIPCION

        await show_summary(update, context)
        return CONFIRM

     
    async def cmd_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Crea la página en Notion con todos los datos recopilados."""
        await update.message.reply_text("⏳ Creando tarea en Notion...")

        try:
            task = NotionTask(
                titulo=context.user_data["title"],
                plazo=context.user_data["due_date"],
                tipo=context.user_data["task_type"],
                prioridad=context.user_data["priority"],
                contenido=context.user_data["description"],
                materia=context.user_data["subject"]
            )
            notion_url = await self.notion.create_task(task)
            await update.message.reply_text(
                "✅ ¡Tarea creada! 🎉\n[Ver en Notion]\n"
                "Enviá /nueva para agregar otra.",
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )
        except Exception as exc:
            # logger.error(f"Error creando tarea en Notion: {exc}", exc_info=True)
            print(exc)
            await update.message.reply_text(
                "❌ Error al crear la tarea. Revisá los logs o intentá de nuevo."
            )

        context.user_data.clear()
        return ConversationHandler.END

     
    async def cmd_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancela el flujo y limpia todos los datos de la sesión del usuario."""
        context.user_data.clear()
        await update.message.reply_text(
            "❌ Operación cancelada. Enviá /nueva para empezar de nuevo.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END



