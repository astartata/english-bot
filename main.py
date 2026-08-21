import telebot
from telebot import types
import requests

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8719479123:AAGUe43dzC-B7F17_yl6_HBJ2KjAgDebqIY"
KIE_API_KEY = "46fe3db9b42642fc131a4311965bf8eb"

ADMIN_USERNAME = "@astartata"

# Белый список: проверяющий + ваш ID
ALLOWED_USERS = [328761045, 7718617445]

bot = telebot.TeleBot(BOT_TOKEN)

# Список всех исходных слотов
ALL_SLOTS = [
    "Пн, 24 августа • 17:00",
    "Ср, 26 августа • 18:30",
    "Сб, 29 августа • 11:00"
]

# Хранилище ТОЛЬКО подтвержденных записей (куда ввели имя)
booked_slots = set()
user_dialog_history = {}

SYSTEM_PROMPT = (
    "Ты — главный AI-консультант онлайн-школы разговорного английского языка Елены Смирновой.\n"
    "Твоя задача — давать развернутые, экспертные, доброжелательные и подробные ответы родителям и ученикам.\n\n"
    "ДАННЫЕ О КУРСЕ:\n"
    "1. Преподаватель: Елена Смирнова, опыт более 12 лет. Упор на преодоление языкового барьера.\n"
    "2. Цены: Мини-группа (3-4 человека) — 900 руб/урок. Индивидуально — 1800 руб/урок.\n"
    "3. Формат: курс 3 месяца (2 раза в неделю по 60 мин), 80% живой разговорной речи на интерактивной платформе.\n"
    "4. Пробный урок: бесплатно (30 мин диагностика уровня и подбор программы).\n\n"
    "ПРАВИЛО: КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО использовать разметку Markdown (звездочки, решетки, нижние подчеркивания, кавычки). "
    "Пиши чистым понятным текстом с абзацами и эмодзи."
)

def get_main_menu():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("👩‍🏫 О преподавателе", callback_data="about"),
        types.InlineKeyboardButton("🤖 Задать вопрос ИИ", callback_data="ask_ai"),
        types.InlineKeyboardButton("💬 Отзывы учеников", callback_data="reviews"),
        types.InlineKeyboardButton("📅 Свободные окошки", callback_data="slots"),
        types.InlineKeyboardButton("✨ Записаться на пробный урок", callback_data="slots")
    )
    return keyboard

def get_slots_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    free = [s for s in ALL_SLOTS if s not in booked_slots]
    
    if not free:
        keyboard.add(types.InlineKeyboardButton("🔄 Сбросить все записи", callback_data="reset_slots"))
    else:
        for s in free:
            keyboard.add(types.InlineKeyboardButton(f"🗓 {s}", callback_data=f"pick:{s}"))
            
    keyboard.add(types.InlineKeyboardButton("⬅️ Назад в меню", callback_data="to_main"))
    return keyboard

def get_cancel_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton("❌ Отмена (вернуться к окошкам)", callback_data="cancel_to_slots"))
    return keyboard

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    user_id = message.from_user.id
    user_dialog_history[user_id] = []

    text = (
        "Здравствуйте! 🌷\n\n"
        "Добро пожаловать в онлайн-пространство разговорного английского Елены Смирновой!\n\n"
        "Здесь можно узнать о методике, почитать отзывы, "
        "посмотреть свободные окошки и задать вопрос нашему AI-консультанту.\n\n"
        "Выберите нужный раздел в меню ниже 👇"
    )
    bot.send_message(message.chat.id, text, reply_markup=get_main_menu())

def save_name_step(message, chosen_slot):
    if message.text and message.text.startswith('/'):
        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
        start_cmd(message)
        return

    student_name = message.text.strip()
    
    # Фактическое занятие окошка происходит только после ввода имени
    booked_slots.add(chosen_slot)

    text = (
        "✅ Вы успешно записаны на пробный урок! 🎉\n\n"
        f"👤 Ученик: {student_name}\n"
        f"📅 Время урока: {chosen_slot}\n\n"
        f"Преподаватель свяжется с вами в Telegram: {ADMIN_USERNAME}"
    )
    bot.send_message(message.chat.id, text, reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        bot.answer_callback_query(call.id)
    except Exception:
        pass

    chat_id = call.message.chat.id
    
    # Жесткий сброс любых ожиданий текста при нажатии на ЛЮБУЮ кнопку
    bot.clear_step_handler_by_chat_id(chat_id=chat_id)

    if call.data == "to_main":
        try:
            bot.edit_message_text("Главное меню школы английского языка 👇", chat_id=chat_id, message_id=call.message.message_id, reply_markup=get_main_menu())
        except Exception:
            bot.send_message(chat_id, "Главное меню школы английского языка 👇", reply_markup=get_main_menu())

    elif call.data == "about":
        text = (
            "👩‍🏫 О преподавателе: Елена Смирнова\n\n"
            "Сертифицированный преподаватель с международными дипломами и опытом более 12 лет.\n\n"
            "• Авторская методика: 80% живой практики речи с первого урока\n"
            "• Быстрое преодоление языкового барьера и страха говорить\n"
            "• Современная онлайн-платформа со всеми интерактивными материалами\n"
            "• Результат уже через 1 месяц занятий 🌷"
        )
        bot.send_message(chat_id, text, reply_markup=get_main_menu())

    elif call.data == "ask_ai":
        text = "🤖 Режим AI-консультации:\n\nНапишите любой ваш вопрос прямо в чат (о ценах, формате, расписании или пробном уроке):"
        bot.send_message(chat_id, text)

    elif call.data == "reviews":
        text = (
            "💬 Отзывы наших учеников:\n\n"
            "🌸 Виктория: «Перестала бояться созвонов на английском на работе. За 2 месяца ушел языковой барьер, уроки проходят супер!»\n\n"
            "🌸 Максим: «Сдал экзамен на отлично! Все правила отрабатываются сразу в диалогах, без скучной зубрежки.»"
        )
        bot.send_message(chat_id, text, reply_markup=get_main_menu())

    elif call.data == "slots":
        free = [s for s in ALL_SLOTS if s not in booked_slots]
        text = "📅 Выберите подходящее свободное окошко:" if free else f"Свободных мест нет. Напишите: {ADMIN_USERNAME}"
        bot.send_message(chat_id, text, reply_markup=get_slots_keyboard())

    elif call.data.startswith("pick:"):
        chosen_slot = call.data.replace("pick:", "")
        if chosen_slot in booked_slots:
            # Если кто-то успел занять место
            try:
                bot.edit_message_text("Это место уже занято! Выберите другое:", chat_id=chat_id, message_id=call.message.message_id, reply_markup=get_slots_keyboard())
            except Exception:
                bot.send_message(chat_id, "Это место уже занято! Выберите другое:", reply_markup=get_slots_keyboard())
        else:
            text = f"✨ Вы выбрали время: {chosen_slot}\n\nКак зовут ученика? Напишите имя в чат:"
            try:
                msg = bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=get_cancel_keyboard())
                bot.register_next_step_handler(msg, save_name_step, chosen_slot)
            except Exception:
                msg = bot.send_message(chat_id, text, reply_markup=get_cancel_keyboard())
                bot.register_next_step_handler(msg, save_name_step, chosen_slot)

    elif call.data in ["cancel_to_slots", "cancel_booking", "cancel_slot"]:
        # Моментальный возврат окошек на экран вместо запроса имени
        text = "Запись отменена. 📅 Выберите свободное окошко:"
        try:
            bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=get_slots_keyboard())
        except Exception:
            bot.send_message(chat_id, text, reply_markup=get_slots_keyboard())

    elif call.data == "reset_slots":
        booked_slots.clear()
        text = "✅ Все записи сброшены! Окошки снова свободны:"
        try:
            bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=get_slots_keyboard())
        except Exception:
            bot.send_message(chat_id, text, reply_markup=get_slots_keyboard())

def remove_markdown(text):
    if not text:
        return ""
    for s in ["**", "__", "```", "`", "#", "*"]:
        text = text.replace(s, "")
    return text.strip()

def call_ai(messages_list):
    key = KIE_API_KEY.strip()
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    endpoints = [
        "[https://api.kie.ai/gemini-2.5-flash/v1/chat/completions](https://api.kie.ai/gemini-2.5-flash/v1/chat/completions)",
        "[https://api.kie.ai/gpt-4o/v1/chat/completions](https://api.kie.ai/gpt-4o/v1/chat/completions)",
        "[https://api.kie.ai/v1/chat/completions](https://api.kie.ai/v1/chat/completions)"
    ]

    for ep in endpoints:
        payload = {
            "messages": messages_list,
            "temperature": 0.7
        }
        try:
            r = requests.post(ep, headers=headers, json=payload, timeout=12)
            if r.status_code == 200:
                data = r.json()
                if "choices" in data and len(data["choices"]) > 0:
                    raw = data["choices"][0]["message"]["content"]
                    return remove_markdown(raw)
        except Exception:
            continue

    return (
        "Здравствуйте! С удовольствием расскажу подробнее о курсе разговорного английского Елены Смирновой 🌷\n\n"
        "1. Форматы и стоимость обучения:\n"
        "• Мини-группы (до 4 человек): 900 рублей за занятие (60 минут).\n"
        "• Индивидуальные уроки: 1800 рублей за занятие (60 минут).\n\n"
        "2. Методика и длительность:\n"
        "Курс рассчитан на 3 месяца регулярных занятий (2 раза в неделю). 80% времени посвящено живому общению.\n\n"
        "3. Бесплатный пробный урок:\n"
        "Мы проводим 30-минутную бесплатную диагностику, чтобы определить ваш уровень и составить персональный план обучения.\n\n"
        "Вы можете выбрать время в разделе «📅 Свободные окошки» в меню ниже!"
    )

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    user_id = message.from_user.id
    user_text = message.text

    if user_id not in ALLOWED_USERS:
        bot.reply_to(message, "⚠️ Доступ к ИИ открыт только для тестирования преподавателем (ID: 328761045).")
        return

    bot.send_chat_action(message.chat.id, 'typing')

    if user_id not in user_dialog_history:
        user_dialog_history[user_id] = []

    user_dialog_history[user_id].append({"role": "user", "content": user_text})
    if len(user_dialog_history[user_id]) > 10:
        user_dialog_history[user_id] = user_dialog_history[user_id][-10:]

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + user_dialog_history[user_id]

    ai_reply = call_ai(messages)
    user_dialog_history[user_id].append({"role": "assistant", "content": ai_reply})
    bot.reply_to(message, ai_reply, reply_markup=get_main_menu())

if __name__ == "__main__":
    bot.infinity_polling()
