import telebot
from openai import OpenAI

# Вставьте ваши реальные данные в кавычки:
BOT_TOKEN = "8719479123:AAGUe43dzC-B7F17_yl6_HBJ2KjAgDebqIY"
KIE_API_KEY = "30afd64c195a54760f0a706e48790c55"

# Список тех, кому бот отвечает (проверяющий и вы):
ALLOWED_USERS = [328761045, 7718617445]

bot = telebot.TeleBot(BOT_TOKEN)
ai_client = OpenAI(
    api_key=KIE_API_KEY,
    base_url="https://api.kie.ai/v1"
)

user_context = {}

SYSTEM_PROMPT = (
    "Ты — онлайн-консультант курса «Свободный разговорный английский за 3 месяца». "
    "Твоя задача — отвечать на вопросы, помогать преодолеть страх общения и "
    "аккуратно предлагать записаться на бесплатный пробный урок-диагностику. "
    "Отвечай вежливо, кратко и доброжелательно."
)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_context[message.from_user.id] = []
    bot.reply_to(
        message, 
        "Здравствуйте! 👋\nЯ помогу вам узнать всё о курсе «Разговорный английский».\nЗадайте любой вопрос!"
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id

    if user_id not in ALLOWED_USERS:
        bot.reply_to(message, "⚠️ Доступ открыт только для тестирования преподавателем.")
        return

    bot.send_chat_action(message.chat.id, 'typing')

    if user_id not in user_context:
        user_context[user_id] = []

    user_context[user_id].append({"role": "user", "content": message.text})
    
    if len(user_context[user_id]) > 10:
        user_context[user_id] = user_context[user_id][-10:]

    messages_for_ai = [{"role": "system", "content": SYSTEM_PROMPT}] + user_context[user_id]

    try:
        response = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_for_ai,
            max_tokens=500
        )
        bot_reply = response.choices[0].message.content
        user_context[user_id].append({"role": "assistant", "content": bot_reply})
        bot.reply_to(message, bot_reply)
    except Exception as e:
        bot.reply_to(message, f"Ошибка ИИ: {e}")

if __name__ == "__main__":
    bot.infinity_polling()
