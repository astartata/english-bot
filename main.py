import telebot
from telebot import types
import requests

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8719479123:AAGUe43dzC-B7F17_yl6_HBJ2KjAgDebqIY"
KIE_API_KEY = "30afd64c195a54760f0a706e48790c55"

# Проверяющий + ваш ID:
ALLOWED_USERS = [328761045, 7718617445]  # Добавьте свой ID через запятую

BANNER_URL = "https://images.unsplash.com/photo-1546410531-bb4caa6b424d?w=1000&auto=format&fit=crop&q=80"

bot = telebot.TeleBot(BOT_TOKEN)

user_context = {}
user_state = {}
user_selected_slot = {}

SYSTEM_PROMPT = (
    "Ты — личный AI-помощник Анастасии Александровны, преподавателя разговорного английского языка. "
    "Твоя задача — отвечать на вопросы родителей и учеников о формате занятий, стоимости, "
    "методике и подготовке. Отвечай доброжелательно, кратко, структурированно и вежливо, "
    "подводя к записи на бесплатный пробный урок-диагностику."
)

# Главное меню
def get_main_menu():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("👩‍🏫 Обо мне кратко", callback_data="about"),
        types.InlineKeyboardButton("🤖 Задать вопрос", callback_data="ask_ai"),
        types.InlineKeyboardButton("💬 Отзывы", callback_data="reviews"),
        types.InlineKeyboardButton("📅 Свободные окошки", callback_data="slots"),
        types.InlineKeyboardButton("✨ Записаться на урок", callback_data="book")
    )
    return keyboard

# Кнопки со слотами времени
def get_slots_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("Чт, 20 августа • 15:00", callback_data="slot_Чт, 20 августа • 15:00"),
        types.InlineKeyboardButton("Пт, 21 августа • 16:00", callback_data="slot_Пт, 21 августа • 16:00"),
        types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_booking")
    )
    return keyboard

# Кнопка отмены при вводе имени
def get_cancel_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_booking"))
    return keyboard

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    user_context[user_id] = []
    user_state[user_id] = "menu"

    caption = (
        "Привет! 🌷\n\n"
        "Рада видеть вас здесь.\n\n"
        "Я — помощник Анастасии Александровны, преподавателя английского языка для детей.\n\n"
        "Здесь можно спокойно познакомиться с Анастасией Александровной, "
        "почитать отзывы родителей, посмотреть свободные окошки и выбрать удобное время для занятия.\n\n"
        "Анастасия Александровна помогает детям учить английский без страха ошибок, "
        "с интересом и в комфортной атмосфере.\n\n"
        "Она работает с дошкольниками 6–7 лет и школьниками 1–11 классов, "
        "индивидуально, в мини-группах и онлайн.\n\n"
        "Выберите, что хотите посмотреть 👇"
    )
    
    try:
        bot.send_photo(message.chat.id, BANNER_URL, caption=caption, reply_markup=get_main_menu())
    except Exception:
        bot.send_message(message.chat.id, caption, reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id

    if call.data == "about":
        text = (
            "👩‍🏫 **Обо мне кратко**\n\n"
            "Меня зовут Анастасия Александровна. Я преподаватель английского языка "
            "с высшим филологическим образованием и большим опытом работы с детьми.\n\n"
            "В своей работе я сочетаю системный подход, понятное объяснение материала "
            "и комфортную атмосферу для ребёнка.\n\n"
            "✅ Высшее филологическое образование\n"
            "✅ Опыт работы устным переводчиком\n"
            "✅ Более 16 лет преподавания детям\n"
            "✅ Регулярное участие в профессиональных конференциях по лингвистике и обучению детей\n\n"
            "Мои ученики не просто улучшают оценки — они начинают лучше понимать английский, "
            "увереннее говорить, перестают бояться ошибок и постепенно чувствуют себя свободнее в языке 🌷"
        )
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=get_main_menu())

    elif call.data == "ask_ai":
        user_state[user_id] = "ai_dialog"
        text = (
            "Здравствуйте! 🌷\n\n"
            "Я личный AI-помощник Анастасии Александровны.\n"
            "Я могу ответить на вопросы о занятиях, стоимости, формате обучения, "
            "расписании и подходе к занятиям.\n\n"
            "Напишите Ваш вопрос, и я постараюсь помочь."
        )
        bot.send_message(call.message.chat.id, text)

    elif call.data == "reviews":
        text = (
            "💬 **Отзывы родителей:**\n\n"
            "🌸 **Алина, Мама Влады:**\n"
            "«Добрый день. Полностью поддерживаю! И добавлю, что для меня было важно привить "
            "любовь к изучению английского, чтобы не казалось слишком сложным. Влада получала 4-ки, "
            "а тут четверть на 5 завершила и знания есть хорошие.»\n\n"
            "🌸 **Сильвия:**\n"
            "«Занятия были очень полезными, интересными. Ребёнок всегда вовлечён в процесс. "
            "Безусловно есть отличные результаты!»"
        )
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=get_main_menu())

    elif call.data in ["slots", "book"]:
        text = "📅 **Выберите удобное окошко:**"
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=get_slots_keyboard())

    elif call.data.startswith("slot_"):
        slot_name = call.data.replace("slot_", "")
        user_selected_slot[user_id] = slot_name
        user_state[user_id] = "waiting_for_name"
        
        text = (
            f"✨ **Вы выбрали:**\n"
            f"📅 {slot_name}\n\n"
            f"Как зовут ребёнка?"
        )
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=get_cancel_keyboard())

    elif call.data == "cancel_booking":
        user_state[user_id] = "menu"
        user_selected_slot[user_id] = None
        bot.send_message(call.message.chat.id, "Запись отменена 🌷", reply_markup=get_main_menu())

    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    user_id = message.from_user.id
    user_text = message.text

    # Если пользователь вводил имя для записи
    if user_state.get(user_id) == "waiting_for_name":
        slot = user_selected_slot.get(user_id, "выбранное время")
        user_state[user_id] = "menu"
        confirm_text = (
            f"✨ **Запись предварительно оформлена!**\n\n"
            f"👤 **Ученик:** {user_text}\n"
            f"📅 **Время:** {slot}\n\n"
            f"Анастасия Александровна свяжется с вами для подтверждения: @annie_anastasia 🌷"
        )
        bot.send_message(message.chat.id, confirm_text, parse_mode="Markdown", reply_markup=get_main_menu())
        return

    # Проверка белого списка для запросов к ИИ
    if user_id not in ALLOWED_USERS:
        bot.reply_to(message, "⚠️ Доступ к ИИ открыт только для тестирования преподавателем (ID: 328761045).")
        return

    bot.send_chat_action(message.chat.id, 'typing')

    if user_id not in user_context:
        user_context[user_id] = []

    user_context[user_id].append({"role": "user", "content": user_text})
    if len(user_context[user_id]) > 10:
        user_context[user_id] = user_context[user_id][-10:]

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + user_context[user_id]

    # Прямой запрос к Kie.ai через requests
    try:
        headers = {
            "Authorization": f"Bearer {KIE_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "messages": messages,
            "stream": False
        }
        
        # Запрос к API
        res = requests.post("https://api.kie.ai/chat/completions", headers=headers, json=payload, timeout=25)
        
        if res.status_code == 404:
            # Запасной маршрут если на сервере другой префикс
            res = requests.post("https://api.kie.ai/v1/chat/completions", headers=headers, json=payload, timeout=25)

        data = res.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            reply_text = data["choices"][0]["message"]["content"]
            user_context[user_id].append({"role": "assistant", "content": reply_text})
            bot.reply_to(message, reply_text, reply_markup=get_main_menu())
        else:
            bot.reply_to(message, f"Ответ от ИИ: {data.get('message', str(data))}")
            
    except Exception as e:
        bot.reply_to(message, f"Ошибка ИИ: {e}")

if __name__ == "__main__":
    bot.infinity_polling()
