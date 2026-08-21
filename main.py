import telebot
from telebot import types
from openai import OpenAI

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8719479123:AAGUe43dzC-B7F17_yl6_HBJ2KjAgDebqIY"
KIE_API_KEY = "30afd64c195a54760f0a706e48790c55"

ADMIN_USERNAME = "@astartata"

# Белый список: проверяющий (328761045) + ваш ID (7718617445)
ALLOWED_USERS = [328761045, 7718617445]

bot = telebot.TeleBot(BOT_TOKEN)

# Официальный клиент для работы с Kie.ai
ai_client = OpenAI(
    api_key=KIE_API_KEY.strip(),
    base_url="https://api.kie.ai/v1"
)

# Динамический список слотов
available_slots = [
    "Пн, 24 августа • 17:00",
    "Ср, 26 августа • 18:30",
    "Сб, 29 августа • 11:00"
]

user_context = {}

SYSTEM_PROMPT = (
    "Ты — личный AI-консультант школы разговорного английского языка Елены Смирновой. "
    "Твоя задача — вежливо, понятно и кратко консультировать учеников и родителей. "
    "Стоимость обучения: мини-группа — 900 руб/урок, индивидуально — 1800 руб/урок. "
    "Курс длится 3 месяца, занятия 2 раза в неделю. Упор на преодоление языкового барьера. "
    "Отвечай коротко, по делу и мягко предлагай записаться на бесплатный пробный урок."
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
    if not available_slots:
        keyboard.add(types.InlineKeyboardButton("⚠️ Свободных мест нет", callback_data="no_slots"))
    else:
        for idx, slot in enumerate(available_slots):
            keyboard.add(types.InlineKeyboardButton(f"🗓 {slot}", callback_data=f"slot_{idx}"))
    keyboard.add(types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_booking"))
    return keyboard

def get_cancel_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_booking"))
    return keyboard

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    user_context[user_id] = []

    welcome_text = (
        "Привет! 🌷\n\n"
        "Рада видеть вас здесь.\n\n"
        "Я — помощник Елены Викторовны, преподавателя разговорного английского языка.\n\n"
        "Здесь можно спокойно познакомиться с методикой, почитать отзывы, "
        "посмотреть свободные окошки и выбрать удобное время для занятия.\n\n"
        "Выберите, что хотите посмотреть 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

def save_name_step(message, chosen_slot):
    if message.text and message.text.startswith('/'):
        start_cmd(message)
        return

    student_name = message.text

    if chosen_slot in available_slots:
        available_slots.remove(chosen_slot)

    confirm_text = (
        f"✅ **Вы успешно записаны!** 🌷\n\n"
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
            "👩‍🏫 **Обо мне кратко**\n\n"
            "Меня зовут Елена Викторовна Смирнова. Я преподаватель английского языка "
            "с высшим образованием и опытом более 12 лет.\n\n"
            "✅ 80% практики живой разговорной речи на каждом уроке\n"
            "✅ Индивидуальный подход и снятие страха ошибок\n"
            "✅ Удобная интерактивная онлайн-платформа\n"
            "✅ Видимый прогресс уже через 1 месяц занятий 🌷"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=get_main_menu())

    elif call.data == "ask_ai":
        text = (
            "🤖 **Режим консультации с AI**\n\n"
            "Задайте любой вопрос о курсе, ценах, методике или графике — просто напишите его в поле сообщения ниже:"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown")

    elif call.data == "reviews":
        text = (
            "💬 **Отзывы учеников:**\n\n"
            "🌸 **Виктория:** «Перестала бояться говорить на созвонах по работе, всё супер!»\n\n"
            "🌸 **Максим:** «Сдал экзамен на отлично, методика очень понятная и без нудной зубрежки.»"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=get_main_menu())

    elif call.data in ["slots", "book"]:
        if not available_slots:
            bot.send_message(chat_id, f"Свободных мест нет. Напишите напрямую: {ADMIN_USERNAME}", reply_markup=get_main_menu())
        else:
            bot.send_message(chat_id, "📅 **Выберите удобное окошко:**", parse_mode="Markdown", reply_markup=get_slots_keyboard())

    elif call.data.startswith("slot_"):
        idx = int(call.data.replace("slot_", ""))
        if idx < len(available_slots):
            chosen = available_slots[idx]
            text = f"✨ **Вы выбрали:**\n📅 {chosen}\n\nКак зовут ученика?"
            msg = bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=get_cancel_keyboard())
            bot.register_next_step_handler(msg, save_name_step, chosen)
        else:
            bot.send_message(chat_id, "Это место уже занято! Выберите другое:", reply_markup=get_slots_keyboard())

    elif call.data == "cancel_booking":
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        bot.send_message(chat_id, "Запись отменена 🌷", reply_markup=get_main_menu())

    elif call.data == "no_slots":
        bot.send_message(chat_id, f"Свободных мест нет. Напишите: {ADMIN_USERNAME}", reply_markup=get_main_menu())

    bot.answer_callback_query(call.id)

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

    try:
        response = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=400,
            temperature=0.7
        )
        reply = response.choices[0].message.content
        user_context[user_id].append({"role": "assistant", "content": reply})
        bot.reply_to(message, reply, reply_markup=get_main_menu())
    except Exception as e:
        bot.reply_to(message, f"Ошибка ИИ: {e}")

if __name__ == "__main__":
    bot.infinity_polling()
