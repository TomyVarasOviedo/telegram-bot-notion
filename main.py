import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import ApplicationBuilder
from utils.config import TELEGRAM_BOT_TOKEN, NOTION_API, NOTION_DATABASE_ID, GEMINI_API_KEY, AI_MODEL
from controllers.handlers import create_conv_handler
from utils.notionutils import NotionController
from utils.aiutils import IAController


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health" or self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def run_health_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()


def main():
    notion = NotionController(
        api_key=str(NOTION_API), id_database=str(NOTION_DATABASE_ID)
    )
    ai = IAController(api_key=str(GEMINI_API_KEY), ai_model=str(AI_MODEL))
    conv_handler = create_conv_handler(notion=notion, ai=ai)

    application = ApplicationBuilder().token(str(TELEGRAM_BOT_TOKEN)).build()
    application.add_handler(conv_handler)

    health_thread = threading.Thread(target=run_health_server, daemon=True)
    try:
        health_thread.start()
    except Exception:
        pass

    application.run_polling()


if __name__ == "__main__":
    import os

    main()
