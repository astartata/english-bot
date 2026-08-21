import telebot
from telebot import types
import requests

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8719479123:AAGUe43dzC-B7F17_yl6_HBJ2KjAgDebqIY"
ADMIN_USERNAME = "@astartata"

# Белый список пользователей
ALLOWED_USERS = [328761045, 7718617445]

# Прямая ссылка на фото-баннер
BANNER_IMAGE = "https://images.unsplash.com/photo-1546410531-bb4caa6b424d?w=900&auto=format&fit=crop&q=80"

bot = telebot.TeleBot(BOT_TOKEN)

# Список всех окошек
ALL_SLOTS = [
    "Пн, 24 августа • 17:00",
    "Ср, 26 августа • 18:30",
    "Сб, 29 августа • 11:00"
]

booked_slots = set()

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
    free = [s for s in ALL_SLOTS if s not in booked_slots]
    
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
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)

    welcome_text = (
        "Здравствуйте! 🌷\n\n"
        "Добро пожаловать в онлайн-пространство разговорного английского Елены Смирновой!\n\n"
        "Здесь можно познакомиться с методикой, почитать отзывы, "
        "посмотреть свободные окошки и задать вопрос нашему AI-консультанту.\n\n"
        "Выберите нужный раздел 👇"
    )
    try:
        bot.send_photo(message.chat.id, BANNER_IMAGE, caption=welcome_text, reply_markup=get_main_menu())
    except Exception:
        bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

def save_name_step(message, chosen_slot):
    if message.text and message.text.startswith('/'):
        start_cmd(message)
        return

    student_name = message.text
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
            "👩‍🏫 **О преподавателе: Елена Смирнова**\n\n"
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
        free = [s for s in ALL_SLOTS if s not in booked_slots]
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

def get_ai_answer(user_query):
    q = user_query.strip().lower()

    if any(k in q for k in ["цен", "стоим", "скольк", "оплат", "руб", "прайс"]):
        return (
            "💰 **Стоимость занятий:**\n\n"
            "• **Мини-группа (до 4 человек):** 900 руб / урок\n"
            "• **Индивидуальное обучение:** 1800 руб / урок\n\n"
            "Первый пробный урок-диагностика проводится бесплатно! Чтобы выбрать время, нажмите кнопку «✨ Записаться на пробный урок»."
        )

    if any(k in q for k in ["методик", "как проходит", "формат", "программ", "курс", "занят"]):
        return (
            "📚 **О методике и обучении:**\n\n"
            "• Курс длится 3 месяца, занятия 2 раза в неделю онлайн.\n"
            "• 80% времени каждого урока посвящено разговорной практике.\n"
            "• Методика нацелена на быстрое преодоление языкового барьера и свободное общение без зубрежки правил 🌷"
        )

    if any(k in q for k in ["график", "расписан", "врем", "когда", "день", "дни"]):
        return (
            "📅 **График занятий:**\n\n"
            "Занятия проходят в удобное дневное и вечернее время 2 раза в неделю.\n"
            "Посмотреть актуальное расписание свободных мест можно в разделе **«📅 Свободные окошки»**."
        )

    if any(k in q for k in ["пробн", "бесплатн", "диагностик", "перв"]):
        return (
            "✨ **Бесплатный пробный урок:**\n\n"
            "Это 30-минутное занятие-диагностика, где преподаватель определит текущий уровень и составит персональный план обучения.\n"
            "Для записи нажмите **«✨ Записаться на пробный урок»** в меню!"
        )

    return (
        "Здравствуйте! Я личный помощник Елены Смирновой 🌷\n\n"
        "Я могу ответить на любые вопросы по обучению:\n"
        "• Стоимость (900 руб группа / 1800 руб индивидуально)\n"
        "• Программа и методика курса (3 месяца, 2 раза в неделю)\n"
        "• Запись на бесплатную диагностику\n\n"
        "Выберите раздел меню или задайте конкретный вопрос!"
    )

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    user_id = message.from_user.id
    user_text = message.text

    if user_id not in ALLOWED_USERS:
        bot.reply_to(message, "⚠️ Доступ открыт только для тестирования преподавателем (ID: 328761045).")
        return

    bot.send_chat_action(message.chat.id, 'typing')
    response_text = get_ai_answer(user_text)
    bot.reply_to(message, response_text, parse_mode="Markdown", reply_markup=get_main_menu())

if __name__ == "__main__":
    bot.infinity_polling()
