import requests
import json

# --- ВАШИ ДАННЫЕ ИЗ СКРИНШОТОВ ---
TOKEN = "8642555081:AAFCPMuESMEH4QX7Mlbk4L6AhdA2D1_vR8w"
CHAT_ID = "7149867962"
# --------------------------------

print("\033[93m--- ТЕСТ СВЯЗИ С TELEGRAM API ---\033[0m")

try:
    # 1. Проверка самого бота (getMe)
    print("\n1. Проверка токена бота...")
    url_me = f"https://api.telegram.org/bot{TOKEN}/getMe"
    r_me = requests.get(url_me, timeout=10)
    print(f"Статус код: {r_me.status_code}")
    print(f"Ответ сервера: {r_me.text}")
    
    if r_me.status_code == 200:
        bot_info = r_me.json()
        print(f"\033[92m[+] Бот найден: @{bot_info['result']['username']}\033[0m")
    else:
        print("\033[91m[!] Ошибка: Токен неверный или бот не существует.\033[0m")

    # 2. Попытка отправить сообщение
    print(f"\n2. Попытка отправить сообщение на ID {CHAT_ID}...")
    url_send = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": "✅ ТЕСТ СВЯЗИ ПРОЙДЕН! Если вы видите это сообщение, значит всё настроено верно."
    }
    r_send = requests.post(url_send, data=payload, timeout=10)
    print(f"Статус код: {r_send.status_code}")
    print(f"Полный ответ сервера: {r_send.text}")
    
    if r_send.status_code == 200:
        print("\033[92m[+] СООБЩЕНИЕ УСПЕШНО ОТПРАВЛЕНО!\033[0m")
    else:
        print("\033[91m[!] ОШИБКА: Сообщение не отправлено.\033[0m")
        print("\033[93mСовет: Убедитесь, что вы нажали кнопку START в боте.\033[0m")

except requests.exceptions.ConnectionError:
    print("\033[91m[!] ОШИБКА СЕТИ: Не удалось подключиться к серверам Telegram.\033[0m")
    print("\033[93mСовет: Проверьте интернет или попробуйте выключить/включить VPN.\033[0m")
except Exception as e:
    print(f"\033[91m[!] ПРОИЗОШЛА НЕПРЕДВИДЕННАЯ ОШИБКА: {e}\033[0m")

print("\n\033[93m--- КОНЕЦ ТЕСТА ---\033[0m")
