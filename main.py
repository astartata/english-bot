import telebot
from telebot import types
from openai import OpenAI

# 1. ТОКЕНЫ И НАСТРОЙКИ
BOT_TOKEN = "8719479123:AAGUe43dzC-B7F17_yl6_HBJ2KjAgDebqIY"
KIE_API_KEY = "30afd64c195a54760f0a706e48790c55"

# Проверяющий + ваш ID:
ALLOWED_USERS = [328761045, 7718617445]

bot = telebot.TeleBot(BOT_TOKEN)

ai_client = OpenAI(
    api_key=KIE_API_KEY,
    base_url="https://api.kie.ai/api/v1"
)

user_context = {}
user_mode = {}  # Режим общения с ИИ

SYSTEM_PROMPT = (
    "Ты — личный AI-помощник преподавателя курса «Разговорный английский». "
    "Твоя задача — отвечать на вопросы о занятиях, формате, стоимости и подходе к обучению. "
    "Отвечай вежливо, кратко, помогай преодолеть языковой барьер и ненавязчиво "
    "предлагай записаться на бесплатный пробный урок-диагностику."
)

def get_main_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btn_about = types.InlineKeyboardButton("👩‍🏫 Обо мне кратко", callback_data="about")
    btn_ai = types.InlineKeyboardButton("🤖 Задать вопрос", callback_data="ask_ai")
    btn_reviews = types.InlineKeyboardButton("💬 Отзывы", callback_data="reviews")
    btn_slots = types.InlineKeyboardButton("📅 Свободные окошки", callback_data="slots")
    btn_book = types.InlineKeyboardButton("✨ Записаться на урок", callback_data="book")
    keyboard.add(btn_about, btn_ai, btn_reviews, btn_slots, btn_book)
    return keyboard

@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    user_context[user_id] = []
    user_mode[user_id] = "menu"

    welcome_text = (
        "Привет! 🌷\n\n"
        "Рада видеть вас здесь.\n\n"
        "Я — помощник преподавателя курса «Разговорный английский».\n\n"
        "Здесь можно познакомиться с методикой, почитать отзывы, "
        "посмотреть свободные окошки и задать любой вопрос нашему ИИ-ассистенту.\n\n"
        "Выберите, что хотите посмотреть 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user_id = call.from_user.id

    if call.data == "about":
        text = (
            "👩‍🏫 **Обо мне кратко**\n\n"
            "Я преподаватель английского языка с высшим профильным образованием "
            "и многолетним опытом разговорной практики.\n\n"
            "✅ Индивидуальный подход без стресса\n"
            "✅ 80% времени каждого урока — живой разговор\n"
            "✅ Разбор реальных жизненных ситуаций и снятие языкового барьера\n"
            "✅ Быстрый результат за 3 месяца регулярных занятий"
        )
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=get_main_keyboard())

    elif call.data == "ask_ai":
        user_mode[user_id] = "chatting_with_ai"
        text = (
            "Здравствуйте! 🌷\n\n"
            "Я личный AI-помощник курса разговорного английского.\n"
            "Я могу ответить на любые вопросы о занятиях, стоимости, расписании и программе.\n\n"
            "Напишите ваш вопрос в чат, и я помогу вам!"
        )
        bot.send_message(call.message.chat.id, text)

    elif call.data == "reviews":
        text = (
            "💬 **Отзывы студентов:**\n\n"
            "⭐️ *Елена*: «Наконец-то пропал страх говорить на работе! Уроки проходят на одном дыхании.»\n\n"
            "⭐️ *Максим*: «За 2 месяца подтянул речь перед переездом за границу. Отличная подача материала!»"
        )
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=get_main_keyboard())

    elif call.data == "slots":
        text = (
            "📅 **Свободные окошки на этой неделе:**\n\n"
            "• Вторник — 18:00\n"
            "• Четверг — 19:30\n"
            "• Суббота — 12:00"
        )
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=get_main_keyboard())

    elif call.data == "book":
        text = (
            "✨ **Запись на пробный урок**\n\n"
            "Чтобы записаться на бесплатное занятие-диагностику, напишите в личные сообщения: @annie_anastasia\n"
            "Укажите удобный день и время!"
        )
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=get_main_keyboard())

    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    user_text = message.text

    # Проверка белого списка для защиты токенов ИИ
    if user_id not in ALLOWED_USERS:
        bot.reply_to(message, "⚠️ Доступ к ИИ открыт только для тестирования преподавателем (ID: 328761045).")
        return

    bot.send_chat_action(message.chat.id, 'typing')

    if user_id not in user_context:
        user_context[user_id] = []

    user_context[user_id].append({"role": "user", "content": user_text})
    if len(user_context[user_id]) > 10:
        user_context[user_id] = user_context[user_id][-10:]

    messages_for_ai = [{"role": "system", "content": SYSTEM_PROMPT}] + user_context[user_id]

    try:
        response = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_for_ai,
            max_tokens=500
        )
        reply = response.choices[0].message.content
        user_context[user_id].append({"role": "assistant", "content": reply})
        bot.reply_to(message, reply, reply_markup=get_main_keyboard())
    except Exception as e:
        bot.reply_to(message, f"Ошибка ИИ: {e}")

if __name__ == "__main__":
    bot.infinity_polling()
