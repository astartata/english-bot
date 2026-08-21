import telebot
from telebot import types
from openai import OpenAI

BOT_TOKEN = "8719479123:AAGUe43dzC-B7F17_yl6_HBJ2KjAgDebqIY"
KIE_API_KEY = "30afd64c195a54760f0a706e48790c55"

ADMIN_USERNAME = "@astartata"

# Белый список: проверяющий (328761045) + ваш ID (7718617445)
ALLOWED_USERS = [328761045, 7718617445]

bot = telebot.TeleBot(BOT_TOKEN)

# Официальное подключение к ИИ из урока
ai_client = OpenAI(
    api_key=KIE_API_KEY.strip(),
    base_url="https://api.kie.ai/v1"
)

# Список доступных окошек
available_slots = [
    "Пн, 24 августа • 17:00",
    "Ср, 26 августа • 18:30",
    "Сб, 29 августа • 11:00"
]

user_context = {}

# Инструкция для ИИ: все факты и цены уже заложены сюда
SYSTEM_PROMPT = (
    "Ты — личный AI-консультант преподавателя курсов разговорного английского языка Елены Смирновой. "
    "Твоя задача — вежливо, понятно и кратко консультировать учеников и родителей. "
    "Стоимость обучения: мини-группа — 900 руб/урок, индивидуально — 1800 руб/урок. "
    "Курс длится 3 месяца, занятия 2 раза в неделю. Упор на преодоление языкового барьера. "
    "Отвечай кратко, по делу и мягко предлагай записаться на бесплатный пробный урок."
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
            keyboard.add(types.InlineKeyboardButton(f"🗓 {slot}", callback_data=f"book_slot_{idx}"))
    keyboard.add(types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_booking"))
    return keyboard

def get_cancel_keyboard(chosen_slot):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton("❌ Отмена", callback_data=f"cancel_slot_{chosen_slot}"))
    return keyboard

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    user_context[user_id] = []

    welcome_text = (
        "Здравствуйте! 🌷\n\n"
        "Добро пожаловать в онлайн-пространство разговорного английского!\n\n"
        "Здесь можно познакомиться с программой, почитать отзывы, "
        "посмотреть свободные окошки и задать вопрос нашему AI-консультанту.\n\n"
        "Выберите нужный раздел 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

# Подтверждение записи после ввода имени
def save_student_step(message, chosen_slot):
    if message.text and message.text.startswith('/'):
        start_cmd(message)
        return

    student_name = message.text

    # Удаляем слот только сейчас, когда имя реально введено
    if chosen_slot in available_slots:
        available_slots.remove(chosen_slot)

    confirm_text = (
        f"✅ **Вы успешно записаны!** 🎉\n\n"
        f"👤 **Ученик:** {student_name}\n"
        f"📅 **Время урока:** {chosen_slot}\n\n"
        f"Преподаватель свяжется с вами для подтверждения: {ADMIN_USERNAME}"
    )
    bot.send_message(message.chat.id, confirm_text, parse_mode="Markdown", reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id

    if call.data == "about":
        text = (
            "👩‍🏫 **О преподавателе**\n\n"
            "Сертифицированный преподаватель с опытом более 12 лет.\n\n"
            "✅ Практика живой речи с первого занятия\n"
            "✅ Снятие языкового барьера и страха говорить\n"
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
            "⭐ **Виктория:** «Перестала бояться созвонов на работе, уроки супер!»\n\n"
            "⭐ **Максим:** «Сдал экзамен на отлично, методика очень понятная!»"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=get_main_menu())

    elif call.data in ["slots", "book"]:
        if not available_slots:
            bot.send_message(chat_id, f"Свободных мест нет. Напишите преподавателю: {ADMIN_USERNAME}", reply_markup=get_main_menu())
        else:
            bot.send_message(chat_id, "📅 **Выберите удобное окошко:**", parse_mode="Markdown", reply_markup=get_slots_keyboard())

    elif call.data.startswith("book_slot_"):
        idx = int(call.data.replace("book_slot_", ""))
        if idx < len(available_slots):
            chosen = available_slots[idx]
            text = f"✨ **Вы выбрали:**\n📅 {chosen}\n\nКак зовут ученика?"
            msg = bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=get_cancel_keyboard(chosen))
            bot.register_next_step_handler(msg, save_student_step, chosen)
        else:
            bot.send_message(chat_id, "Это место уже занято! Выберите другое:", reply_markup=get_slots_keyboard())

    elif call.data.startswith("cancel_slot_") or call.data == "cancel_booking":
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        bot.send_message(chat_id, "Запись отменена. Окошко осталось свободным 🌷", reply_markup=get_main_menu())

    elif call.data == "no_slots":
        bot.send_message(chat_id, f"Свободных мест нет. Напишите: {ADMIN_USERNAME}", reply_markup=get_main_menu())

    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    user_id = message.from_user.id
    user_text = message.text

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

    try:
        response = ai_client.chat.completions.create(
            model="gpt-3.5-turbo",
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
