from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from telegram_bot_calendar import WMonthTelegramCalendar
from functools import partial

from utils.notionutils import NotionController
from utils.aiutils import IAController
from controllers.conversationController import ConversationController


filter_text = filters.TEXT & ~filters.COMMAND
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

def create_conv_handler(notion: NotionController, ai: IAController):
    controller = ConversationController(notion_controller=notion, ai_controller=ai)
    return ConversationHandler(
            entry_points=[CommandHandler("newtask", partial(controller.start_new_tarea))],
            states={
                TITULO: [MessageHandler(filter_text, partial(controller.receive_title))],
                TIPO: [MessageHandler(filter_text, partial(controller.receive_task_type))],
                PLAZO: [
                    CallbackQueryHandler(
                        partial(controller.receive_calendar),
                        pattern=lambda call_data: call_data and call_data.startswith("cbcal")
                    ),
                ],
                MATERIA: [MessageHandler(filter_text, partial(controller.receive_subject))],
                PRIORIDAD: [
                    MessageHandler(filter_text, partial(controller.receive_priority))
                ],
                DESCRIPCION: [
                    MessageHandler(
                        filters.Document.ALL | filters.PHOTO,
                        partial(controller.receive_description),
                    ),
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        partial(controller.receive_description),
                    ),
                ],
                CONFIRM: [
                    CommandHandler("confirmar", partial(controller.cmd_confirm)),
                    CommandHandler("cancelar", partial(controller.cmd_cancel)),
                ],
            },
            fallbacks=[CommandHandler("cancelar", partial(controller.cmd_cancel))],
            allow_reentry=True,
        )