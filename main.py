from telegram.ext import ApplicationBuilder
from controllers.conversationController import conv_handler

TOKEN = ""


def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
