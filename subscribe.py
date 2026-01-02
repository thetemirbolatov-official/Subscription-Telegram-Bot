import telebot
from telebot import types

# --- НАСТРОЙКИ ---

# Вставь сюда НОВЫЙ токен от BotFather
TOKEN = 'you token'

# Список каналов для проверки.
# Можно использовать @username или ID (например, -100123456789).
# ВАЖНО: Бот должен быть АДМИНИСТРАТОРОМ в этих каналах!
CHANNELS = [
    "@miraje_age_age",       # Пример 1 (замени на свой)
    # "@telegram",  # Пример 2
]

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def check_subscription(user_id):
    """
    Проверяет подписку пользователя на все каналы из списка CHANNELS.
    Возвращает True, если подписан на все, иначе False.
    """
    for channel in CHANNELS:
        try:
            chat_member = bot.get_chat_member(chat_id=channel, user_id=user_id)
            # Статусы, при которых пользователь считается подписанным
            if chat_member.status not in ['member', 'administrator', 'creator']:
                return False
        except Exception as e:
            print(f"Ошибка проверки канала {channel}: {e}")
            # Если бот не админ или канала не существует, считаем, что подписки нет
            return False
    return True

def main_menu_keyboard():
    """Клавиатура главного меню (появляется после успешной проверки)"""
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="🎁 Получить поздравление", callback_data="get_congrats")
    markup.add(btn)
    return markup

def subscription_keyboard():
    """Клавиатура с кнопками подписки и кнопкой проверки"""
    markup = types.InlineKeyboardMarkup()
    
    # Генерируем кнопки для каждого канала
    for channel in CHANNELS:
        # Формируем ссылку. Если ID, ссылку нужно знать заранее, если @username - формируем автоматически
        if isinstance(channel, str) and channel.startswith("@"):
            url = f"https://t.me/{channel.replace('@', '')}"
            btn = types.InlineKeyboardButton(text=f"Подписаться на канал", url=url)
            markup.add(btn)
    
    # Кнопка проверки
    btn_check = types.InlineKeyboardButton(text="✅ Я подписался", callback_data="check_sub")
    markup.add(btn_check)
    return markup

# --- ОБРАБОТЧИКИ СООБЩЕНИЙ ---

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    
    if check_subscription(user_id):
        bot.send_message(
            message.chat.id, 
            "Добро пожаловать! Вы успешно авторизованы.",
            reply_markup=main_menu_keyboard()
        )
    else:
        bot.send_message(
            message.chat.id,
            "👋 Привет! Для доступа к боту необходимо подписаться на наши каналы:",
            reply_markup=subscription_keyboard()
        )

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    
    # Если нажали кнопку "Я подписался"
    if call.data == "check_sub":
        if check_subscription(user_id):
            # Удаляем сообщение с просьбой подписаться
            bot.delete_message(call.message.chat.id, call.message.message_id)
            # Отправляем меню
            bot.send_message(
                call.message.chat.id,
                "✅ Проверка пройдена! Вот ваше меню:",
                reply_markup=main_menu_keyboard()
            )
        else:
            # Показываем всплывающее уведомление
            bot.answer_callback_query(callback_query_id=call.id, text="❌ Вы подписались не на все каналы!", show_alert=True)

    # Если нажали кнопку "Получить поздравление"
    elif call.data == "get_congrats":
        # На всякий случай проверяем подписку снова (чтобы не отписались после входа)
        if check_subscription(user_id):
            bot.send_message(call.message.chat.id, "🎉 Поздравляю! Вы великолепны! 🥳")
            bot.answer_callback_query(call.id)
        else:
             bot.send_message(
                call.message.chat.id, 
                "⛔️ Кажется, вы отписались от каналов. Доступ закрыт.",
                reply_markup=subscription_keyboard()
            )

# --- ЗАПУСК ---
if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()