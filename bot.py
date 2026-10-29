import requests
from bs4 import BeautifulSoup
import time

TOKEN = "9222419466:AAF65zfqe89xnHDSMcxpGEV2nabmhPbz0e4"
CHAT_ID = "8242316628"

# Hedef Kriterler ve Güncellenen Fiyat Aralığı
HEDEF_MAHALLELER = ["viranşehir", "menderes", "atatürk", "75. yıl"]
HEDEF_ODALAR = ["2+1", "3+1"]
MINIMUM_FIYAT = 3000000
MAKSIMUM_FIYAT = 5250000

# Sitelerin bot korumalarını aşmak için tarayıcı kimliği
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

def telegram_bildirim_gonder(baslik, fiyat, konum, oda, kaynak, link):
    mesaj = (
        f"🚨 *YENİ MÜLK SAHİBİ İLANI!* 🚨\n\n"
        f"📌 *Başlık:* {baslik}\n"
        f"🏠 *Oda:* {oda}\n"
        f"💰 *Fiyat:* {fiyat:,.0f} TL\n"
        f"📍 *Konum:* {konum}\n"
        f"🌐 *Kaynak:* {kaynak}\n\n"
        f"🔗 [İlana Git ve İncele]({link})"
    )
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mesaj,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        print(f"[{kaynak}] Telegram Yanıt Kodu:", response.status_code)
    except Exception as e:
        print(f"Telegram gönderim hatası: {e}")

def ilanlari_tara():
    print(f"Mersin Mezitli Taraması Başlatıldı (Fiyat Aralığı: {MINIMUM_FIYAT:,} TL - {MAKSIMUM_FIYAT:,} TL)...")
    
    platformlar = [
        ("Sahibinden", "https://www.sahibinden.com/emlak-konut-satilik/mersin-mezitli"),
        ("Hepsiemlak", "https://www.hepsiemlak.com/mersin-mezitli-satilik"),
        ("Emlakjet", "https://www.emlakjet.com/satilik-konut/mersin-mezitli/"),
        ("Emlaksitem", "https://www.emlaksitem.com/ilanlar/mersin-mezitli-satilik-daire")
    ]

    for
