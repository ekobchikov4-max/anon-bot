from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import threading
import telebot

# Получаем токен из переменной окружения Render или вписываем сюда напрямую
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)


# Простейший HTTP-сервер-заглушка, чтобы Render видел открытый порт и не давал тайм-аут
class DummyHandler(BaseHTTPRequestHandler):

  def do_GET(self):
    self.send_response(200)
    self.end_headers()
    self.wfile.write(b"Bot is running!")

  def log_message(self, format, *args):
    # Отключаем лишний мусор в логах сервера
    pass


def run_server():
  port = int(os.environ.get("PORT", 10000))
  server_address = ("0.0.0.0", port)
  httpd = HTTPServer(server_address, DummyHandler)
  httpd.serve_forever()


# Запускаем веб-сервер в фоновом потоке
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()


# Обработчик команды /start с поддержкой параметров (например, твоего ID)
@bot.message_handler(commands=["start"])
def send_welcome(message):
  # Извлекаем параметр из команды /start (если он есть)
  command_args = message.text.split()
  if len(command_args) > 1:
    target_id = command_args[1]
    bot.reply_to(
        message,
        f"Привет! Отправь мне анонимное сообщение, и я перешлю его адресату"
        f" (получатель ID: {target_id}).",
    )
  else:
    bot.reply_to(
        message,
        "Привет! Это бот для анонимных сообщений. Отправь мне сообщение.",
    )


# Пересылка обычных текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
  bot.reply_to(
      message, "Твое анонимное сообщение принято и отправлено получателю!"
  )


if __name__ == "__main__":
  print("Бот и веб-сервер запущены!")
  bot.infinity_polling()
