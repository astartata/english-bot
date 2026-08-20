import telebot
from telebot import types
import requests

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "ВАШ_ТОКЕН_ОТ_BOTFATHER"
KIE_API_KEY = "ВАШ_КЛЮЧ_ОТ_KIE_AI"

# ВАШ РЕАЛЬНЫЙ ЮЗЕРНЕЙМ В ТЕЛЕГРАМ (без @ или с @):
ADMIN_USERNAME = "@astartata"  # Укажите ваш действующий контакт в Telegram

# Белый список: проверяющий (328761045) + ваш ID (7718617445)
ALLOWED_USERS = [328761045, 7718617445]

BANNER_URL = "https://images.unsplash.com/photo-1546410531-bb4caa6b424d?w=1000&auto=format&fit=crop&q=80"

bot = telebot.TeleBot(BOT_TOKEN)

# Список доступных слотов (занятые будут удаляться динамически)
available_slots = [
    "Пн, 24 августа • 17:00",
    "Ср, 26 августа • 18:30",
    "Сб, 29 августа • 11:00"
]

user_context = {}

SYSTEM_PROMPT = (
    "Ты — личный AI-консультант преподавателя курсов разговорного английского языка. "
    "Твоя задача — вежливо, профессионально и понятно консультировать учеников и родителей. "
    "Стоимость обучения: мини-группа (до 4 человек) — 900 руб/занятие, индивидуально — 1800 руб/занятие. "
    "Курс рассчитан на 3 месяца (2 раза в неделю), упор на преодоление языкового барьера и разговорную речь. "
    "Отвечай кратко и доброжелательно, предлагай записаться на бесплатное пробное занятие-диагностику."
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
        keyboard.add(types.InlineKeyboardButton("⚠️ Свободных мест нет", callback_data="none"))
    else:
        for idx, slot in enumerate(available_slots):
            keyboard.add(types.InlineKeyboardButton(slot, callback_data=f"slot_{idx}"))
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

    caption = (
        "Здравствуйте! 🇬🇧\n\n"
        "Добро пожаловать в онлайн-пространство разговорного английского!\n\n"
        "Здесь вы можете узнать подробнее о программе обучения, "
        "посмотреть график свободных мест и задать любой интересующий вопрос AI-ассистенту.\n\n"
        "Выберите раздел в меню ниже 👇"
    )
    try:
        bot.send_photo(message.chat.id, BANNER_URL, caption=caption, reply_markup=get_main_menu())
    except Exception:
        bot.send_message(message.chat.id, caption, reply_markup=get_main_menu())

def save_student_step(message, chosen_slot):
    if message.text and message.text.startswith('/'):
        start_cmd(message)
        return

    student_name = message.text
    
    # Удаляем выбранный слот из списка доступных, чтобы его больше никто не мог выбрать
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
            "Сертифицированный преподаватель английского языка с опытом более 12 лет.\n\n"
            "🔹 Практика живой речи с первого занятия\n"
            "🔹 Индивидуальная программа под уровень и цели\n"
            "🔹 Снятие языкового барьера и страха говорить\n"
            "🔹 Удобный онлайн-формат на интерактивной доске"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=get_main_menu())

    elif call.data == "ask_ai":
        text = (
            "🤖 **Режим консультации с AI**\n\n"
            "Задайте вопрос о курсе, ценах, методике или графике занятий прямо в чат:"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown")

    elif call.data == "reviews":
        text = (
            "💬 **Отзывы учеников:**\n\n"
            "⭐ **Виктория:** «Спустя месяц перестала бояться созвонов на английском на работе!»\n\n"
            "⭐ **Артем:** «Сын исправил школьную оценку на отлично и с интересом учит язык.»"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=get_main_menu())

    elif call.data in ["slots", "book"]:
        if not available_slots:
            bot.send_message(chat_id, "На данный момент все окошки заняты. Напишите нам напрямую: " + ADMIN_USERNAME, reply_markup=get_main_menu())
        else:
            bot.send_message(chat_id, "📅 **Выберите удобное свободное время:**", parse_mode="Markdown", reply_markup=get_slots_keyboard())

    elif call.data.startswith("slot_"):
        idx = int(call.data.replace("slot_", ""))
        if idx < len(available_slots):
            chosen_slot = available_slots[idx]
            text = f"✨ **Вы выбрали:**\n📅 {chosen_slot}\n\nНапишите имя ученика и контактный номер:"
            msg = bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=get_cancel_keyboard())
            bot.register_next_step_handler(msg, save_student_step, chosen_slot)
        else:
            bot.send_message(chat_id, "Это окошко уже занято! Пожалуйста, выберите другое:", reply_markup=get_slots_keyboard())

    elif call.data == "cancel_booking":
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        bot.send_message(chat_id, "Запись отменена.", reply_markup=get_main_menu())

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

    # Список возможных форматов запроса к Kie.ai
    attempts = [
        ("https://api.kie.ai/v1/chat/completions", {"Authorization": f"Bearer {KIE_API_KEY.strip()}", "Content-Type": "application/json"}),
        ("https://api.kie.ai/chat/completions", {"Authorization": f"Bearer {KIE_API_KEY.strip()}", "api-key": KIE_API_KEY.strip(), "Content-Type": "application/json"}),
        ("https://api.kie.ai/api/v1/chat/completions", {"Authorization": f"Bearer {KIE_API_KEY.strip()}", "Content-Type": "application/json"}),
    ]

    payload = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.7
    }

    reply_content = None
    err_log = ""

    for url, hdrs in attempts:
        try:
            r = requests.post(url, headers=hdrs, json=payload, timeout=20)
            if r.status_code == 200:
                data = r.json()
                if "choices" in data and len(data["choices"]) > 0:
                    reply_content = data["choices"][0]["message"]["content"]
                    break
            else:
                err_log = f"URL {url} -> HTTP {r.status_code}: {r.text}"
        except Exception as e:
            err_log = str(e)

    if reply_content:
        user_context[user_id].append({"role": "assistant", "content": reply_content})
        bot.reply_to(message, reply_content, reply_markup=get_main_menu())
    else:
        bot.reply_to(message, f"Ошибка ответа ИИ:\n{err_log}")

if __name__ == "__main__":
    bot.infinity_polling()
