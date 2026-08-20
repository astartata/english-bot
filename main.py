import telebot
from telebot import types
from openai import OpenAI

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8719479123:AAGUe43dzC-B7F17_yl6_HBJ2KjAgDebqIY"
KIE_API_KEY = "30afd64c195a54760f0a706e48790c55"

# Белый список: проверяющий + ваш TG ID
ALLOWED_USERS = [328761045, 7718617445]  # Добавьте свой ID через запятую, например: [328761045, 123456789]

# Ссылка на красивый баннер визитки
BANNER_URL = "https://images.unsplash.com/photo-1546410531-bb4caa6b424d?w=1000&auto=format&fit=crop&q=80"

bot = telebot.TeleBot(BOT_TOKEN)

ai_client = OpenAI(
    api_key=KIE_API_KEY,
    base_url="https://api.kie.ai/api/v1"
)

user_context = {}
user_state = {}

SYSTEM_PROMPT = (
    "Ты — личный AI-помощник Анастасии Александровны, преподавателя разговорного английского языка. "
    "Твоя задача — отвечать на вопросы родителей и учеников о формате занятий, стоимости, "
    "методике и подготовке. Отвечай доброжелательно, грамотно, структурированно и вежливо, "
    "подводя к записи на бесплатный пробный урок-диагностику."
)

# Главное меню с кнопками
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

# Меню выбора окошек для записи
def get_slots_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("Чт, 20 августа • 15:00", callback_data="slot_1"),
        types.InlineKeyboardButton("Пт, 21 августа • 16:00", callback_data="slot_2"),
        types.InlineKeyboardButton("Сб, 22 августа • 12:00", callback_data="slot_3"),
        types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_booking")
    )
    return keyboard

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    user_context[user_id] = []
    user_state[user_id] = "menu"

    caption = (
        "Привет! 🌷\n\n"
        "Рада видеть вас здесь.\n\n"
        "Я — помощник Анастасии Александровны, преподавателя английского языка.\n\n"
        "Здесь можно спокойно познакомиться с методикой, почитать отзывы, "
        "посмотреть свободные окошки и выбрать удобное время для занятия.\n\n"
        "Анастасия Александровна помогает учить английский без страха ошибок, "
        "с интересом и в комфортной атмосфере.\n\n"
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
            "с высшим филологическим образованием и большим опытом работы.\n\n"
            "В своей работе я сочетаю системный подход, понятное объяснение материала "
            "и комфортную атмосферу.\n\n"
            "✅ Высшее филологическое образование\n"
            "✅ Опыт работы устным переводчиком\n"
            "✅ Более 16 лет преподавания\n"
            "✅ Регулярное участие в профессиональных конференциях\n\n"
            "Мои ученики не просто улучшают оценки — они начинают свободно говорить "
            "и перестают бояться ошибок 🌷"
        )
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=get_main_menu())

    elif call.data == "ask_ai":
        user_state[user_id] = "ai_dialog"
        text = (
            "Здравствуйте! 🌷\n\n"
            "Я личный AI-помощник Анастасии Александровны.\n"
            "Я могу ответить на вопросы о занятиях, стоимости, формате обучения, "
            "расписании и подходе к урокам.\n\n"
            "Напишите ваш вопрос прямо в чат, и я постараюсь помочь."
        )
        bot.send_message(call.message.chat.id, text)

    elif call.data == "reviews":
        text = (
            "💬 **Отзывы родителей:**\n\n"
            "🌸 **Алина, мама Влады:**\n"
            "«Добрый день. Анастасия привила любовь к английскому! Влада получала 4-ки, "
            "а четверть завершила на 5 с отличными знаниями.»\n\n"
            "🌸 **Сильвия:**\n"
            "«Занятия были очень полезными и интересными. Ребёнок всегда вовлечён в процесс, "
            "результаты отличные!»"
        )
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=get_main_menu())

    elif call.data == "slots":
        text = "📅 **Выберите удобное окошко:**"
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=get_slots_keyboard())

    elif call.data == "book":
        text = "✨ **Выберите удобное свободное время для пробного урока:**"
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=get_slots_keyboard())

    elif call.data in ["slot_1", "slot_2", "slot_3"]:
        slots_map = {
            "slot_1": "Четверг, 20 августа • 15:00",
            "slot_2": "Пятница, 21 августа • 16:00",
            "slot_3": "Суббота, 22 августа • 12:00"
        }
        chosen = slots_map[call.data]
        text = (
            f"✨ **Вы выбрали:**\n📅 {chosen}\n\n"
            "Для подтверждения записи напишите преподавателю: @annie_anastasia 🌷"
        )
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=get_main_menu())

    elif call.data == "cancel_booking":
        bot.send_message(call.message.chat.id, "Запись отменена 🌷", reply_markup=get_main_menu())

    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    user_id = message.from_user.id
    user_text = message.text

    # Проверка белого списка (проверяющий + вы)
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
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        reply_text = response.choices[0].message.content
        user_context[user_id].append({"role": "assistant", "content": reply_text})
        bot.reply_to(message, reply_text, reply_markup=get_main_menu())
    except Exception as e:
        bot.reply_to(message, f"Ошибка ИИ: {e}")

if __name__ == "__main__":
    bot.infinity_polling()
