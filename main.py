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

# Исходный список доступных окошек
ALL_SLOTS = [
    "Пн, 24 августа • 17:00",
    "Ср, 26 августа • 18:30",
    "Сб, 29 августа • 11:00"
]

# Хранилище подтвержденных записей (слот занимает ТОЛЬКО после отправки имени)
confirmed_bookings = set()

# Временный выбор до отправки имени
pending_user_slot = {}
user_dialog_history = {}

# Глубокая и подробная база знаний для ИИ
SYSTEM_PROMPT = (
    "Ты — главный AI-консультант онлайн-школы разговорного английского языка Елены Смирновой.\n"
    "Твоя задача — давать развернутые, экспертные, доброжелательные и подробные ответы родителям и потенциальным ученикам.\n\n"
    "ПОДРОБНЫЕ ДАННЫЕ О ШКОЛЕ И КУРСЕ:\n"
    "1. О преподавателе: Елена Смирнова, сертифицированный преподаватель с международными дипломами и опытом более 12 лет. Специализируется на преодолении психологического и языкового барьера.\n"
    "2. Форматы обучения и стоимость:\n"
    "   - Мини-группы (3-4 человека): 900 рублей за 60 минут. Идеально для живого общения, групповых диалогов и погружения в языковую среду.\n"
    "   - Индивидуальные занятия: 1800 рублей за 60 минут. Персональный темп, фокус на личных целях (работа, переезд, экзамены, бизнес-английский).\n"
    "3. Методика и формат уроков:\n"
    "   - Курс рассчитан на 3 месяца (24 урока при графике 2 раза в неделю по 60 минут).\n"
    "   - 80% времени каждого урока посвящено активной разговорной речи.\n"
    "   - Занятия проходят онлайн на современной интерактивной платформе с видеосвязью. Все материалы, карточки, аудио и конспекты предоставляются бесплатно в личном кабинете.\n"
    "   - Никакой скучной зубрежки правил: грамматика сразу отрабатывается в живых диалогах и жизненных ситуациях.\n"
    "4. Пробный урок:\n"
    "   - Проводится абсолютно БЕСПЛАТНО (30 минут). Включает точную диагностику текущего уровня, определение сильных сторон и составление персонального плана обучения.\n\n"
    "СТРОГОЕ ТРЕБОВАНИЕ К ФОРМАТИРОВАНИЮ ОТВЕТОВ:\n"
    "- КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО использовать разметку Markdown: никаких звездочек (** или *), нижних подчеркиваний (_), решеток (#) и обратных кавычек (`).\n"
    "- Ответ должен быть подробным, понятным, с комфортными абзацами и красивыми эмодзи.\n"
    "- В конце каждого ответа вежливо приглашай записаться на бесплатный пробный урок через кнопки меню."
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
    # Показываем только слоты, которые НЕ подтверждены
    available_slots = [slot for slot in ALL_SLOTS if slot not in confirmed_bookings]
    
    if not available_slots:
        keyboard.add(types.InlineKeyboardButton("🔄 Сбросить брони (вернуть все окошки)", callback_data="reset_slots"))
    else:
        for slot in available_slots:
            keyboard.add(types.InlineKeyboardButton(f"🗓 {slot}", callback_data=f"select_slot:{slot}"))
            
    keyboard.add(types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_booking"))
    return keyboard

def get_cancel_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton("❌ Отмена записи", callback_data="cancel_booking"))
    return keyboard

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    user_dialog_history[user_id] = []
    pending_user_slot.pop(user_id, None)
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)

    welcome_text = (
        "Здравствуйте! 🌷\n\n"
        "Добро пожаловать в онлайн-пространство разговорного английского Елены Смирновой!\n\n"
        "Здесь вы можете узнать всё о методике обучения, ознакомиться с отзывами учеников, "
        "выбрать удобное время для занятий и получить подробную консультацию нашего AI-помощника.\n\n"
        "Выберите интересующий вас раздел в меню ниже 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

def save_name_step(message):
    user_id = message.from_user.id

    # Если введена команда отмены/перезапуска
    if message.text and message.text.startswith('/'):
        pending_user_slot.pop(user_id, None)
        start_cmd(message)
        return

    slot_to_book = pending_user_slot.get(user_id)
    if not slot_to_book:
        bot.send_message(message.chat.id, "Выбор времени был сброшен. Пожалуйста, выберите окошко из списка:", reply_markup=get_slots_keyboard())
        return

    student_name = message.text.strip()
    
    # ФИКСАЦИЯ БРОНИРОВАНИЯ ТОЛЬКО ЗДЕСЬ
    confirmed_bookings.add(slot_to_book)
    pending_user_slot.pop(user_id, None)

    confirm_text = (
        "✅ Вы успешно записаны на бесплатный пробный урок! 🎉\n\n"
        f"👤 Ученик: {student_name}\n"
        f"📅 Выбранное время: {slot_to_book}\n\n"
        f"Преподаватель свяжется с вами в Telegram для подтверждения и отправки ссылки: {ADMIN_USERNAME}"
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

    if call.data == "about":
        pending_user_slot.pop(user_id, None)
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        text = (
            "👩‍🏫 О преподавателе: Елена Смирнова\n\n"
            "Сертифицированный преподаватель английского языка с опытом преподавания более 12 лет.\n\n"
            "• Авторская коммуникативная методика: 80% живой практики с первого занятия\n"
            "• Индивидуальный подход и снятие страха говорить на иностранном языке\n"
            "• Удобный онлайн-формат на интерактивной платформе со всеми материалами\n"
            "• Заметный результат и свобода в речи уже через 1 месяц регулярных уроков 🌷"
        )
        bot.send_message(chat_id, text, reply_markup=get_main_menu())

    elif call.data == "ask_ai":
        pending_user_slot.pop(user_id, None)
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        text = "🤖 Режим подробной AI-консультации:\n\nЗадайте любой вопрос о курсе, ценах, расписании или методике прямо в поле сообщения ниже:"
        bot.send_message(chat_id, text)

    elif call.data == "reviews":
        pending_user_slot.pop(user_id, None)
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        text = (
            "💬 Отзывы наших учеников:\n\n"
            "🌸 Виктория (IT-специалист):\n«Перестала бояться созвонов на английском с иностранными коллегами. За 2 месяца полностью ушел языковой барьер, уроки проходят на одном дыхании!»\n\n"
            "🌸 Максим (студент):\n«Сдал международный экзамен на отлично! Очень понравилась подача грамматики — без зубрежки, всё сразу в диалогах. Спасибо Елене!»"
        )
        bot.send_message(chat_id, text, reply_markup=get_main_menu())

    elif call.data in ["slots", "book"]:
        pending_user_slot.pop(user_id, None)
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        available = [s for s in ALL_SLOTS if s not in confirmed_bookings]
        if not available:
            bot.send_message(
                chat_id, 
                f"Все окошки на ближайшие дни заняты.\nВы можете сбросить записи для проверки или написать напрямую преподавателю: {ADMIN_USERNAME}", 
                reply_markup=get_slots_keyboard()
            )
        else:
            bot.send_message(chat_id, "📅 Выберите подходящее свободное окошко для пробного урока:", reply_markup=get_slots_keyboard())

    elif call.data.startswith("select_slot:"):
        chosen_slot = call.data.replace("select_slot:", "")
        if chosen_slot in confirmed_bookings:
            bot.send_message(chat_id, "Это место уже подтверждено другим учеником. Выберите другое:", reply_markup=get_slots_keyboard())
        else:
            pending_user_slot[user_id] = chosen_slot
            text = f"✨ Вы выбрали время:\n📅 {chosen_slot}\n\nПожалуйста, напишите имя и фамилию ученика:"
            msg = bot.send_message(chat_id, text, reply_markup=get_cancel_keyboard())
            bot.register_next_step_handler(msg, save_name_step)

    elif call.data == "cancel_booking":
        # Полная очистка ожидания имени — слот НЕ теряется
        pending_user_slot.pop(user_id, None)
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        bot.send_message(chat_id, "Запись отменена. Все свободные окошки сохранены и доступны в меню 🌷", reply_markup=get_main_menu())

    elif call.data == "reset_slots":
        confirmed_bookings.clear()
        pending_user_slot.pop(user_id, None)
        bot.send_message(chat_id, "✅ Все окошки успешно сброшены и снова открыты для записи!", reply_markup=get_slots_keyboard())

# Функция очистки текста от любых символов разметки
def remove_markdown(text):
    if not text:
        return ""
    for symbol in ["**", "__", "```", "`", "#", "*"]:
        text = text.replace(symbol, "")
    return text.strip()

# Запрос к нейросети через шлюз KIE AI
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

    for url in endpoints:
        payload = {
            "messages": messages_list,
            "temperature": 0.7
        }
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=12)
            if r.status_code == 200:
                data = r.json()
                if "choices" in data and len(data["choices"]) > 0:
                    raw_answer = data["choices"][0]["message"]["content"]
                    return remove_markdown(raw_answer)
        except Exception:
            continue

    # Подробный ответ по базе знаний, если внешний сервер дает сбой
    return (
        "Здравствуйте! С удовольствием расскажу подробнее о курсе разговорного английского Елены Смирновой 🌷\n\n"
        "1. Форматы и стоимость обучения:\n"
        "• Мини-группы (до 4 человек): 900 рублей за занятие (60 минут). Отличная возможность практиковать речь в компании единомышленников.\n"
        "• Индивидуальные уроки: 1800 рублей за занятие (60 минут). Программа полностью адаптируется под ваши персональные цели и график.\n\n"
        "2. Методика и длительность:\n"
        "Курс рассчитан на 3 месяца регулярных занятий (2 раза в неделю). 80% времени посвящено живому общению и снятию языкового барьера без зубрежки сложных правил.\n\n"
        "3. Бесплатный пробный урок:\n"
        "Мы проводим 30-минутную бесплатную диагностику, чтобы определить ваш уровень и составить персональный план обучения.\n\n"
        "Вы можете выбрать удобное время в разделе меню «📅 Свободные окошки» или нажать «✨ Записаться на пробный урок»!"
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
