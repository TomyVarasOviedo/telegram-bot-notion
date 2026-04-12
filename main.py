
from telegram.ext import ApplicationBuilder
from utils.config import TELEGRAM_BOT_TOKEN, NOTION_API, NOTION_DATABASE_ID
from controllers.handlers import create_conv_handler
from utils.notionutils import NotionController


def main():
    #------Controlador de Notion ---------#
    notion = NotionController(api_key=str(NOTION_API), id_database=str(NOTION_DATABASE_ID))

    #-------Controlador de Telegram ------#
    conv_handler = create_conv_handler(notion=notion)

    #--------LANZADOR DE TELEGRAM--------#
    application = ApplicationBuilder().token(str(TELEGRAM_BOT_TOKEN)).build()
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
