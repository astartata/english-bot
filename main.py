import telebot
from telebot import types
import requests

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8719479123:AAGUe43dzC-B7F17_yl6_HBJ2KjAgDebqIY"
KIE_API_KEY = "46fe3db9b42642fc131a4311965bf8eb"

ADMIN_USERNAME = "@astartata"

# Белый список: проверяющий (328761045) + ваш ID (7718617445)
ALLOWED_USERS = [328761045, 7718617445]

bot = telebot.TeleBot(BOT_TOKEN)

# Список всех исходных слотов
ALL_SLOTS = [
    "Пн, 24 августа • 17:00",
    "Ср, 26 августа • 18:30",
    "Сб, 29 августа • 11:00"
]

# Хранилище только подтвержденных записей
confirmed_bookings = set()

# Временный выбор слота
user_selected_slot = {}
user_dialog_history = {}

SYSTEM_PROMPT = (
    "Ты — главный AI-консультант онлайн-школы разговорного английского языка Елены Смирновой.\n"
    "Твоя задача — давать развернутые, экспертные, доброжелательные и подробные ответы родителям и ученикам.\n\n"
    "ДАННЫЕ О КУРСЕ:\n"
    "1. Преподаватель: Елена Смирнова, опыт более 12 лет, международные сертификаты. Упор на преодоление языкового барьера.\n"
    "2. Цены:\n"
    "   - Мини-группа (3-4 человека): 900 руб/урок (60 мин)\n"
    "   - Индивидуально: 1800 руб/урок (60 мин)\n"
    "3. Формат: курс 3 месяца (2 раза в неделю по 60 мин), 80% живой разговорной речи на интерактивной платформе.\n"
    "4. Пробный урок: бесплатно (30 мин диагностика уровня и подбор программы).\n\n"
    "ПРАВИЛО: КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО использовать разметку Markdown (звездочки, решетки, нижние подчеркивания). "
    "Пиши чистым понятным текстом с абзацами и эмодзи."
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
    # Показываем только те, по которым реально ввели имя
    free_slots = [s for s in ALL_SLOTS if s not in confirmed_bookings]
    
    if not free_slots:
        keyboard.add(types.InlineKeyboardButton("🔄 Сбросить все записи", callback_data="reset_slots"))
    else:
        for slot in free_slots:
            keyboard.add(types.InlineKeyboardButton(f"🗓 {slot}", callback_data=f"pick:{slot}"))
            
    keyboard.add(types.InlineKeyboardButton("⬅️ Главное меню", callback_data="to_main_menu"))
    return keyboard

def get_cancel_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton("❌ Отмена (вернуться к окошкам)", callback_data="cancel_to_slots"))
    return keyboard

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    user_dialog_history[user_id] = []
    user_selected_slot.pop(user_id, None)
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)

    welcome_text = (
        "Здравствуйте! 🌷\n\n"
        "Добро пожаловать в онлайн-пространство разговорного английского Елены Смирновой!\n\n"
        "Здесь можно узнать о методике, почитать отзывы, "
        "посмотреть свободные окошки и задать вопрос нашему AI-консультанту.\n\n"
        "Выберите нужный раздел в меню ниже 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

def save_name_step(message):
    user_id = message.from_user.id

    if message.text and message.text.startswith('/'):
        user_selected_slot.pop(user_id, None)
        start_cmd(message)
        return

    slot = user_selected_slot.get(user_id)
    if not slot:
        bot.send_message(message.chat.id, "Выбор времени был сброшен. Пожалуйста, выберите окошко:", reply_markup=get_slots_keyboard())
        return

    student_name = message.text.strip()
    
    # БРОНИРОВАНИЕ ПРОИСХОДИТ ТОЛЬКО ЗДЕСЬ
    confirmed_bookings.add(slot)
    user_selected_slot.pop(user_id, None)

    confirm_text = (
        "✅ Вы успешно записаны на пробный урок! 🎉\n\n"
        f"👤 Ученик: {student_name}\n"
        f"📅 Время урока: {slot}\n\n"
        f"Преподаватель свяжется с вами в Telegram: {ADMIN_USERNAME}"
    )
    bot.send_message(message.chat.id, confirm_text, reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        bot.answer_callback_query(call.id)
    except Exception:
        pass

    chat_id = call.message.chat.id
    user_id = call.from_user.id

    if call.data == "to_main_menu":
        user_selected_slot.pop(user_id, None)
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        bot.send_message(chat_id, "Главное меню школы английского языка 👇", reply_markup=get_main_menu())

    elif call.data == "about":
        user_selected_slot.pop(user_id, None)
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
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
        user_selected_slot.pop(user_id, None)
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        text = "🤖 Режим подробной AI-консультации:\n\nНапишите любой ваш вопрос прямо в чат (о ценах, формате, расписании или пробном уроке):"
        bot.send_message(chat_id, text)

    elif call.data == "reviews":
        user_selected_slot.pop(user_id, None)
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        text = (
            "💬 Отзывы наших учеников:\n\n"
            "🌸 Виктория: «Перестала бояться созвонов на английском на работе. За 2 месяца ушел языковой барьер, уроки проходят супер!»\n\n"
            "🌸 Максим: «Сдал экзамен на отлично! Все правила отрабатываются сразу в диалогах, без скучной зубрежки.»"
        )
        bot.send_message(chat_id, text, reply_markup=get_main_menu())

    elif call.data in ["slots", "book"]:
        user_selected_slot.pop(user_id, None)
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        free = [s for s in ALL_SLOTS if s not in confirmed_bookings]
        if not free:
            bot.send_message(chat_id, f"Свободных мест нет. Напишите: {ADMIN_USERNAME}", reply_markup=get_slots_keyboard())
        else:
            bot.send_message(chat_id, "📅 Выберите подходящее свободное окошко:", reply_markup=get_slots_keyboard())

    elif call.data.startswith("pick:"):
        chosen_slot = call.data.replace("pick:", "")
        if chosen_slot in confirmed_bookings:
            bot.send_message(chat_id, "Это место уже подтверждено другим учеником. Выберите другое:", reply_markup=get_slots_keyboard())
        else:
            user_selected_slot[user_id] = chosen_slot
            text = f"✨ Вы выбрали время: {chosen_slot}\n\nКак зовут ученика? Напишите имя в чат:"
            msg = bot.send_message(chat_id, text, reply_markup=get_cancel_keyboard())
            bot.register_next_step_handler(msg, save_name_step)

    elif call.data == "cancel_to_slots":
        # СБРОС ВЫБОРА И МГНОВЕННЫЙ ВОЗВРАТ ВСЕХ ОКОШЕК
        user_selected_slot.pop(user_id, None)
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        bot.send_message(chat_id, "Запись отменена. Вот список всех доступных свободных окошек:", reply_markup=get_slots_keyboard())

    elif call.data == "reset_slots":
        confirmed_bookings.clear()
        user_selected_slot.pop(user_id, None)
        bot.send_message(chat_id, "✅ Все записи сброшены! Все окошки снова свободны:", reply_markup=get_slots_keyboard())

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
