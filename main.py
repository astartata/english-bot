import telebot
from telebot import types
import requests

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8719479123:AAGUe43dzC-B7F17_yl6_HBJ2KjAgDebqIY"
KIE_API_KEY = "30afd64c195a54760f0a706e48790c55"

# Белый список: проверяющий (328761045) + ваш ID (7718617445)
ALLOWED_USERS = [328761045, 7718617445]

BANNER_URL = "https://images.unsplash.com/photo-1546410531-bb4caa6b424d?w=1000&auto=format&fit=crop&q=80"

bot = telebot.TeleBot(BOT_TOKEN)

user_context = {}

SYSTEM_PROMPT = (
    "Ты — личный AI-помощник Анастасии Александровны, преподавателя английского языка для детей. "
    "Твоя задача — отвечать на вопросы родителей о формате занятий, стоимости (индивидуально — 1500 руб/час, "
    "мини-группы — 800 руб/час), методике и подготовке. Отвечай доброжелательно, кратко и вежливо, "
    "ненавязчиво предлагая записаться на бесплатный пробный урок-диагностику."
)

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

def get_slots_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("Чт, 20 августа • 15:00", callback_data="slot_Чт, 20 августа • 15:00"),
        types.InlineKeyboardButton("Пт, 21 августа • 16:00", callback_data="slot_Пт, 21 августа • 16:00"),
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

def process_child_name_step(message, chosen_slot):
    if message.text and message.text.startswith('/'):
        start_cmd(message)
        return

    child_name = message.text
    confirm_text = (
        f"✨ **Вы успешно записаны!** 🌷\n\n"
        f"👤 **Имя:** {child_name}\n"
        f"📅 **Окошко:** {chosen_slot}\n\n"
        f"Анастасия Александровна свяжется с вами перед началом занятия: @annie_anastasia"
    )
    bot.send_message(message.chat.id, confirm_text, parse_mode="Markdown", reply_markup=get_main_menu())

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
        text = (
            f"✨ **Вы выбрали:**\n"
            f"📅 {slot_name}\n\n"
            f"Как зовут ребёнка?"
        )
        msg = bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=get_cancel_keyboard())
        bot.register_next_step_handler(msg, process_child_name_step, slot_name)

    elif call.data == "cancel_booking":
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        bot.send_message(call.message.chat.id, "Запись отменена 🌷", reply_markup=get_main_menu())

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

    urls_to_try = [
        "https://api.kie.ai/api/v1/chat/completions",
        "https://api.kie.ai/v1/chat/completions",
        "https://api.kie.ai/chat/completions"
    ]

    bot_reply = None
    last_error = ""

    for url in urls_to_try:
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=20)
            if res.status_code == 200:
                data = res.json()
                if "choices" in data and len(data["choices"]) > 0:
                    bot_reply = data["choices"][0]["message"]["content"]
                    break
            else:
                last_error = f"HTTP {res.status_code}: {res.text}"
        except Exception as e:
            last_error = str(e)

    if bot_reply:
        user_context[user_id].append({"role": "assistant", "content": bot_reply})
        bot.reply_to(message, bot_reply, reply_markup=get_main_menu())
    else:
        bot.reply_to(message, f"Ошибка ответа ИИ: {last_error}")

if __name__ == "__main__":
    bot.infinity_polling()
