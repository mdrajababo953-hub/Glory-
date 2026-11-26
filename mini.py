# ═══════════════════════════════════════════════════════════════
#  ARIYAN SUITE — BD Register + Auto Guild Join
#  Flow: [1] 4 IDs  [2] 8 IDs → Guild ID → Auto Register → Auto Join → JSON
# ═══════════════════════════════════════════════════════════════

import hmac, hashlib, requests, string, random, json, os, sys, base64, re, uuid, time
import asyncio, threading
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3
urllib3.disable_warnings()

try:
    import aiohttp
except ImportError:
    import subprocess, importlib.util
    if importlib.util.find_spec("aiohttp") is None:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "aiohttp"])
    import aiohttp

# ═══════════════════════════════════════════════════════════════
#  🎨 UI
# ═══════════════════════════════════════════════════════════════
class C:
    R="\033[0m"; B="\033[1m"; DIM="\033[2m"
    RED="\033[91m"; GRN="\033[92m"; YLW="\033[93m"
    BLU="\033[94m"; MAG="\033[95m"; CYN="\033[96m"; WHT="\033[97m"
    GOLD="\033[38;5;220m"; PINK="\033[38;5;201m"; AQUA="\033[38;5;51m"
    LIME="\033[38;5;82m"; ORANGE="\033[38;5;208m"; PURPLE="\033[38;5;135m"

def clear():
    os.system('clear' if os.name=='posix' else 'cls')

def banner():
    print(f"""{C.PINK}{C.B}
  ╔═══════════════════════════════════════════════════════════╗
  ║   ░█████╗░██████╗░██╗██╗░░░██╗░█████╗░███╗░░██╗          ║
  ║   ██╔══██╗██╔══██╗██║╚██╗░██╔╝██╔══██╗████╗░██║          ║
  ║   ███████║██████╔╝██║░╚████╔╝░███████║██╔██╗██║          ║
  ║   ██╔══██║██╔══██╗██║░░╚██╔╝░░██╔══██║██║╚████║          ║
  ║   ██║░░██║██║░░██║██║░░░██║░░░██║░░██║██║░╚███║          ║
  ║   ╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚══╝          ║
  ╠═══════════════════════════════════════════════════════════╣
  ║  {C.AQUA}🇧🇩 BANGLADESH SERVER{C.PINK}  │  {C.LIME}REGISTER + AUTO GUILD JOIN{C.PINK}    ║
  ╚═══════════════════════════════════════════════════════════╝{C.R}
""")

def box(title, lines, color=C.AQUA, width=62):
    print(f"{color}╔{'═'*(width-2)}╗{C.R}")
    print(f"{color}║{C.R} {C.B}{C.WHT}{title:<{width-4}}{C.R} {color}║{C.R}")
    print(f"{color}╠{'═'*(width-2)}╣{C.R}")
    for ln in lines:
        clean = re.sub(r'\033\[[0-9;]*m', '', ln)
        pd = max(0, width - 4 - len(clean))
        print(f"{color}║{C.R} {ln}{' '*pd} {color}║{C.R}")
    print(f"{color}╚{'═'*(width-2)}╝{C.R}")

def ok(m):   print(f"  {C.LIME}✔{C.R} {m}", flush=True)
def err(m):  print(f"  {C.RED}✘{C.R} {m}", flush=True)
def warn(m): print(f"  {C.YLW}⚠{C.R} {m}", flush=True)
def info(m): print(f"  {C.CYN}ℹ{C.R} {m}", flush=True)
def ask(p, d=""):
    try:
        v = input(f"  {C.GRN}╰─▶{C.R} {p}").strip()
        return v if v else d
    except EOFError:
        return d

def progress_bar(current, total, prefix="", width=30):
    pct = current / total if total else 0
    filled = int(width * pct)
    bar = "█" * filled + "░" * (width - filled)
    color = C.LIME if pct == 1 else C.AQUA
    print(f"\r  {prefix} {color}{bar}{C.R} {C.WHT}{current}/{total}{C.R}", end="", flush=True)

def typing(msg, delay=0.015, color=C.AQUA):
    for ch in msg:
        print(f"{color}{ch}{C.R}", end="", flush=True)
        time.sleep(delay)
    print()

# ═══════════════════════════════════════════════════════════════
#  BD LOCKED CONSTANTS
# ═══════════════════════════════════════════════════════════════
BANGLADESH_REGION       = "BD"
BANGLADESH_LANG         = "bn"
BANGLADESH_COUNTRY_CODE = "BD"
BANGLADESH_CARRIER      = "Grameenphone"

_SUP = {'0':'\u2070','1':'\u00B9','2':'\u00B2','3':'\u00B3',
        '4':'\u2074','5':'\u2075','6':'\u2076','7':'\u2077',
        '8':'\u2078','9':'\u2079'}
_ARIYAN_STYLIZED = "Aʀɪʏᴀɴ"
PASSWORD_PREFIX  = "FOUK_BY_ARIYAN_"

def _make_ariyan_name():
    d = ''.join(random.choice(string.digits) for _ in range(6))
    return _ARIYAN_STYLIZED + ''.join(_SUP[c] for c in d)

def generate_password():
    s = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
    return f"{PASSWORD_PREFIX}{s}"

# ═══════════════════════════════════════════════════════════════
#  CRYPTO + PROTO
# ═══════════════════════════════════════════════════════════════
def gen_signature(payload):
    return hmac.new(
        b"2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        payload.encode(), hashlib.sha256
    ).hexdigest()

def encrypt_payload(plain_hex):
    key = bytes([89,103,38,116,99,37,68,69,117,104,54,37,90,99,94,56])
    iv  = bytes([54,111,121,90,68,114,50,50,69,51,121,99,104,106,77,37])
    return AES.new(key, AES.MODE_CBC, iv).encrypt(pad(bytes.fromhex(plain_hex), AES.block_size)).hex()

def encode_varint(n):
    if n < 0: return b''
    out = bytearray()
    while True:
        b = n & 0x7F; n >>= 7
        if n: b |= 0x80
        out.append(b)
        if not n: break
    return bytes(out)

def create_field(fn, v):
    if isinstance(v, int):
        return encode_varint((fn << 3) | 0) + encode_varint(v)
    if isinstance(v, (str, bytes)):
        ev = v.encode() if isinstance(v, str) else v
        return encode_varint((fn << 3) | 2) + encode_varint(len(ev)) + ev
    return b''

def build_proto(d):
    return b''.join(create_field(k, v) for k, v in d.items())

_XOR_KEYSTREAM = bytes([
    0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,0x37,
    0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30,
])
def build_field_14(open_id):
    ob = open_id.encode('utf-8')
    return bytes([ob[i] ^ _XOR_KEYSTREAM[i % 32] for i in range(len(ob))])

FIELD_22 = bytes.fromhex(
    "4747524501010100620200001052aa0d669c6a368f08338060d2ee0690053af84a41edcd3558556ec10f24f4"
    "6c93ac64ca41a16732c46a2cb071246a79b8929032f9e1b6f4ef331bd53cabf29b09b97349a46e9863c0314e"
    "1a0d80819fef8aabf03876b3d037db354a7ccb5c1bce96411fb3753f6f50e44c69c4ed617fa30efb8ffc0517"
    "ff2f636739be1f304d999cfd6fd48bf69454199794c3dc88f55a4bdbd66534d5a061359cdfd1fb680cd37918"
    "df9fdb3cf7d80067b0a3506c90063cf62b2ccec11e23913a2fd7c4ef091331967bb518a5ad1e551146b90821"
    "be800883abadde39d6c80a5d798611466c748f075481806c5842ce45e6bd4e3368ec08fe2ec41ceb880cd862"
    "49eb71693f79f0bccf9e590c3fae12519fe08c7a1905d0927690109e0df28574bb14847225db1a59230e6662"
    "ed7730e15ff9a6c815cb41b420edeada735a4b03e181037c37c2c850257311df2f07b0a56e759372cbd0268e"
    "3f13a292ee4373e38ab5096e0342a5e0d7fec6da2bbc265d74baadd2b24ee4f74862f82c21d6694bac53f8ce"
    "80312a30068a6276a641c19b11d0305c6fe2f531ac7de578b29f543697f5c73663e6f23aa15277b6122dcd4d"
    "4171e38f9ac0b173f39c58416a16c5c1f4a35acd065ce78f449cf538a249339e763272d458e4ed86c976591a"
    "9c066b3a37111e44091eb6b5a795249f3e5145db022a6055f2cc675936391312f688f89627845df222a91156"
    "555225be36f9714a0ba50246d0f003bda3c9c1292ab73b4f79635ddd023218eda93a302d79e023404c143965"
    "44a930b98ed54771aca7fec10d095587685b473e81a9619764fad9256529dcd6e911f4f4629612287d4ee3ec"
    "5389f6ec4ec020b0e2aac017232a9197be9e46239ce690fe5d4872b2e98e651510c971667f3aca8b59f3e9d5"
    "0e43"
)

def make_session():
    s = requests.Session(); s.verify = False
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    r = Retry(total=0, connect=0, read=0, redirect=0, status=0,
              backoff_factor=0.0, status_forcelist=[], allowed_methods=None)
    ad = HTTPAdapter(max_retries=r, pool_connections=10, pool_maxsize=20)
    s.mount('https://', ad); s.mount('http://', ad)
    return s

# ═══════════════════════════════════════════════════════════════
#  ENDPOINTS
# ═══════════════════════════════════════════════════════════════
API_BASE    = "https://100067.connect.garena.com"
MAJOR_BASE  = "https://loginbp.ppmainecoonghj.com"
API_HEX_KEY = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
CLAN_JOIN_API = "https://ariyan-join-a9x.vercel.app/join"

BD_DEVICES = ["SM-S918B","SM-S908B","SM-S928B","OnePlus 11","Xiaomi 13 Pro",
              "Pixel 7 Pro","iPhone 15 Pro Max","Nothing Phone 2","iQOO 11"]

REG_HEADERS = {
    "Connection":"Keep-Alive","Accept":"application/json","Accept-Encoding":"gzip",
    "Content-Type":"application/json; charset=utf-8","Host":"100067.connect.garena.com",
}
COOKIE = ("datadome=y23Z3X17pgkMHEt5zY8dqxC6BIf7WJMgC0RXNbqifHT7t9zajKe_hegFb1Ie9_7Jix"
          "Xpz7FRGVodOn~mWPk_NrqIIhUOXDYqKOahzoRQcyEy77GWEMcdA9_MqPJeM5qv")
MAJOR_HEADERS = {
    "User-Agent":"UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
    "Accept-Encoding":"deflate, gzip","X-GA-SV":"1789535859","Authorization":"Bearer",
    "X-GA":"v1 1","ReleaseVersion":"OB55","Content-Type":"application/octet-stream",
    "X-Unity-Version":"2018.4.12f1",
}

def random_ua():
    d = random.choice(BD_DEVICES); av = random.choice(["12","13","14"])
    return f"GarenaMSDK/4.0.44({d} ;Android {av};bn;IND;app 2.127.1 2019118047;)"

def build_major_login(open_id, access_token):
    model = random.choice(BD_DEVICES)
    device_id = f"Google|{uuid.uuid4()}"
    ip = f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    av = random.choice(["12","13","14"]); api = 30 + int(av) - 11
    fields = {
        3: datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        4:"free fire",5:4,7:"1.132.1",8:"2019116753",
        9:f"Android OS {av} / API-{api} (SP1A.210812.016.C2)",
        10:"Handheld",11:model,12:1280,13:720,14:"240",
        15:"x86-64 SSE3 SSE4.1 SSE4.2 AVX AVX2 | 2400 | 4",
        16:random.choice([5951,6000,6100]),17:"Adreno 740",
        18:"OpenGL ES 3.1 v1.46",19:device_id,20:ip,
        21:BANGLADESH_LANG,22:open_id,23:"4",24:"Handheld",25:model,
        26:BANGLADESH_COUNTRY_CODE,29:access_token,30:1,
        41:BANGLADESH_CARRIER,42:"WIFI",
        92:random.choice([19788,20000,21000]),93:"android_max",
        97:1,98:1,99:"4",100:"4",104:77149,105:1,
    }
    p = build_proto(fields)
    try: return bytes.fromhex(encrypt_payload(p.hex()))
    except Exception: return p

# ═══════════════════════════════════════════════════════════════
#  REGISTER ONE ACCOUNT
# ═══════════════════════════════════════════════════════════════
def register_one():
    session = make_session()
    try:
        name = _make_ariyan_name()
        password = generate_password()
        ua = random_ua()

        reg_payload = '{"app_id":100067,"client_type":2,"password":"%s","source":2}' % password
        rh = dict(REG_HEADERS); rh["User-Agent"]=ua; rh["Cookie"]=COOKIE
        rh["Authorization"]=f"Signature {gen_signature(reg_payload)}"
        r = session.post(f"{API_BASE}/api/v2/oauth/guest:register",
                         headers=rh, data=reg_payload, timeout=15, verify=False)
        if r.status_code != 200: return None
        j = r.json()
        if j.get("code") != 0: return None
        uid = j['data']['uid']

        hc = '0123456789abcdef'
        dev_id = ("02-"+"".join(random.choice(hc) for _ in range(8))+"-"+
                  "".join(random.choice(hc) for _ in range(4))+"-"+
                  "".join(random.choice(hc) for _ in range(4))+"-"+
                  "".join(random.choice(hc) for _ in range(4))+"-"+
                  "".join(random.choice(hc) for _ in range(12)))
        tok_payload = ('{"client_id":100067,"client_secret":"%s","client_type":2,'
                       '"device_id":"%s","password":"%s","response_type":"token","uid":%s}'
                       ) % (API_HEX_KEY, dev_id, password, uid)
        th = dict(rh); th["Authorization"]=f"Signature {gen_signature(tok_payload)}"
        r = session.post(f"{API_BASE}/api/v2/oauth/guest/token:grant",
                         headers=th, data=tok_payload, timeout=15, verify=False)
        if r.status_code != 200: return None
        j = r.json()
        if j.get("code") != 0: return None
        access_token = j['data']['access_token']
        open_id = j['data']['open_id']

        proto = build_proto({
            1:name,2:access_token,3:open_id,5:102000007,6:4,7:1,13:1,
            14:build_field_14(open_id),15:BANGLADESH_LANG,16:1,22:FIELD_22,
        })
        enc = bytes.fromhex(encrypt_payload(proto.hex()))
        mh = dict(MAJOR_HEADERS); mh["User-Agent"]=ua
        mh["Authorization"]=f"Bearer {access_token}"
        r = session.post(f"{MAJOR_BASE}/MajorRegister",
                         headers=mh, data=enc, timeout=15, verify=False)
        if r.status_code != 200: return None

        enc_login = build_major_login(open_id, access_token)
        r = session.post(f"{MAJOR_BASE}/MajorLogin",
                         headers=mh, data=enc_login, timeout=15, verify=False)
        if r.status_code != 200: return None
        m = re.search(rb"eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+", r.content)
        if not m: return None
        token = m.group(0).decode('utf-8', errors='ignore')

        try:
            pb = token.split('.')[1]; pad_='='*(4-len(pb)%4)
            dj = json.loads(base64.urlsafe_b64decode(pb+pad_))
            acc_id = dj.get('account_id') or dj.get('external_id') or dj.get('uid')
        except Exception: return None
        if not acc_id: return None

        return {
            "uid": str(uid),
            "password": password,
            "account_id": str(acc_id),
            "name": name,
            "region": BANGLADESH_REGION,
            "server": "BANGLADESH",
            "jwt_token": token,
            "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    except Exception:
        return None
    finally:
        try: session.close()
        except Exception: pass

# ═══════════════════════════════════════════════════════════════
#  GUILD JOIN
# ═══════════════════════════════════════════════════════════════
async def _join_async(uid, password, clan_id):
    for attempt in range(5):
        params = {"uid":str(uid),"pass":str(password),
                  "clan_id":str(clan_id),"region":"BD"}
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(CLAN_JOIN_API, params=params, ssl=False,
                                 timeout=aiohttp.ClientTimeout(total=45)) as r:
                    if r.status != 200: continue
                    d = await r.json(content_type=None)
                    if d.get("success"):
                        nick = (d.get("player") or {}).get("nickname", uid)
                        return True, nick
        except Exception:
            pass
        if attempt < 4:
            await asyncio.sleep(2)
    return False, None

def _join_sync(uid, password, clan_id):
    try:
        loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
        try: return loop.run_until_complete(_join_async(uid, password, clan_id))
        finally: loop.close()
    except Exception:
        return False, None

# ═══════════════════════════════════════════════════════════════
#  SAVE — ONLY accounts.json
# ═══════════════════════════════════════════════════════════════
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNT_JSON_PATH = os.path.join(BASE_DIR, "accounts.json")

def save_json_only(accounts):
    existing = []
    if os.path.exists(ACCOUNT_JSON_PATH):
        try:
            with open(ACCOUNT_JSON_PATH, "r", encoding="utf-8") as f:
                existing = json.load(f) or []
        except Exception:
            existing = []

    have = {str(a.get("uid")) for a in existing if isinstance(a, dict)}
    added = 0
    for a in accounts:
        if a["uid"] in have: continue
        existing.append(a)
        have.add(a["uid"])
        added += 1

    tmp = ACCOUNT_JSON_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)
    os.replace(tmp, ACCOUNT_JSON_PATH)
    return added, len(existing)

# ═══════════════════════════════════════════════════════════════
#  MAIN FLOW
# ═══════════════════════════════════════════════════════════════
def main():
    clear()
    banner()

    # ── Step 1: Select 4 or 8 ──
    print(f"{C.AQUA}  ╔═══════════════════════════════════════════════════════════╗{C.R}")
    print(f"{C.AQUA}  ║{C.R}  {C.B}{C.WHT}SELECT HOW MANY ACCOUNTS TO CREATE{C.R}                     {C.AQUA}║{C.R}")
    print(f"{C.AQUA}  ╠═══════════════════════════════════════════════════════════╣{C.R}")
    print(f"{C.AQUA}  ║{C.R}    {C.LIME}[1]{C.R}  →  Create {C.WHT}4{C.R} Accounts                           {C.AQUA}║{C.R}")
    print(f"{C.AQUA}  ║{C.R}    {C.LIME}[2]{C.R}  →  Create {C.WHT}8{C.R} Accounts                           {C.AQUA}║{C.R}")
    print(f"{C.AQUA}  ╚═══════════════════════════════════════════════════════════╝{C.R}")
    print()
    while True:
        ch = ask(f"{C.WHT}Choose option{C.R} (1/2) : ")
        if ch == "1": total = 4; break
        if ch == "2": total = 8; break
        warn("Invalid option! Choose 1 or 2.")

    # ── Step 2: Ask Guild ID ──
    print()
    print(f"{C.AQUA}  ╔═══════════════════════════════════════════════════════════╗{C.R}")
    print(f"{C.AQUA}  ║{C.R}  {C.B}{C.WHT}ENTER GUILD / CLAN ID{C.R}                                {C.AQUA}║{C.R}")
    print(f"{C.AQUA}  ╚═══════════════════════════════════════════════════════════╝{C.R}")
    print()
    while True:
        clan_id = ask(f"{C.WHT}Guild ID{C.R} (numeric) : ")
        if clan_id.isdigit():
            break
        warn("Guild ID must be numeric!")

    # ── Step 3: Register with animation ──
    clear(); banner()
    box(f"🚀 REGISTERING {total} ACCOUNTS",
        [f"{C.LIME}Region{C.R}   : {C.AQUA}BANGLADESH (BD){C.R}",
         f"{C.LIME}Language{C.R} : {C.AQUA}বাংলা (bn){C.R}",
         f"{C.LIME}Threads{C.R}  : {C.AQUA}2{C.R}",
         f"{C.LIME}Guild ID{C.R} : {C.AQUA}{clan_id}{C.R}",
         f"{C.LIME}Prefix{C.R}   : {C.AQUA}Aʀɪʏᴀɴ⁰⁰⁰⁰⁰⁰{C.R}"], color=C.PINK)
    print()

    accounts = []
    lock = threading.Lock()
    stop = threading.Event()

    def worker(_):
        while not stop.is_set():
            with lock:
                if len(accounts) >= total:
                    stop.set(); return
            acc = register_one()
            if acc:
                with lock:
                    if len(accounts) >= total:
                        stop.set(); return
                    accounts.append(acc)
                    n = len(accounts)
                    print(f"  {C.LIME}✅ [{n}/{total}]{C.R} "
                          f"{C.WHT}{acc['name']}{C.R}  "
                          f"{C.AQUA}UID:{acc['uid']}{C.R}")
            else:
                time.sleep(0.1)

    threads = [threading.Thread(target=worker, args=(i,), daemon=True) for i in range(2)]
    for t in threads: t.start()
    for t in threads: t.join()

    if len(accounts) > total:
        accounts = accounts[:total]

    if not accounts:
        err("No accounts created.")
        return

    print()
    ok(f"Registered {C.WHT}{len(accounts)}{C.R} account(s).")
    time.sleep(0.5)

    # ── Step 4: Auto Join Guild ──
    print()
    box(f"🔗 AUTO JOINING GUILD {clan_id}",
        [f"{C.LIME}Accounts{C.R} : {C.WHT}{len(accounts)}{C.R}",
         f"{C.LIME}Guild ID{C.R} : {C.AQUA}{clan_id}{C.R}",
         f"{C.LIME}Workers{C.R}  : {C.AQUA}{min(len(accounts),10)}{C.R}"],
        color=C.AQUA)
    print()

    start = time.time()
    joined = 0
    with ThreadPoolExecutor(max_workers=min(len(accounts),10)) as ex:
        futures = {ex.submit(_join_sync, a["uid"], a["password"], clan_id): a
                   for a in accounts}
        done = 0
        for fut in as_completed(futures):
            a = futures[fut]; success, nick = fut.result()
            done += 1
            if success:
                joined += 1
                print(f"\n  {C.LIME}✔{C.R} Joined: {C.WHT}{nick}{C.R} ({a['uid']})")
            else:
                print(f"\n  {C.RED}✘{C.R} Failed: {C.WHT}{a['uid']}{C.R}")
            progress_bar(done, len(accounts), prefix=f"{C.CYN}Progress{C.R}")

    print()
    for a in accounts:
        a["clan_id"] = str(clan_id)

    # ── Step 5: Save ONLY accounts.json ──
    added, total_in_json = save_json_only(accounts)

    elapsed = time.time() - start
    print()
    box("📊 FINAL SUMMARY",
        [f"{C.LIME}Accounts Created{C.R}  : {C.WHT}{len(accounts)}{C.R}",
         f"{C.LIME}Guild Joined{C.R}      : {C.LIME}{joined}/{len(accounts)}{C.R}",
         f"{C.LIME}Guild ID{C.R}           : {C.AQUA}{clan_id}{C.R}",
         f"{C.LIME}Added to JSON{C.R}      : {C.LIME}{added}{C.R}",
         f"{C.LIME}Total in JSON{C.R}      : {C.CYN}{total_in_json}{C.R}",
         f"{C.LIME}File Saved{C.R}         : {C.AQUA}accounts.json{C.R}",
         f"{C.LIME}Time Taken{C.R}         : {C.CYN}{elapsed:.1f}s{C.R}"],
        color=C.GRN)
    print()
    typing("  ✨ All done! Only accounts.json has been saved.", 0.015, C.LIME)
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C.RED}[!] Stopped by user.{C.R}\n")
        sys.exit(0)