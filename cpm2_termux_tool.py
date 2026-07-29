import requests
import json
import os

# --- CONFIGURATION ---
API_KEY = 'AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ'
BASE_URL = 'https://europe-west1-cpm-2-7cea1.cloudfunctions.net/'

class CPM2Tool:
    def __init__(self):
        self.token = None
        self.local_id = None
        self.headers = {}

    def clear_screen(self):
        os.system('clear')

    def login(self, email, password):
        print(f"[*] Logging in as {email}...")
        url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}'
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        try:
            r = requests.post(url, json=payload)
            if r.status_code == 200:
                data = r.json()
                self.token = data['idToken']
                self.local_id = data['localId']
                self.headers = {"Authorization": f"Bearer {self.token}"}
                print(f"[+] Success! LocalID: {self.local_id}")
                return True
            else:
                print(f"[-] Login Failed: {r.text}")
                return False
        except Exception as e:
            print(f"[-] Error: {e}")
            return False

    def inject_coins(self, amount):
        print(f"[*] Injecting {amount} coins...")
        # Using BuyCoins21_1 from the server list
        url = BASE_URL + "BuyCoins21_1"
        payload = {
            "amount": int(amount),
            "version": "1.1.5",
            "platform": "android"
        }
        r = requests.post(url, json=payload, headers=self.headers)
        print(f"[*] Server Response: {r.text}")

    def inject_car(self, car_id):
        print(f"[*] Injecting Car ID {car_id}...")
        # Using SaveCar23_1 from the server list
        url = BASE_URL + "SaveCar23_1"
        payload = {
            "carId": int(car_id),
            "action": "add",
            "isPremium": True
        }
        r = requests.post(url, json=payload, headers=self.headers)
        print(f"[*] Server Response: {r.text}")

    def inject_money(self, amount):
        print(f"[*] Setting money to {amount}...")
        # Using SaveWalletData23_1 from the server list
        url = BASE_URL + "SaveWalletData23_1"
        payload = {
            "money": int(amount)
        }
        r = requests.post(url, json=payload, headers=self.headers)
        print(f"[*] Server Response: {r.text}")

def main():
    tool = CPM2Tool()
    tool.clear_screen()
    print("====================================")
    print("   CPM 2 POWERFUL TERMUX TOOL v1.0  ")
    print("====================================")
    
    email = input("Enter Email: ")
    password = input("Enter Password: ")
    
    if tool.login(email, password):
        while True:
            print("\n--- MENU ---")
            print("1. Inject Coins")
            print("2. Inject Car by ID")
            print("3. Set Money (50M Max)")
            print("4. Exit")
            
            choice = input("\nSelect option: ")
            
            if choice == '1':
                amt = input("Enter Coins Amount: ")
                tool.inject_coins(amt)
            elif choice == '2':
                cid = input("Enter Car ID: ")
                tool.inject_car(cid)
            elif choice == '3':
                mny = input("Enter Money Amount: ")
                tool.inject_money(mny)
            elif choice == '4':
                print("Goodbye!")
                break
            else:
                print("Invalid choice.")

if __name__ == "__main__":
    main()
