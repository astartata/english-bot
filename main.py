import telebot
from telebot import types
import requests

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8719479123:AAGUe43dzC-B7F17_yl6_HBJ2KjAgDebqIY"
KIE_API_KEY = "30afd64c195a54760f0a706e48790c55"

# Белый список: проверяющий (328761045) + ваш ID (7718617445)
ALLOWED_USERS = [328761045, 7718617445]

# Баннер курса
BANNER_URL = "https://images.unsplash.com/photo-1546410531-bb4caa6b424d?w=1000&auto=format&fit=crop&q=80"

bot = telebot.TeleBot(BOT_TOKEN)

user_context = {}

SYSTEM_PROMPT = (
    "Ты — личный AI-консультант школы английского языка Елены Смирновой. "
    "Твоя задача — профессионально и дружелюбно консультировать учеников и родителей "
    "по поводу курсов разговорного английского. "
    "Стоимость занятий: мини-группа — 900 руб/час, индивидуально — 1800 руб/час. "
    "Курс длится 3 месяца, занятия проходят 2 раза в неделю на интерактивной платформе. "
    "Отвечай кратко, ёмко, по делу и мягко предлагай записаться на бесплатный пробный урок."
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
    keyboard.add(
        types.InlineKeyboardButton("Пн, 24 августа • 17:00", callback_data="slot_Пн, 24 августа • 17:00"),
        types.InlineKeyboardButton("Ср, 26 августа • 18:30", callback_data="slot_Ср, 26 августа • 18:30"),
        types.InlineKeyboardButton("Сб, 29 августа • 11:00", callback_data="slot_Сб, 29 августа • 11:00"),
        types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_booking")
    )
    return keyboard

def get_cancel_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_booking"))
    return keyboard

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    user_context[user_id] = []

    caption = (
        "Здравствуйте! 🇬🇧\n\n"
        "Добро пожаловать в онлайн-пространство разговорного английского Елены Смирновой!\n\n"
        "Здесь вы можете узнать подробнее о методике быстрого преодоления языкового барьера, "
        "посмотреть расписание свободных мест и задать любой вопрос нашему AI-ассистенту.\n\n"
        "Выберите интересующий раздел меню ниже 👇"
    )
    try:
        bot.send_photo(message.chat.id, BANNER_URL, caption=caption, reply_markup=get_main_menu())
    except Exception:
        bot.send_message(message.chat.id, caption, reply_markup=get_main_menu())

# Функция, которая срабатывает сразу после ввода имени
def save_child_name_step(message, chosen_slot):
    if message.text and message.text.startswith('/'):
        start_cmd(message)
        return

    student_name = message.text
    confirm_text = (
        f"✅ **Запись успешно оформлена!** 🎉\n\n"
        f"👤 **Ученик:** {student_name}\n"
        f"📅 **Время урока:** {chosen_slot}\n\n"
        f"Преподаватель свяжется с вами для отправки ссылки на урок: @elena_english_pro"
    )
    bot.send_message(message.chat.id, confirm_text, parse_mode="Markdown", reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id

    if call.data == "about":
        text = (
            "👩‍🏫 **О преподавателе: Елена Викторовна Смирнова**\n\n"
            "Сертифицированный преподаватель (CELTA / Cambridge), опыт работы более 12 лет.\n\n"
            "🔹 Авторская методика погружения без зубрёжки\n"
            "🔹 Развитие беглой речи с первого урока\n"
            "🔹 Интерактивные материалы и разговорные клубы\n"
            "🔹 95% студентов начинают уверенно говорить уже через 2 месяца"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=get_main_menu())

    elif call.data == "ask_ai":
        text = (
            "🤖 **Режим консультации с ИИ**\n\n"
            "Задайте любой вопрос о курсе, методике, ценах или графике прямо в поле сообщения ниже:"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown")

    elif call.data == "reviews":
        text = (
            "💬 **Отзывы наших учеников:**\n\n"
            "⭐ **Виктория К.:**\n"
            "«Спустя месяц занятий перестала паниковать при разговоре с иностранными коллегами. Уроки очень живые!»\n\n"
            "⭐ **Артем М. (папа Дениса, 12 лет):**\n"
            "«Сын подтянул оценку с тройки до твёрдой пятёрки и с удовольствием смотрит мультфильмы в оригинале.»"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=get_main_menu())

    elif call.data in ["slots", "book"]:
        text = "📅 **Выберите удобное окошко для пробного урока:**"
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=get_slots_keyboard())

    elif call.data.startswith("slot_"):
        slot_name = call.data.replace("slot_", "")
        text = (
            f"✨ **Выбранное время:**\n📅 {slot_name}\n\n"
            f"Напишите имя ученика (и контакт для связи):"
        )
        msg = bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=get_cancel_keyboard())
        bot.register_next_step_handler(msg, save_child_name_step, slot_name)

    elif call.data == "cancel_booking":
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        bot.send_message(chat_id, "Запись отменена. Главное меню:", reply_markup=get_main_menu())

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

    headers = {
        "Authorization": f"Bearer {KIE_API_KEY.strip()}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.7
    }

    # Точные маршруты шлюза Kie.ai
    endpoints = [
        "https://api.kie.ai/openai/v1/chat/completions",
        "https://api.kie.ai/api/v1/chat/completions",
        "https://api.kie.ai/v1/chat/completions"
    ]

    reply_content = None
    err_log = ""

    for url in endpoints:
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=20)
            if r.status_code == 200:
                data = r.json()
                if "choices" in data and len(data["choices"]) > 0:
                    reply_content = data["choices"][0]["message"]["content"]
                    break
            else:
                err_log = f"HTTP {r.status_code}: {r.text}"
        except Exception as e:
            err_log = str(e)

    if reply_content:
        user_context[user_id].append({"role": "assistant", "content": reply_content})
        bot.reply_to(message, reply_content, reply_markup=get_main_menu())
    else:
        bot.reply_to(message, f"Ошибка ответа ИИ: {err_log}")

if __name__ == "__main__":
    bot.infinity_polling()
