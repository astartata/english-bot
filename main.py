import telebot
from telebot import types
import requests

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8719479123:AAGUe43dzC-B7F17_yl6_HBJ2KjAgDebqIY"
KIE_API_KEY = "46fe3db9b42642fc131a4311965bf8eb"

ADMIN_USERNAME = "@astartata"

ALLOWED_USERS = [328761045, 7718617445]

bot = telebot.TeleBot(BOT_TOKEN)

ALL_SLOTS = [
    "Пн, 24 августа • 17:00",
    "Ср, 26 августа • 18:30",
    "Сб, 29 августа • 11:00"
]

booked_slots = set()
user_dialog_history = {}
# Надежная замена глючному next_step_handler
user_state = {} 

SYSTEM_PROMPT = (
    "Ты — AI-консультант онлайн-школы разговорного английского Елены Смирновой.\n"
    "Давай подробные и вежливые ответы.\n"
    "1. Преподаватель: Елена Смирнова, опыт более 12 лет.\n"
    "2. Цены: Мини-группа — 900 руб/урок. Индивидуально — 1800 руб/урок.\n"
    "3. Формат: курс 3 месяца, 2 раза в неделю по 60 мин, 80% разговорной практики.\n"
    "4. Пробный урок: бесплатно (30 мин).\n\n"
    "ПРАВИЛО: КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО использовать Markdown (звездочки, решетки, нижние подчеркивания). "
    "Пиши обычным текстом."
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
            
    keyboard.add(types.InlineKeyboardButton("⬅️ Главное меню", callback_data="to_main"))
    return keyboard

def get_cancel_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton("❌ Отмена (вернуться к окошкам)", callback_data="cancel_to_slots"))
    return keyboard

@bot.message_handler(commands=['start'])
def start_cmd(message):
    chat_id = message.chat.id
    user_state.pop(chat_id, None)
    
    text = (
        "Здравствуйте! 🌷 (Система обновлена)\n\n"
        "Добро пожаловать в онлайн-пространство разговорного английского Елены Смирновой!\n\n"
        "Здесь можно узнать о методике, посмотреть свободные окошки и задать вопрос нашему AI-консультанту.\n\n"
        "Выберите раздел в меню ниже 👇"
    )
    bot.send_message(chat_id, text, reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    try:
        bot.answer_callback_query(call.id)
    except:
        pass

    if call.data == "to_main":
        user_state.pop(chat_id, None)
        bot.send_message(chat_id, "Главное меню 👇", reply_markup=get_main_menu())

    elif call.data == "about":
        user_state.pop(chat_id, None)
        text = (
            "👩‍🏫 О преподавателе: Елена Смирнова\n\n"
            "Сертифицированный преподаватель с опытом более 12 лет.\n"
            "• 80% живой практики речи\n"
            "• Быстрое преодоление языкового барьера\n"
            "• Результат уже через 1 месяц занятий 🌷"
        )
        bot.send_message(chat_id, text, reply_markup=get_main_menu())

    elif call.data == "ask_ai":
        user_state.pop(chat_id, None)
        bot.send_message(chat_id, "🤖 Режим AI-консультации:\n\nНапишите любой ваш вопрос прямо в чат:")

    elif call.data == "reviews":
        user_state.pop(chat_id, None)
        text = (
            "💬 Отзывы учеников:\n\n"
            "🌸 Виктория: Перестала бояться созвонов на английском. За 2 месяца ушел языковой барьер!\n\n"
            "🌸 Максим: Сдал экзамен на отлично! Все правила отрабатываются в диалогах."
        )
        bot.send_message(chat_id, text, reply_markup=get_main_menu())

    elif call.data == "slots":
        user_state.pop(chat_id, None)
        bot.send_message(chat_id, "📅 Выберите подходящее свободное окошко:", reply_markup=get_slots_keyboard())

    elif call.data.startswith("pick:"):
        chosen_slot = call.data.split(":", 1)[1]
        if chosen_slot in booked_slots:
            bot.send_message(chat_id, "Это место уже занято! Выберите другое:", reply_markup=get_slots_keyboard())
        else:
            # Запоминаем состояние пользователя без глючных функций Telegram
            user_state[chat_id] = f"booking_{chosen_slot}"
            bot.send_message(chat_id, f"✨ Вы выбрали время: {chosen_slot}\n\nКак зовут ученика? Напишите имя в чат:", reply_markup=get_cancel_keyboard())

    elif call.data == "cancel_to_slots":
        user_state.pop(chat_id, None)
        bot.send_message(chat_id, "Запись отменена. Свободные окошки снова доступны:", reply_markup=get_slots_keyboard())

    elif call.data == "reset_slots":
        booked_slots.clear()
        user_state.pop(chat_id, None)
        bot.send_message(chat_id, "✅ Все записи сброшены! Окошки снова свободны:", reply_markup=get_slots_keyboard())

def remove_markdown(text):
    if not text: return ""
    for s in ["**", "__", "```", "`", "#", "*"]:
        text = text.replace(s, "")
    return text.strip()

def call_ai(messages_list):
    key = KIE_API_KEY.strip()
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    endpoints = [
        "[https://api.kie.ai/gemini-2.5-flash/v1/chat/completions](https://api.kie.ai/gemini-2.5-flash/v1/chat/completions)",
        "[https://api.kie.ai/gpt-4o/v1/chat/completions](https://api.kie.ai/gpt-4o/v1/chat/completions)",
        "[https://api.kie.ai/v1/chat/completions](https://api.kie.ai/v1/chat/completions)"
    ]

    for ep in endpoints:
        try:
            r = requests.post(ep, headers=headers, json={"model": "gpt-3.5-turbo", "messages": messages_list, "temperature": 0.7}, timeout=10)
            if r.status_code == 200:
                return remove_markdown(r.json()["choices"][0]["message"]["content"])
        except:
            continue

    return "Стоимость в мини-группе — 900 руб/урок, индивидуально — 1800 руб/урок. Вы можете записаться на бесплатный урок через меню!"

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    chat_id = message.chat.id
    user_text = message.text

    # Проверяем, находится ли пользователь в состоянии ввода имени
    state = user_state.get(chat_id)
    if state and state.startswith("booking_"):
        slot = state.replace("booking_", "")
        booked_slots.add(slot)
        user_state.pop(chat_id, None) # Сбрасываем состояние
        
        text = f"✅ Вы успешно записаны!\n\n👤 Ученик: {user_text}\n📅 Время: {slot}\n\nПреподаватель свяжется с вами: {ADMIN_USERNAME}"
        bot.send_message(chat_id, text, reply_markup=get_main_menu())
        return

    # Если это не ввод имени, пускаем к ИИ
    if message.from_user.id not in ALLOWED_USERS:
        bot.reply_to(message, "⚠️ Доступ к ИИ открыт только для тестирования.")
        return

    bot.send_chat_action(chat_id, 'typing')
    if chat_id not in user_dialog_history:
        user_dialog_history[chat_id] = []

    user_dialog_history[chat_id].append({"role": "user", "content": user_text})
    if len(user_dialog_history[chat_id]) > 10:
        user_dialog_history[chat_id] = user_dialog_history[chat_id][-10:]

    ai_reply = call_ai([{"role": "system", "content": SYSTEM_PROMPT}] + user_dialog_history[chat_id])
    user_dialog_history[chat_id].append({"role": "assistant", "content": ai_reply})
    bot.reply_to(message, ai_reply, reply_markup=get_main_menu())

if __name__ == "__main__":
    bot.infinity_polling()
