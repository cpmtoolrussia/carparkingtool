import requests
import json
import re
import sqlite3
import time
import struct
import hashlib
import logging
import sys
import random
import string
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

try:
    import brotli
    HAS_BROTLI = True
except ImportError:
    HAS_BROTLI = False

import zlib
import base64

# ═══════════════════════════════════════════
#  ⚙️  CONFIG
# ═══════════════════════════════════════════

FK       = "AIzaSyAe_aOVT1gSfmHKBrorFvX4fRwN5nODXVA"
LOAD_URL = "https://europe-west1-cp-multiplayer.cloudfunctions.net/GetPlayerRecords3"
SAVE_URL = "https://europe-west1-cp-multiplayer.cloudfunctions.net/SavePlayerRecordsPartially8"
RANK_URL = "https://us-central1-cp-multiplayer.cloudfunctions.net/SetUserRating4"

MAX_MONEY = 50_000_000
MAX_COIN  = 500_000

logging.basicConfig(level=logging.ERROR, format="%(message)s")
log = logging.getLogger("CPM")

# ═══════════════════════════════════════════
#  🔐 CRYPTO & UTILS
# ═══════════════════════════════════════════

def make_xor_key(uid: str) -> bytes:
    chars = list(uid)
    if len(chars) >= 9: chars[1], chars[8] = chars[8], chars[1]
    if len(chars) >= 3: chars.pop(2)
    if len(chars) >= 5: chars.append(chars[4])
    return "".join(chars).encode("utf-8")

def xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(data[i] ^ key[i % len(key)] for i in range(len(data)))

def decompress(data: bytes) -> Optional[bytes]:
    if HAS_BROTLI:
        try: return brotli.decompress(data)
        except: pass
    try: return zlib.decompress(data, zlib.MAX_WBITS | 16)
    except: pass
    try: return zlib.decompress(data)
    except: pass
    return None

def decrypt_aes(data: bytes, key: bytes) -> Optional[bytes]:
    if not HAS_CRYPTO: return None
    try:
        cipher = AES.new(key[:16], AES.MODE_CBC, b"\x00" * 16)
        return unpad(cipher.decrypt(data), 16)
    except: return None

def _md5(t): return hashlib.md5(t.encode()).digest()
def _sha1(t): return hashlib.sha1(t.encode()).digest()[:16]

def build_aes_keys(uid, password=None, email=None):
    keys = [_md5("olzhas_carparking")]
    if password: keys += [_md5(password), _sha1(password)]
    if uid:      keys += [_md5(uid), _sha1(uid)]
    if email:    keys.append(_md5(email))
    return keys

class Reader:
    def __init__(self, data):
        self.buf = data; self.pos = 0
    def has_bytes(self, n): return self.pos + n <= len(self.buf)
    def read_byte(self):
        if not self.has_bytes(1): return 0
        v = self.buf[self.pos]; self.pos += 1; return v
    def read_int(self):
        if not self.has_bytes(4): self.pos = len(self.buf); return 0
        v = struct.unpack_from("<i", self.buf, self.pos)[0]; self.pos += 4; return v
    def read_float(self):
        if not self.has_bytes(4): self.pos = len(self.buf); return 0.0
        v = struct.unpack_from("<f", self.buf, self.pos)[0]; self.pos += 4; return v
    def read_string(self):
        marker = self.read_int()
        if marker in (0, -1): return ""
        length = (-marker) - 1 if marker < -1 else marker
        if marker < -1: self.read_int()
        if length > 1_000_000: length = 1_000_000
        if not self.has_bytes(length): return ""
        text = self.buf[self.pos:self.pos + length].decode("utf-8", errors="replace")
        self.pos += length
        return text.replace("\x00", "").strip()
    def read_list(self, item_fn):
        count = self.read_int()
        if count <= 0 or count > 1_000_000: return []
        result = []
        for _ in range(count):
            if self.pos >= len(self.buf): break
            v = item_fn()
            if v is not None: result.append(v)
        return result
    def read_dict(self):
        count = self.read_int()
        if count <= 0 or count > 1_000_000: return {}
        d = {}
        for _ in range(count):
            if self.pos >= len(self.buf): break
            d[self.read_int()] = self.read_int()
        return d
    def read_equipment(self):
        if self.read_byte() == 0: return None
        return {
            "hair": self.read_list(self.read_int),
            "face": self.read_list(self.read_int),
            "beard": self.read_list(self.read_int),
            "cap": self.read_list(self.read_int),
            "mask": self.read_list(self.read_int),
            "top": self.read_list(self.read_int),
            "gloves": self.read_list(self.read_int),
            "bag": self.read_list(self.read_int),
            "pants": self.read_list(self.read_int),
            "shoes": self.read_list(self.read_int),
            "glasses": self.read_list(self.read_int),
            "SelectedEquipments": self.read_list(self.read_int),
            "Gender": self.read_int(),
        }

def parse_player(buf):
    r = Reader(buf)
    if r.read_byte() == 0: return None
    p = {}
    p["Name"] = r.read_string(); p["money"] = r.read_int()
    p["coin"] = r.read_int(); p["localID"] = r.read_string()
    p["boughtFsos"] = r.read_list(r.read_int)
    def read_friend():
        r.read_byte()
        return {"id": r.read_string(), "Name": r.read_string(), "accountID": r.read_string()}
    p["FriendsID"] = r.read_list(read_friend)
    p["LevelsDoneTime"] = r.read_list(r.read_float)
    p["floats"] = r.read_list(r.read_float)
    p["integers"] = r.read_list(r.read_int)
    p["fcar"] = r.read_list(r.read_int)
    p["favouriteWheels"] = r.read_list(r.read_int)
    p["favouriteVinyls"] = r.read_list(r.read_int)
    p["favouriteEmojis"] = r.read_list(r.read_int)
    p["personEquipmentsMale"] = r.read_equipment()
    p["personEquipmentsFemale"] = r.read_equipment()
    if r.read_byte() == 0: p["platesData"] = None
    else:
        def read_vinyl():
            r.read_byte()
            def rv(): return {"x": r.read_float(), "y": r.read_float(), "z": r.read_float()}
            return {"vectors": r.read_list(rv), "v": r.read_list(r.read_string),
                    "floats": r.read_list(r.read_float), "text": r.read_string()}
        def read_plate():
            r.read_byte()
            return {"plateId": r.read_int(), "frontCarId": r.read_int(),
                    "rearCarId": r.read_int(), "vinyls": r.read_list(read_vinyl)}
        p["platesData"] = {"allPlates": r.read_list(read_plate)}
    if r.read_byte() == 0: p["carIDnStatus"] = None
    else:
        p["carIDnStatus"] = {
            "carGeneratedIDs": r.read_list(r.read_string),
            "carStatus": r.read_list(r.read_int),
        }
    p["allData"] = r.read_string()
    p["flags"] = r.read_dict()
    p["animations"] = r.read_list(r.read_int)
    p["emojiPacks"] = r.read_list(r.read_int)
    p["wheels"] = r.read_list(r.read_int)
    p["boughtPoliceLights"] = r.read_list(r.read_int)
    p["boughtPoliceSirens"] = r.read_list(r.read_int)
    return p

def try_parse(buf):
    candidates = [buf]
    d1 = decompress(buf)
    if d1:
        candidates.append(d1)
        d2 = decompress(d1)
        if d2: candidates.append(d2)
    for c in candidates:
        if not c: continue
        if len(c) > 0 and c[0] in (17, 23, 24):
            try:
                p = parse_player(c)
                if p and p.get("Name") is not None: return p
            except: pass
        try:
            clean = c[3:] if (len(c) >= 3 and c[0] == 0xef and c[1] == 0xbb) else c
            if clean[0] == 123: return json.loads(clean.decode("utf-8"))
        except: pass
    return None

def decrypt_player_record(base64_text, uid, password=None, email=None):
    try: buf = base64.b64decode(base64_text)
    except: return {"success": False, "message": "Bad base64"}
    direct = try_parse(buf)
    if direct: return {"success": True, "record": direct}
    if uid:
        try:
            xp = xor_bytes(buf, make_xor_key(uid))
            d  = decompress(xp)
            if d:
                p = try_parse(d)
                if p: return {"success": True, "record": p}
        except: pass
    for key in build_aes_keys(uid or "", password, email):
        plain = decrypt_aes(buf, key)
        if not plain: continue
        p = try_parse(plain)
        if p: return {"success": True, "record": p}
    return {"success": False, "message": "Could not decrypt"}

class Writer:
    def __init__(self): self._p: List[bytes] = []
    def write_byte(self, v): self._p.append(bytes([v & 0xFF]))
    def write_int(self, v):  self._p.append(struct.pack("<i", int(v or 0)))
    def write_float(self, v): self._p.append(struct.pack("<f", float(v or 0.0)))
    def write_string(self, s):
        if s is None: self._p.append(struct.pack("<i", -1)); return
        s = str(s)
        if s == "": self._p.append(struct.pack("<i", 0)); return
        enc = s.encode("utf-8")
        self._p.append(struct.pack("<ii", -(len(enc)) - 1, len(s)) + enc)
    def write_list(self, lst, fn):
        if lst is None: self._p.append(struct.pack("<i", -1)); return
        self._p.append(struct.pack("<i", len(lst)))
        for item in lst: fn(item)
    def write_equipment(self, data):
        if not data: self.write_byte(0); return
        self.write_byte(13)
        for k in ["hair","face","beard","cap","mask","top","gloves","bag","pants","shoes","glasses","SelectedEquipments"]:
            self.write_list(data.get(k, []), self.write_int)
        self.write_int(data.get("Gender", 0))
    def write_plates(self, data):
        if not data: self.write_byte(0); return
        self.write_byte(1)
        plates = data.get("allPlates", [])
        self._p.append(struct.pack("<i", len(plates)))
        for plate in plates:
            self.write_byte(4)
            self.write_int(plate.get("plateId", 0))
            self.write_int(plate.get("frontCarId", 0))
            self.write_int(plate.get("rearCarId", 0))
            vinyls = plate.get("vinyls", [])
            self._p.append(struct.pack("<i", len(vinyls)))
            for vinyl in vinyls:
                self.write_byte(4)
                vecs = vinyl.get("vectors", [])
                self._p.append(struct.pack("<i", len(vecs)))
                for vec in vecs:
                    self._p.append(struct.pack("<fff", vec.get("x",0), vec.get("y",0), vec.get("z",0)))
                self.write_list(vinyl.get("v", []), self.write_string)
                self.write_list(vinyl.get("floats", []), self.write_float)
                self.write_string(vinyl.get("text", ""))
    def write_car_id_status(self, data):
        if not data: self.write_byte(0); return
        self.write_byte(2)
        self.write_list(data.get("carGeneratedIDs", []), self.write_string)
        self.write_list(data.get("carStatus", []), self.write_int)
    def to_bytes(self): return b"".join(self._p)

FIELD_MAPPING = [
    (1,"localID"),(2,"money"),(3,"Name"),(4,"coin"),(5,"allData"),
    (6,"boughtFsos"),(7,"boughtPoliceLights"),(8,"boughtPoliceSirens"),
    (9,"FriendsID"),(10,"LevelsDoneTime"),(11,"floats"),(12,"integers"),
    (13,"fcar"),(14,"favouriteWheels"),(15,"favouriteVinyls"),
    (16,"favouriteEmojis"),(18,"emojiPacks"),
    (41,"personEquipmentsMale"),(42,"personEquipmentsFemale"),
    (43,"platesData"),(44,"carIDnStatus"),(45,"flags"),
    (46,"animations"),(48,"wheels"),
]
INT_LIST_FIELDS   = {6,7,8,12,13,14,15,16,18,46,48}
FLOAT_LIST_FIELDS = {10,11}

def serialize_field(fid, value):
    w = Writer()
    if fid in (1,3,5): w.write_string(value); return w.to_bytes()
    if fid in (2,4): w.write_int(value or 0); return w.to_bytes()
    if fid == 9:
        friends = value or []
        w._p.append(struct.pack("<i", len(friends)))
        for f in friends:
            w.write_byte(3)
            w.write_string((f or {}).get("id",""))
            w.write_string((f or {}).get("Name",""))
            w.write_string((f or {}).get("accountID",""))
        return w.to_bytes()
    if fid in INT_LIST_FIELDS: w.write_list(value or [], w.write_int); return w.to_bytes()
    if fid in FLOAT_LIST_FIELDS: w.write_list(value or [], w.write_float); return w.to_bytes()
    if fid in (41,42): w.write_equipment(value); return w.to_bytes()
    if fid == 43: w.write_plates(value); return w.to_bytes()
    if fid == 44: w.write_car_id_status(value); return w.to_bytes()
    if fid == 45:
        flags = value or {}
        w._p.append(struct.pack("<i", len(flags)))
        for k, v in flags.items():
            w.write_int(int(k)); w.write_int(int(v))
        return w.to_bytes()
    return None

def build_payload(record, uid):
    fields = []
    for fid, key in FIELD_MAPPING:
        value = record.get(key)
        if value is None: continue
        raw = serialize_field(fid, value)
        if raw is not None: fields.append((fid, raw))
    parts = [struct.pack("<i", len(fields))]
    for fid, raw in fields:
        parts.append(struct.pack("<hi", fid, len(raw)))
        parts.append(raw)
    combined   = b"".join(parts)
    compressed = brotli.compress(combined) if HAS_BROTLI else zlib.compress(combined)
    encrypted  = xor_bytes(compressed, make_xor_key(uid))
    return base64.b64encode(encrypted).decode("ascii")

# ═══════════════════════════════════════════
#  🎮 CPM NUKER CORE (SYNCHRONOUS)
# ═══════════════════════════════════════════

GAME_HEADERS = {
    "Accept": "*/*", "Accept-Encoding": "gzip",
    "Content-Type": "application/json",
    "User-Agent": "UnityPlayer/2022.3.62f2 (UnityWebRequest/1.0, libcurl/8.10.1-DEV)",
    "X-Unity-Version": "2022.3.62f2",
}

class CPMNuker:
    def __init__(self):
        self.auth_token = None
        self.email = None
        self.password = None
        self.firebase_uid = None
        self.record = None
        self.session = requests.Session()

    def _post(self, url, payload, headers):
        try:
            r = self.session.post(url, json=payload, headers=headers, timeout=30)
            return r.json()
        except: return None

    def login(self, email, password):
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FK}"
        p = {"email":email,"password":password,"returnSecureToken":True,"clientType":"CLIENT_TYPE_ANDROID"}
        r = self._post(url, p, GAME_HEADERS)
        if r and "idToken" in r:
            self.auth_token = r["idToken"]
            self.email = email
            self.password = password
            self.firebase_uid = r.get("localId","")
            return {"ok":True}
        return {"ok":False, "message": str(r.get("error",{}).get("message","LOGIN_FAILED")) if r else "Network error"}

    def load(self):
        if not self.auth_token: return False
        r = self._post(LOAD_URL,{"data":None},{**GAME_HEADERS,"Authorization":f"Bearer {self.auth_token}"})
        if not r or not r.get("result"): return False
        dec = decrypt_player_record(r["result"], self.firebase_uid, self.password, self.email)
        if dec.get("success"):
            self.record = dec["record"]
            return True
        return False

    def _save(self, data):
        if not self.firebase_uid: return {"ok":False,"message":"NO_UID"}
        payload = build_payload(data, self.firebase_uid)
        r = self._post(SAVE_URL,
            {"data":{"data":payload,"deviceId":self.firebase_uid[:8]}},
            {**GAME_HEADERS,"Authorization":f"Bearer {self.auth_token}","Connection":"Keep-Alive",
             "User-Agent":"Dalvik/2.1.0 (Linux; U; Android 12; Pixel 6 Build/SD1A.210817.036)"})
        if r and (r.get("result") in (1, True, "1") or r.get("ok") or r.get("success")):
            self.record = data
            return {"ok":True}
        return {"ok":False,"message":f"SAVE_FAILED: {str(r)[:100]}"}

    def _modify(self, mods):
        if not self.record: self.load()
        if not self.record: return {"ok":False,"message":"Load failed"}
        d = deepcopy(self.record)
        for k,v in mods.items(): d[k]=v
        return self._save(d)

    def set_money(self, amount): return self._modify({"money": min(amount, MAX_MONEY)})
    def set_coin(self, amount): return self._modify({"coin": min(amount, MAX_COIN)})
    def set_name(self, name): return self._modify({"Name": name})
    def set_id(self, pid): return self._modify({"localID": pid.upper()})

    def unlock_w16(self):
        if not self.record: self.load()
        d = deepcopy(self.record)
        fl = d.get("floats",[])
        while len(fl) <= 32: fl.append(0.0)
        fl[32] = 1.0
        d["floats"] = fl
        return self._save(d)

    def unlock_all(self):
        if not self.record: self.load()
        d = deepcopy(self.record)
        d["money"] = MAX_MONEY
        d["coin"] = MAX_COIN
        d["boughtFsos"] = list(range(100))
        it = d.get("integers",[])
        while len(it) < 120: it.append(0)
        for i in range(120): it[i] = 1
        d["integers"] = it
        return self._save(d)

    def _signup(self, email, password):
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FK}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        r = self._post(url, payload, {"Content-Type": "application/json"})
        if r and r.get("idToken"):
            return {"ok": True, "auth": r["idToken"], "firebase_uid": r.get("localId", "")}
        return {"ok": False, "message": str(r.get("error",{}).get("message","Unknown")) if r else "Network error"}

    def mass_clone(self, domain, count, new_password):
        if not self.record: self.load()
        donor_record = deepcopy(self.record)
        donor_record["localID"] = "CLD_" + donor_record.get("localID", "UNK")[:8]
        created = []
        for i in range(count):
            login = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)) + domain
            pw = new_password if new_password != "random" else ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            res = self._signup(login, pw)
            if res.get("ok"):
                payload = {"data":{"data":build_payload(donor_record, res["firebase_uid"]),"deviceId":res["firebase_uid"][:8]}}
                self._post(SAVE_URL, payload, {**GAME_HEADERS,"Authorization":f"Bearer {res['auth']}"})
                created.append(f"{login}:{pw}")
                print(f"  [{i+1}/{count}] Created: {login}")
        return created

# ═══════════════════════════════════════════
#  🖥️  CLI INTERFACE
# ═══════════════════════════════════════════

def clear(): print("\033[H\033[J", end="")

def main():
    nuker = CPMNuker()
    
    while True:
        clear()
        print("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅")
        print("   🔥 PRIMO CPM TOOL CLI 🔥")
        print("   (Requests Version)      ")
        print("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅")
        
        if not nuker.auth_token:
            print("\n  [1] Login")
            print("  [0] Exit")
            choice = input("\n  Choice: ")
            if choice == "1":
                email = input("  Email: ")
                pw = input("  Password: ")
                print("  Logging in...")
                res = nuker.login(email, pw)
                if res["ok"]:
                    print("  Success! Loading data...")
                    nuker.load()
                else:
                    print(f"  Error: {res['message']}")
                    input("\n  Press Enter...")
            elif choice == "0": break
        else:
            rec = nuker.record or {}
            print(f"\n  👤 {rec.get('Name', 'Unknown')}")
            print(f"  🆔 {rec.get('localID', 'Unknown')}")
            print(f"  💰 ${rec.get('money', 0):,}")
            print(f"  🪙 {rec.get('coin', 0):,}")
            print("\n  [1] Set Money ($50M)")
            print("  [2] Set Coins (500K)")
            print("  [3] Set Name")
            print("  [4] Set ID")
            print("  [5] Unlock W16")
            print("  [6] Unlock Everything")
            print("  [7] 🔥 MASS CLONE")
            print("  [8] Refresh")
            print("  [9] Logout")
            print("  [0] Exit")
            
            choice = input("\n  Choice: ")
            if choice == "1":
                print("  Setting money...")
                nuker.set_money(MAX_MONEY)
            elif choice == "2":
                print("  Setting coins...")
                nuker.set_coin(MAX_COIN)
            elif choice == "3":
                name = input("  New Name: ")
                nuker.set_name(name)
            elif choice == "4":
                pid = input("  New ID: ")
                nuker.set_id(pid)
            elif choice == "5":
                print("  Unlocking W16...")
                nuker.unlock_w16()
            elif choice == "6":
                print("  Unlocking everything...")
                nuker.unlock_all()
            elif choice == "7":
                domain = input("  Domain (e.g. @gmail.com): ")
                try: count = int(input("  Count (max 50): "))
                except: count = 0
                pw = input("  Password (or 'random'): ")
                if count > 0:
                    print(f"  Cloning {count} accounts...")
                    accs = nuker.mass_clone(domain, count, pw)
                    with open("cloned_accounts.txt", "w") as f:
                        f.write("\n".join(accs))
                    print(f"\n  Done! {len(accs)} accounts saved to cloned_accounts.txt")
                input("\n  Press Enter...")
            elif choice == "8":
                print("  Refreshing...")
                nuker.load()
            elif choice == "9":
                nuker = CPMNuker()
            elif choice == "0": break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
