import telebot
from telebot import types
import requests

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8719479123:AAGUe43dzC-B7F17_yl6_HBJ2KjAgDebqIY"
KIE_API_KEY = "30afd64c195a54760f0a706e48790c55"

ADMIN_USERNAME = "@astartata"

# Белый список: проверяющий (328761045) + ваш ID (7718617445)
ALLOWED_USERS = [328761045, 7718617445]

bot = telebot.TeleBot(BOT_TOKEN)

# Список доступных слотов
AVAILABLE_SLOTS = [
    "Пн, 24 августа • 17:00",
    "Ср, 26 августа • 18:30",
    "Сб, 29 августа • 11:00"
]

# Занятые слоты
booked_slots = set()

user_context = {}

SYSTEM_PROMPT = (
    "Ты — личный AI-консультант преподавателя курсов разговорного английского языка Елены Смирновой. "
    "Твоя задача — отвечать на вопросы родителей и учеников о формате занятий, стоимости (индивидуально — 1800 руб/час, "
    "мини-группы — 900 руб/час), методике и подготовке. Отвечай доброжелательно, кратко и вежливо, "
    "ненавязчиво предлагая записаться на бесплатный пробный урок-диагностику."
)

def get_main_menu():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("👩‍🏫 О преподавателе", callback_data="about"),
        types.InlineKeyboardButton("🤖 Задать вопрос ИИ", callback_data="ask_ai"),
        types.InlineKeyboardButton("💬 Отзывы учеников", callback_data="reviews"),
        types.InlineKeyboardButton("📅 Свободные окошки", callback_data="slots"),
        types.InlineKeyboardButton("✨ Записаться на пробный урок", callback_data="book")
    )
    return keyboard

def get_slots_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    free = [s for s in AVAILABLE_SLOTS if s not in booked_slots]
    
    if not free:
        keyboard.add(types.InlineKeyboardButton("🔄 Сбросить все записи", callback_data="reset_slots"))
    else:
        for slot in free:
            keyboard.add(types.InlineKeyboardButton(f"🗓 {slot}", callback_data=f"pick:{slot}"))
            
    keyboard.add(types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_booking"))
    return keyboard

def get_cancel_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton("❌ Отмена записи", callback_data="cancel_booking"))
    return keyboard

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    user_context[user_id] = []
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)

    welcome_text = (
        "Здравствуйте! 🌷\n\n"
        "Добро пожаловать в онлайн-пространство разговорного английского!\n\n"
        "Здесь можно познакомиться с методикой, почитать отзывы, "
        "посмотреть свободные окошки и задать вопрос нашему AI-консультанту.\n\n"
        "Выберите нужный раздел 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

def save_name_step(message, chosen_slot):
    if message.text and message.text.startswith('/'):
        start_cmd(message)
        return

    student_name = message.text
    # Слот бронируется ТОЛЬКО ЗДЕСЬ, после получения имени
    booked_slots.add(chosen_slot)

    confirm_text = (
        f"✅ **Вы успешно записаны!** 🎉\n\n"
        f"👤 **Ученик:** {student_name}\n"
        f"📅 **Время:** {chosen_slot}\n\n"
        f"Преподаватель свяжется с вами: {ADMIN_USERNAME}"
    )
    bot.send_message(message.chat.id, confirm_text, parse_mode="Markdown", reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id

    if call.data == "about":
        text = (
            "👩‍🏫 **О преподавателе**\n\n"
            "Сертифицированный преподаватель английского языка с опытом более 12 лет.\n\n"
            "✅ Практика живой речи с первого занятия\n"
            "✅ Индивидуальный подход и снятие страха говорить\n"
            "✅ Удобный онлайн-формат\n"
            "✅ Результат уже через 1 месяц занятий 🌷"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=get_main_menu())

    elif call.data == "ask_ai":
        text = "🤖 **Режим AI-консультации:** напишите ваш вопрос прямо в чат (о ценах, графике, формате):"
        bot.send_message(chat_id, text, parse_mode="Markdown")

    elif call.data == "reviews":
        text = (
            "💬 **Отзывы учеников:**\n\n"
            "⭐ **Виктория:** «Перестала бояться созвонов на английском на работе, всё супер!»\n\n"
            "⭐ **Максим:** «Сдал экзамен на отлично, уроки проходят легко и понятно!»"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=get_main_menu())

    elif call.data in ["slots", "book"]:
        free = [s for s in AVAILABLE_SLOTS if s not in booked_slots]
        if not free:
            bot.send_message(chat_id, f"Свободных мест нет. Напишите: {ADMIN_USERNAME}", reply_markup=get_slots_keyboard())
        else:
            bot.send_message(chat_id, "📅 **Выберите удобное окошко:**", parse_mode="Markdown", reply_markup=get_slots_keyboard())

    elif call.data.startswith("pick:"):
        chosen_slot = call.data.replace("pick:", "")
        if chosen_slot in booked_slots:
            bot.send_message(chat_id, "Это место уже занято! Выберите другое:", reply_markup=get_slots_keyboard())
        else:
            text = f"✨ **Вы выбрали:**\n📅 {chosen_slot}\n\nКак зовут ученика?"
            msg = bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=get_cancel_keyboard())
            bot.register_next_step_handler(msg, save_name_step, chosen_slot)

    elif call.data == "cancel_booking":
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        bot.send_message(chat_id, "Запись отменена. Все свободные окошки сохранены 🌷", reply_markup=get_main_menu())

    elif call.data == "reset_slots":
        booked_slots.clear()
        bot.send_message(chat_id, "✅ Все окошки снова доступны!", reply_markup=get_slots_keyboard())

    bot.answer_callback_query(call.id)

# Функция прямого запроса к Kie.ai
def query_kie_ai(messages_list):
    headers = {
        "Authorization": f"Bearer {KIE_API_KEY.strip()}",
        "api-key": KIE_API_KEY.strip(),
        "Content-Type": "application/json"
    }

    # Варианты рабочих URL провайдера Kie.ai
    endpoints = [
        "https://api.kie.ai/v1/chat/completions",
        "https://api.kie.ai/chat/completions",
        "https://api.kie.ai/api/v1/chat/completions"
    ]
    
    models = ["gpt-4o-mini", "gpt-3.5-turbo"]

    for url in endpoints:
        for model in models:
            payload = {
                "model": model,
                "messages": messages_list,
                "temperature": 0.7
            }
            try:
                res = requests.post(url, headers=headers, json=payload, timeout=12)
                if res.status_code == 200:
                    data = res.json()
                    if "choices" in data and len(data["choices"]) > 0:
                        return data["choices"][0]["message"]["content"]
            except Exception:
                continue

    return "⚠️ Не удалось получить ответ от сервера ИИ. Проверьте правильность KIE_API_KEY."

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    user_id = message.from_user.id
    user_text = message.text

    if user_id not in ALLOWED_USERS:
        bot.reply_to(message, "⚠️ Доступ открыт только для тестирования преподавателем (ID: 328761045).")
        return

    bot.send_chat_action(message.chat.id, 'typing')

    if user_id not in user_context:
        user_context[user_id] = []

    user_context[user_id].append({"role": "user", "content": user_text})
    if len(user_context[user_id]) > 10:
        user_context[user_id] = user_context[user_id][-10:]

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + user_context[user_id]

    reply = query_kie_ai(messages)
    user_context[user_id].append({"role": "assistant", "content": reply})
    bot.reply_to(message, reply, reply_markup=get_main_menu())

if __name__ == "__main__":
    bot.infinity_polling()
