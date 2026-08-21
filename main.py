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
user_state = {} 

SYSTEM_PROMPT = (
    "Ты — главный AI-консультант онлайн-школы разговорного английского Елены Смирновой.\n"
    "Твоя задача — давать ОЧЕНЬ подробные, развернутые и вежливые ответы родителям и ученикам.\n"
    "ДАННЫЕ О КУРСЕ:\n"
    "1. Преподаватель: Елена Смирнова, опыт более 12 лет, международные дипломы.\n"
    "2. Цены: Мини-группа (3-4 человека) — 900 руб/урок. Индивидуально — 1800 руб/урок. Оплата гибкая.\n"
    "3. Формат: курс 3 месяца, 2 раза в неделю по 60 мин, 80% разговорной практики на интерактивной доске.\n"
    "4. Пробный урок: абсолютно бесплатно (30 мин). Это диагностика уровня и подбор программы.\n\n"
    "ПРАВИЛО: КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО использовать Markdown (звездочки, решетки, нижние подчеркивания). "
    "Пиши длинным, чистым текстом, разделяй на абзацы, используй эмодзи. В конце приглашай на пробный урок."
)

FALLBACK_REPLY = (
    "Здравствуйте! Я с удовольствием проконсультирую вас по курсу Елены Смирновой 🌷\n\n"
    "ОБУЧЕНИЕ И МЕТОДИКА:\n"
    "Курс длится 3 месяца (2 раза в неделю по 60 минут). Главный акцент мы делаем на живом общении. "
    "Уже с первого урока мы преодолеваем языковой барьер, разговаривая 80% времени.\n\n"
    "СТОИМОСТЬ И ФОРМАТЫ:\n"
    "• Мини-группы (до 4 человек): 900 руб/урок. Идеально для практики живых диалогов.\n"
    "• Индивидуальные уроки: 1800 руб/урок. Программа адаптируется полностью под ваши цели.\n\n"
    "ПРОБНЫЙ УРОК (БЕСПЛАТНО):\n"
    "Это 30-минутная встреча-диагностика, где мы определим ваш уровень языка и составим план.\n\n"
    "Вы можете выбрать удобное свободное время в меню ниже (кнопка «📅 Свободные окошки»)!"
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
    
    for s in free:
        keyboard.add(types.InlineKeyboardButton(f"🗓 {s}", callback_data=f"pick:{s}"))
            
    keyboard.add(types.InlineKeyboardButton("⬅️ Назад в меню", callback_data="to_main"))
    return keyboard

def get_cancel_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton("❌ Отмена записи", callback_data="cancel_booking"))
    return keyboard

@bot.message_handler(commands=['start'])
def start_cmd(message):
    chat_id = message.chat.id
    user_state.pop(chat_id, None)
    
    text = (
        "Здравствуйте! 🌷 (Версия 5.0)\n\n"
        "Добро пожаловать в онлайн-пространство разговорного английского Елены Смирновой!\n\n"
        "Здесь можно узнать о методике, посмотреть свободные окошки и задать вопрос нашему AI-консультанту.\n\n"
        "Выберите раздел в меню ниже 👇"
    )
    bot.send_message(chat_id, text, reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    try:
        bot.answer_callback_query(call.id)
    except:
        pass

    if call.data == "to_main":
        user_state.pop(chat_id, None)
        try:
            bot.edit_message_text("Главное меню школы 👇", chat_id, msg_id, reply_markup=get_main_menu())
        except:
            bot.send_message(chat_id, "Главное меню школы 👇", reply_markup=get_main_menu())

    elif call.data == "about":
        user_state.pop(chat_id, None)
        text = (
            "👩‍🏫 О преподавателе: Елена Смирнова\n\n"
            "Сертифицированный преподаватель с опытом более 12 лет.\n"
            "• 80% живой практики речи\n"
            "• Быстрое преодоление языкового барьера\n"
            "• Современная интерактивная доска\n"
            "• Результат уже через 1 месяц занятий 🌷"
        )
        try:
            bot.edit_message_text(text, chat_id, msg_id, reply_markup=get_main_menu())
        except:
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
        try:
            bot.edit_message_text(text, chat_id, msg_id, reply_markup=get_main_menu())
        except:
            bot.send_message(chat_id, text, reply_markup=get_main_menu())

    elif call.data == "slots":
        user_state.pop(chat_id, None)
        free = [s for s in ALL_SLOTS if s not in booked_slots]
        text = "📅 Выберите подходящее свободное окошко:" if free else f"Свободных мест на этой неделе больше нет. Напишите преподавателю: {ADMIN_USERNAME}"
        try:
            bot.edit_message_text(text, chat_id, msg_id, reply_markup=get_slots_keyboard() if free else get_main_menu())
        except:
            bot.send_message(chat_id, text, reply_markup=get_slots_keyboard() if free else get_main_menu())

    elif call.data.startswith("pick:"):
        chosen_slot = call.data.split(":", 1)[1]
        if chosen_slot in booked_slots:
            bot.answer_callback_query(call.id, "Место уже занято!", show_alert=True)
            try:
                bot.edit_message_text("📅 Это место уже занято! Выберите другое:", chat_id, msg_id, reply_markup=get_slots_keyboard())
            except:
                pass
        else:
            user_state[chat_id] = f"booking_{chosen_slot}|{msg_id}"
            try:
                bot.edit_message_text(f"✨ Вы выбрали время: {chosen_slot}\n\nКак зовут ученика? Напишите имя прямо в чат:", chat_id, msg_id, reply_markup=get_cancel_keyboard())
            except:
                bot.send_message(chat_id, f"✨ Вы выбрали время: {chosen_slot}\n\nКак зовут ученика? Напишите имя прямо в чат:", reply_markup=get_cancel_keyboard())

    elif call.data == "cancel_booking":
        user_state.pop(chat_id, None)
        text = "Запись отменена. 📅 Вот доступные свободные окошки:"
        try:
            bot.edit_message_text(text, chat_id, msg_id, reply_markup=get_slots_keyboard())
        except:
            bot.send_message(chat_id, text, reply_markup=get_slots_keyboard())


def remove_markdown(text):
    if not text: return ""
    for s in ["**", "*", "__", "_", "```", "`", "#"]:
        text = text.replace(s, "")
    return text.strip()

def call_ai(messages_list):
    key = KIE_API_KEY.strip()
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    
    url = "[https://api.kie.ai/v1/chat/completions](https://api.kie.ai/v1/chat/completions)"
    models = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]

    for model in models:
        try:
            r = requests.post(url, headers=headers, json={"model": model, "messages": messages_list, "temperature": 0.7}, timeout=12)
            if r.status_code == 200:
                return remove_markdown(r.json()["choices"][0]["message"]["content"])
        except:
            continue

    return FALLBACK_REPLY

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    chat_id = message.chat.id
    user_text = message.text

    # Обработка записи имени (если пользователь кликнул на слот)
    state = user_state.get(chat_id)
    if state and state.startswith("booking_"):
        parts = state.split("|")
        slot = parts[0].replace("booking_", "")
        prev_msg_id = int(parts[1]) if len(parts) > 1 else None
        
        booked_slots.add(slot)
        user_state.pop(chat_id, None)
        
        if prev_msg_id:
            try:
                bot.edit_message_text(f"✅ Запись на {slot} оформлена.", chat_id, prev_msg_id)
            except:
                pass
        
        text = f"✅ Вы успешно записаны!\n\n👤 Ученик: {user_text}\n📅 Время: {slot}\n\nПреподаватель свяжется с вами: {ADMIN_USERNAME}"
        bot.send_message(chat_id, text, reply_markup=get_main_menu())
        return

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
