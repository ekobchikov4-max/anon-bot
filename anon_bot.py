import telebot
from telebot import types

# Вставь токен своего бота от @BotFather
TOKEN = "9095726586:AAFHFMRVu5pfEkDGpeA5KRVtZHLHZPnlhyQ"
# Вставь СВОЙ цифровой Telegram ID
ADMIN_ID = 8490943503

bot = telebot.TeleBot(TOKEN)
BOT_USERNAME = bot.get_me().username

# Словарь для активных диалогов
waiting_for_reply = {}


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    # Генерируем ссылку для конкретного пользователя
    user_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"

    if user_id == ADMIN_ID:
        # Специфичное приветствие для тебя с ТВОЕЙ ссылкой сверху
        admin_start_text = (
            "👑 **Привет, хозяин! Бот запущен и работает.**\n\n"
            f"🔗 **Твоя персональная ссылка для профиля:**\n`{user_link}`\n\n"
            "📥 Жду сообщения от пользователей..."
        )
        bot.send_message(user_id, admin_start_text, parse_mode="Markdown")
        return

    # Приветствие для обычного пользователя
    welcome_text = (
        "👋 Привет! Это бот для анонимных сообщений.\n\n"
        "✍️ **Просто напиши мне сообщение следующим текстом**, и оно будет отправлено владельцу бота анонимно.\n\n"
        f"🔗 *Хочешь такую же штуку себе в профиль? Вот твоя персональная ссылка:*\n`{user_link}`"
    )
    bot.send_message(user_id, welcome_text, parse_mode="Markdown")


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id

    # --- СЦЕНАРИЙ 1: Ты отвечаешь пользователю ---
    if user_id == ADMIN_ID:
        if ADMIN_ID in waiting_for_reply:
            target_user_id = waiting_for_reply[ADMIN_ID]

            markup = types.InlineKeyboardMarkup()
            btn_reply = types.InlineKeyboardButton("💬 Ответить", callback_data="user_reply_back")
            markup.add(btn_reply)

            try:
                bot.send_message(
                    target_user_id,
                    f"📩 **Новое сообщение:**\n\n{message.text}",
                    parse_mode="Markdown",
                    reply_markup=markup
                )
                bot.send_message(ADMIN_ID, "✅ Ответ отправлен!")
            except Exception as e:
                bot.send_message(ADMIN_ID, f"❌ Ошибка отправки: {e}")

            del waiting_for_reply[ADMIN_ID]
        else:
            bot.send_message(ADMIN_ID, "⚠️ Нажми кнопку «💬 Ответить» под сообщением конкретного пользователя.")
        return

    # --- СЦЕНАРИЙ 2: Пользователь пишет тебе ---
    user = message.from_user
    username = f"@{user.username}" if user.username else "нет юзернейма"
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()

    admin_text = (
        "📥 **Новое сообщение!**\n\n"
        f"💬 **Текст:** {message.text}\n\n"
        f"👤 *Отправитель:*\n"
        f"• Имя: {full_name}\n"
        f"• Юзернейм: {username}\n"
        f"• ID: `{user_id}`"
    )

    markup = types.InlineKeyboardMarkup()
    btn_reply = types.InlineKeyboardButton("💬 Ответить", callback_data=f"reply_{user_id}")
    markup.add(btn_reply)

    user_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"

    try:
        # Шлем тебе
        bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown", reply_markup=markup)

        # Пользователю шлем подтверждение и ЕГО личную ссылку
        reply_confirmation = (
            "✅ **Сообщение успешно отправлено!**\n\n"
            f"🔗 А вот твоя ссылка, можешь кинуть её в профиль:\n`{user_link}`"
        )
        bot.send_message(user_id, reply_confirmation, parse_mode="Markdown")
    except Exception as e:
        print(f"Ошибка: {e}")


# Обработка твоей кнопки «Ответить»
@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_"))
def callback_admin_reply(call):
    if call.from_user.id != ADMIN_ID:
        return

    target_user_id = int(call.data.split("_")[1])
    waiting_for_reply[ADMIN_ID] = target_user_id

    bot.answer_callback_query(call.id)
    bot.send_message(ADMIN_ID, "✍️ Напиши текст ответа следующим сообщением:")


# Обработка кнопки «Ответить» от пользователя
@bot.callback_query_handler(func=lambda call: call.data == "user_reply_back")
def callback_user_reply(call):
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.from_user.id,
        "✍️ Напиши свой ответ следующим сообщением:"
    )


if __name__ == "__main__":
    print("[+] Бот запущен и ждет сообщения...")
    bot.infinity_polling()