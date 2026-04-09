from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

TITULO, PLAZO, MATERIA, TIPO, PRIORIDAD, ERROR, EXITO = range(7)
filter_text = filters.TEXT & ~filters.COMMAND


class ConversationController:
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("""** CREAR TAREA DE NOTION** \n\nPor favor, ingresa el título de la tarea:""")
        return TITULO

    @staticmethod


conv_handler = ConversationHandler(
    entry_points=[CommandHandler("newtask", ConversationController.start)],
    states={
        MENU: [CallbackQueryHandler(ConversationController.button_callback)],
    },
    fallbacks=[CommandHandler("start", ConversationController.start)],
)
